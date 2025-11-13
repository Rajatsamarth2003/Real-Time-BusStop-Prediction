import pandas as pd
import json

# Load your stops.txt file
print("Loading stop names from stops.txt...")
try:
    stops_df = pd.read_csv('../data/stops.txt')
    print(f"Found {len(stops_df)} stops in stops.txt")
    
    # Create a proper stop names dictionary
    stop_names = {}
    for _, row in stops_df.iterrows():
        stop_id = int(row['stop_id'])
        stop_name = row['stop_name']
        stop_names[stop_id] = {
            'english': stop_name,
            'hindi': stop_name  # Same name for now
        }
    
    # Save as JSON for the app to use
    with open('../data/stop_names.json', 'w') as f:
        json.dump(stop_names, f, indent=2)
    
    print(f"Stop names saved for {len(stop_names)} stops")
    print("Sample stops:", dict(list(stop_names.items())[:5]))
    
except FileNotFoundError:
    print("❌ stops.txt not found! Please make sure it's in your project folder.")
    print("Available files:")
    import os
    for file in os.listdir('.'):
        if file.endswith('.txt'):
            print(f"  - {file}")