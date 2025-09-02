from pymodbus.client.sync import ModbusTcpClient
import time
import pandas as pd

df = pd.read_csv('emitting_rows.csv')
direction_possible = ['Down', 'Other', 'Up']
direction_categories = [f'direction_{d}' for d in direction_possible]

direction_encoded = pd.get_dummies(df['direction'], prefix='direction')
for col in direction_categories:
    if col not in direction_encoded.columns:
        direction_encoded[col] = 0
df = pd.concat([df, direction_encoded[direction_categories]], axis=1)

base_features = ['length', 'modbus_func_code', 'unit_id', 'iat', 'transaction_id']
features = base_features + direction_categories

client = ModbusTcpClient('localhost', port=5020)
client.connect()

while True:
    row = df.sample(1).iloc[0]
    values = []
    for feat in features:
        try:
            v = int(float(row[feat])) if not pd.isnull(row[feat]) else 0
        except Exception:
            v = 0
        values.append(v)
    for i, val in enumerate(values):
        client.write_register(i, val)
        print(f"Wrote {features[i]}={val} to register {i}")
    result = client.read_holding_registers(0, len(features))
    if result.isError():
        print("Error reading registers.")
    else:
        print("Read values:", result.registers)
    time.sleep(2)
