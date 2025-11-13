#Since the previous route-based sampling data (bus_data_sampled-69.3mb) was too big, we will simplify the sampling process to just randomly select 200,000 rows from the processed dataset for training.(final_training_data.csv ~18.5mb)
import pandas as pd
import os

# Load the processed data
print("Loading processed data...")
df = pd.read_csv('../data/processed_bus_data.csv')

# Simple sampling without groupby complexity
training_df = df.sample(n=200000, random_state=42)

print(f"Original: {len(df):,} rows")
print(f"Final training: {len(training_df):,} rows")
print(f"Routes preserved: {training_df['route_id'].nunique()}")

# Save the final training set
training_df.to_csv('../data/final_training_data.csv', index=False)
print("Final training data saved!")

# Check file size
size_mb = os.path.getsize('../data/final_training_data.csv') / 1024 / 1024
print(f"File size: {size_mb:.1f} MB")