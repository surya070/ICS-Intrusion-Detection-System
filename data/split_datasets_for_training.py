import pandas as pd
import glob

# --- HAI DATASET ---
hai_files = glob.glob('data/hai/*.csv')
hai_dfs = []
for f in hai_files:
    try:
        df = pd.read_csv(f, low_memory=False)
        hai_dfs.append(df)
    except Exception as e:
        print(f'Error reading {f}:', e)
if hai_dfs:
    hai_all = pd.concat(hai_dfs, ignore_index=True)
    # Keep only numeric features and the attack labels
    hai_cols = [col for col in hai_all.columns if col.startswith('P') or col.startswith('attack') or col == 'time']
    hai_out = hai_all[hai_cols]
    hai_out.to_csv('data/hai_for_training.csv', index=False)
    print('Saved HAI dataset to data/hai_for_training.csv')
else:
    print('No HAI data found.')

# --- ICS FLOW DATASET ---
ics = pd.read_csv('data/Dataset.csv', low_memory=False)
# Keep all features and the label
ics_cols = [col for col in ics.columns if col != '']
ics_out = ics[ics_cols]
ics_out.to_csv('data/icsflow_for_training.csv', index=False)
print('Saved ICS Flow dataset to data/icsflow_for_training.csv')

# --- MODBUS DATASET ---
modbus_files = glob.glob('data/Modbus Dataset/Modbus Dataset/attack/**/*.csv', recursive=True)
modbus_dfs = []
for f in modbus_files:
    try:
        df = pd.read_csv(f, low_memory=False)
        modbus_dfs.append(df)
    except Exception as e:
        print(f'Error reading {f}:', e)
if modbus_dfs:
    modbus_all = pd.concat(modbus_dfs, ignore_index=True)
    modbus_all.to_csv('data/modbus_for_training.csv', index=False)
    print('Saved Modbus dataset to data/modbus_for_training.csv')
else:
    print('No Modbus data found.') 