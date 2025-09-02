import pandas as pd
import os

def minimal_cover(df, col):
    # For each unique value in col, pick one row with that value
    samples = []
    for val in df[col].dropna().unique():
        row = df[df[col] == val].iloc[[0]]
        samples.append(row)
    return pd.concat(samples)

def make_small(df):
    # For each column, get minimal cover, then drop duplicates
    covered = []
    for col in df.columns:
        try:
            covered.append(minimal_cover(df, col))
        except Exception as e:
            print(f'Error processing column {col}:', e)
    small = pd.concat(covered).drop_duplicates().reset_index(drop=True)
    return small

# --- HAI ---
hai_path = 'data/hai_for_training.csv'
if os.path.exists(hai_path):
    df_hai = pd.read_csv(hai_path, low_memory=False)
    small_hai = make_small(df_hai)
    small_hai.to_csv('data/hai_for_training_small.csv', index=False)
    print('Saved small HAI dataset to data/hai_for_training_small.csv')
else:
    print('HAI dataset not found.')

# --- ICS FLOW ---
ics_path = 'data/icsflow_for_training.csv'
if os.path.exists(ics_path):
    df_ics = pd.read_csv(ics_path, low_memory=False)
    small_ics = make_small(df_ics)
    small_ics.to_csv('data/icsflow_for_training_small.csv', index=False)
    print('Saved small ICS Flow dataset to data/icsflow_for_training_small.csv')
else:
    print('ICS Flow dataset not found.')

# --- MODBUS ---
modbus_path = 'data/modbus_for_training.csv'
if os.path.exists(modbus_path):
    df_modbus = pd.read_csv(modbus_path, low_memory=False)
    small_modbus = make_small(df_modbus)
    small_modbus.to_csv('data/modbus_for_training_small.csv', index=False)
    print('Saved small Modbus dataset to data/modbus_for_training_small.csv')
else:
    print('Modbus dataset not found.') 