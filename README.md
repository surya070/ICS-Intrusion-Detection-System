# ICS Intrusion Detection System

This project is a **minimal Industrial Control System (ICS) simulation** designed to detect anomalies in Modbus/TCP traffic in real time.
It combines:

* A **CNN-LSTM sequence model** to identify anomalous patterns.
* An **online learner (River Half-Space Trees)** to adapt continuously to new data.

A **Streamlit dashboard** visualizes detection results live and highlights suspicious activity.

---

## Components

* **PLC Server (`plc_server.py`)**
  Hosts a Modbus server and runs the anomaly detection loop. It reads registers, maintains a sliding sequence buffer, and scores each step with both CNN-LSTM and River. Detected anomalies are logged to a CSV file.

* **SCADA Client (`scada_client.py`)**
  Replays rows from `emitting_rows.csv`, encodes direction features, writes them to Modbus registers, and reads them back for verification.

* **Dashboard (`ics_dashboard.py`)**
  Streamlit app plotting model scores over time, marking anomaly windows, and providing buttons to stop PLC and SCADA cleanly.

* **Training Notebook (`CNN-LSTM-Keras.ipynb`)**
  Trains a CNN-LSTM classifier and saves the model (`keras_cnn_lstm_model.h5`) for use by the PLC server.

* **Data Helper (`emit_values.py`)**
  Generates `emitting_rows.csv` by sampling both normal and attack rows.

---

## Workflow

1. SCADA writes features to Modbus registers every \~2s in the order:
   `[length, modbus_func_code, unit_id, iat, transaction_id, direction_Down, direction_Other, direction_Up]`
2. PLC reads the registers, builds a sequence buffer (length = 10), and applies both models.
3. A step is flagged as anomalous if **CNN-LSTM > 0.5** or **River > 3**. Results are logged and displayed on the dashboard.

---

## Running the Project

**Requirements:** Python 3.10–3.11, install packages with `pip install -r requirements.txt`.

**Steps:**

1. Train or provide a `keras_cnn_lstm_model.h5`.
2. Prepare emission data with `emit_values.py` or supply your own CSV.
3. Run in separate terminals:
   * python plc_server.py        # PLC server  
   * python scada_client.py      # SCADA client  
   * streamlit run ics_dashboard.py   # Dashboard  
   
---

## Notes

* Feature order must match on SCADA and PLC.
* CNN-LSTM warms up after 10 steps; initial steps show only River scores.
* Thresholds may be tuned for different datasets.

---
