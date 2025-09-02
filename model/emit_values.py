import pandas as pd

# Load the CSV file
df = pd.read_csv('modbus_packet_features_dpkt_labeled.csv')

# Fetch 200 rows with label == 0
df0 = df[df['label'] == 0].head(200)

# Fetch 50 rows with label == 1
df1 = df[df['label'] == 1].head(50)

# Combine them (optional)
combined_df = pd.concat([df0, df1], ignore_index=True)

# If you want to save the result to a new CSV file:
combined_df.to_csv('emitting_rows.csv', index=False)

# Or, to work with the DataFrame directly:
print(combined_df)
