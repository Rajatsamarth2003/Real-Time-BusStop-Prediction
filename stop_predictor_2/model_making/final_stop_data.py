import pandas as pd
import json

print("Creating comprehensive stop database...")

# Load stops.txt with coordinates
stops_df = pd.read_csv('../data/stops.txt')
print(f"Loaded {len(stops_df)} stops with coordinates")

# Load your model stop names
with open('../data/model_stop_names.json', 'r') as f:
    model_stop_names = json.load(f)

print(f"Loaded {len(model_stop_names)} model stop names")

# Create comprehensive stop database
stop_database = {}
for stop_id_str, stop_info in model_stop_names.items():
    stop_id = int(stop_id_str)
    
    # Find this stop in stops.txt
    stop_coords = stops_df[stops_df['stop_id'] == stop_id]
    
    if not stop_coords.empty:
        stop_database[stop_id] = {
            'english': stop_info['english'],
            'hindi': stop_info['hindi'],
            'latitude': float(stop_coords.iloc[0]['stop_lat']),
            'longitude': float(stop_coords.iloc[0]['stop_lon'])
        }
    else:
        print(f"⚠️ Warning: Stop ID {stop_id} not found in stops.txt")

print(f"✅ Created database with {len(stop_database)} stops with coordinates")

# Save the comprehensive database
with open('../data/stop_database.json', 'w', encoding='utf-8') as f:
    json.dump(stop_database, f, indent=2, ensure_ascii=False)

print("✅ Stop database saved as '../data/stop_database.json'")

# Show some samples
print("\n📍 Sample stops with coordinates:")
for stop_id in list(stop_database.keys())[:5]:
    info = stop_database[stop_id]
    print(f"  {stop_id}: {info['english']} - {info['latitude']}, {info['longitude']}")