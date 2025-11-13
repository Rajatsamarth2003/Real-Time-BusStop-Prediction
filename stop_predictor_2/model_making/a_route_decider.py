#Identify the routes that have the most data points and create a sampled dataset focusing on those routes.

import pandas as pd

print("Reading full dataset...")
df = pd.read_csv('../data/master_bus_data.csv')  


route_counts = df['route_id'].value_counts()#******
print("Top 15 routes by data points:")
print(route_counts.head(15))

print(f"\nTotal routes: {len(route_counts)}")
print(f"Total data points: {len(df):,}")

# Strategy: Keep top 15 routes that have most data
top_routes = route_counts.head(15).index.tolist()
sample_df = df[df['route_id'].isin(top_routes)]

print(f"\nAfter sampling top 15 routes:")
print(f"Original size: {len(df):,} rows")
print(f"Sampled size: {len(sample_df):,} rows") 
print(f"Data coverage: {(len(sample_df)/len(df)) * 100:.1f}%")

# Save the sampled dataset
sample_df.to_csv('../data/bus_data_sampled.csv', index=False)
print("Sampled dataset saved as '../data/bus_data_sampled.csv'")

# Show memory usage
print(f"\nMemory usage:")
print(f"Original: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
print(f"Sampled: {sample_df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")