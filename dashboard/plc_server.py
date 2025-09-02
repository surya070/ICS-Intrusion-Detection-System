from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock

import logging
import threading
import time
import numpy as np
from tensorflow.keras.models import load_model
from collections import deque
import csv
import os
import signal
import sys
import pickle

# Paths -- adapt as needed
LOG_PATH = r"C:\Surya\RVU\mahe-hackathon\dashboard\modbus_data_log.csv"
RIVER_MODEL_PATH = r"C:\Surya\RVU\mahe-hackathon\dashboard\river_hst_model.pkl"
KERAS_MODEL_PATH = r"C:\Surya\RVU\mahe-hackathon\model\keras_cnn_lstm_model.h5"

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

SEQ_LEN = 10
direction_categories = ['direction_Down', 'direction_Other', 'direction_Up']
features = ['length', 'modbus_func_code', 'unit_id', 'iat', 'transaction_id'] + direction_categories
keras_model = load_model(KERAS_MODEL_PATH)

def load_river_model(path=RIVER_MODEL_PATH):
    if os.path.isfile(path):
        print(f"Loading saved River model from {path}")
        with open(path, "rb") as f:
            return pickle.load(f)
    else:
        print("No saved River model found. Starting fresh.")
        from river import anomaly
        return anomaly.HalfSpaceTrees(seed=42)

river_model = load_river_model()
seq_buffer = deque(maxlen=SEQ_LEN)

def save_river_model(path=RIVER_MODEL_PATH):
    with open(path, "wb") as f:
        pickle.dump(river_model, f)
    print(f"River model saved to {path}")

def graceful_exit(signum, frame):
    print("Received exit signal, saving River model...")
    save_river_model()
    sys.exit(0)

for s in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(s, graceful_exit)

def log_prediction(timestep, row, keras_score, river_score, anomaly_flag):
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["timestep"] + list(row.keys()) + ["keras_score", "river_score", "anomaly_flag"]
            writer.writerow(header)
        writer.writerow([timestep] + list(row.values()) + [keras_score, river_score, int(anomaly_flag)])

def preprocess_registers(registers):
    row = {}
    for i, feat in enumerate(features):
        row[feat] = registers[i] if i < len(registers) else 0
    return row

def poll_and_predict(context):
    timestep = 0
    while True:
        registers = context.getValues(3, 0, len(features))
        row = preprocess_registers(registers)
        seq_buffer.append([row[f] for f in features])
        if len(seq_buffer) == SEQ_LEN:
            X_seq = np.array(seq_buffer).reshape(1, SEQ_LEN, len(features))
            keras_score = keras_model.predict(X_seq)[0][0]
        else:
            keras_score = None
        river_score = river_model.score_one(row)
        river_model.learn_one(row)
        print(f'Keras model score: {keras_score}, River HST score: {river_score}')
        anomaly_flag = ((keras_score is not None and keras_score > 0.5) or (river_score > 3))
        if anomaly_flag:
            print('Anomaly detected!')
        log_prediction(timestep, row, keras_score, river_score, anomaly_flag)
        timestep += 1
        time.sleep(2)

store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*100),
    co=ModbusSequentialDataBlock(0, [0]*100),
    hr=ModbusSequentialDataBlock(0, [0]*100),
    ir=ModbusSequentialDataBlock(0, [0]*100)
)

context = ModbusServerContext(slaves=store, single=True)
identity = ModbusDeviceIdentification()
identity.VendorName = 'PrototypeICS'
identity.ProductCode = 'PICS'
identity.VendorUrl = 'http://github.com/'
identity.ProductName = 'PythonPLC'
identity.ModelName = 'ModbusServer'
identity.MajorMinorRevision = '1.0'

if __name__ == "__main__":
    try:
        print("Starting Modbus server on localhost:5020...")
        t = threading.Thread(target=poll_and_predict, args=(store,), daemon=True)
        t.start()
        StartTcpServer(context, identity=identity, address=("localhost", 5020))
    except Exception as e:
        log.error(f"Failed to start Modbus server: {e}")
        save_river_model()
