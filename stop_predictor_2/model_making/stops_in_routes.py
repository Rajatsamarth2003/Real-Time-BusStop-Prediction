#Identify all stops that are part of the 15 routes our model is trained on, and save their names.

import pandas as pd
import json

def find_route_stops():
    print("🔍 Finding stops in our 15 trained routes...")
    
    # Load training data
    training_data = pd.read_csv('../data/final_training_data.csv')
    
    # Get unique stops from training data (these are the stops our model knows)
    trained_stop_ids = set(training_data['next_stop_id'].unique())
    print(f"📊 Model was trained on {len(trained_stop_ids)} stops")
    
    # Load all stop names
    with open('../data/stop_names.json', 'r') as f:
        all_stop_names = json.load(f)
    
    print(f"📋 Total stops in database: {len(all_stop_names)}")
    
    # Filter to only stops our model knows
    model_stop_names = {}
    missing_stops = []
    
    for stop_id in trained_stop_ids:
        stop_id_str = str(stop_id)
        if stop_id_str in all_stop_names:
            model_stop_names[stop_id_str] = all_stop_names[stop_id_str]
        else:
            missing_stops.append(stop_id)
    
    print(f"✅ Found names for {len(model_stop_names)}/{len(trained_stop_ids)} trained stops")
    
    if missing_stops:
        print(f"❌ Missing names for {len(missing_stops)} stops: {missing_stops[:10]}...")
    
    # Save the filtered stop names (only stops our model actually knows)
    with open('../data/model_stop_names.json', 'w') as f:
        json.dump(model_stop_names, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved model_stop_names.json with {len(model_stop_names)} stops")
    
    # Show sample
    print("\n🎯 Sample stops our model knows:")
    for stop_id, names in list(model_stop_names.items())[:10]:
        print(f"  Stop {stop_id}: {names['english']}")

if __name__ == '__main__':
    find_route_stops()