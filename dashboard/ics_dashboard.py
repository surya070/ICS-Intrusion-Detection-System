import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import signal
import psutil
import time

LOG_PATH = r"C:\Surya\RVU\mahe-hackathon\dashboard\modbus_data_log.csv"
ST_REFRESH_SEC = 2

def get_proc_pid_by_name(name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if name in ' '.join(proc.info['cmdline']):
                return proc.info['pid']
        except Exception:
            pass
    return None

st.title("ICS Simulation Dashboard")

col1, col2 = st.columns(2)
with col1:
    if st.button("Shutdown PLC Server"):
        pid = get_proc_pid_by_name('plc_server.py')
        if pid:
            os.kill(pid, signal.SIGTERM)
            st.warning("Shutdown signal sent to PLC Server")
        else:
            st.error("PLC Server not running")
with col2:
    if st.button("Shutdown SCADA Client"):
        pid = get_proc_pid_by_name('scada_client.py')
        if pid:
            os.kill(pid, signal.SIGTERM)
            st.warning("Shutdown signal sent to SCADA Client")
        else:
            st.error("SCADA Client not running")

st.subheader("Live Modbus Data and Anomaly Scores")
status_placeholder = st.empty()
graph_placeholder = st.empty()

if not os.path.isfile(LOG_PATH) or os.path.getsize(LOG_PATH) == 0:
    status_placeholder.info("Waiting for data...")
    st.stop()

# Periodically refresh the dashboard
while True:
    try:
        df = pd.read_csv(LOG_PATH)
        expected_cols = {'timestep', 'keras_score', 'river_score', 'anomaly_flag'}
        if not expected_cols.issubset(df.columns):
            status_placeholder.error(f"CSV file missing columns: {expected_cols - set(df.columns)}. Please restart the server.")
            break

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["timestep"], y=df["keras_score"], name="Keras Score", yaxis="y2"))
        fig.add_trace(go.Scatter(x=df["timestep"], y=df["river_score"], name="River Score", yaxis="y2"))

        for i, flag in enumerate(df["anomaly_flag"]):
            if flag:
                fig.add_vline(x=df["timestep"].iloc[i], line_color="red", line_dash="dash")

        fig.update_layout(
            xaxis_title="Time Step",
            yaxis=dict(title="Feature values", side="left", showgrid=False, showticklabels=False),
            yaxis2=dict(
                title="Anomaly Scores",
                overlaying="y",
                side="right",
                range=[0,0.1]
            ),
            legend=dict(orientation="h"),
            shapes=[dict(
                type="rect", xref="x", yref="paper",
                x0=row['timestep']-0.5, x1=row['timestep']+0.5, y0=0, y1=1, fillcolor="red", opacity=0.15, line_width=0
            ) for idx, row in df[df.anomaly_flag == 1].iterrows()]
        )
        # Use a unique key for each update
        graph_placeholder.plotly_chart(fig, use_container_width=True, key=f"main_chart_{len(df)}")

        recent_anomalies = df[df.anomaly_flag == 1]
        if not recent_anomalies.empty:
            status_placeholder.error(f"Recent anomaly at time {recent_anomalies.iloc[-1]['timestep']}")
        else:
            status_placeholder.success("No recent anomalies")
        time.sleep(ST_REFRESH_SEC)
    except Exception as e:
        status_placeholder.error(f"Error reading log or plotting: {str(e)}")
        time.sleep(ST_REFRESH_SEC)
