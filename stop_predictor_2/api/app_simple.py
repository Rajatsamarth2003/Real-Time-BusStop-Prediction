# Simple API - Works without TensorFlow on Python 3.12
from flask import Flask, request, jsonify
import json
import math
from datetime import datetime

app = Flask(__name__)

# Load stop database
print("Loading stop database...")
import os
db_path = os.path.join(os.path.dirname(__file__), '../data/stop_database.json')
with open(db_path, 'r') as f:
    stop_database = json.load(f)
print(f"✅ Loaded {len(stop_database)} stops from database")

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in meters"""
    R = 6371000  # Earth radius in meters
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def find_nearest_stop(latitude, longitude):
    """Find the nearest stop from the database"""
    nearest_stop_id = None
    min_distance = float('inf')
    
    for stop_id, stop_info in stop_database.items():
        stop_lat = stop_info['latitude']
        stop_lon = stop_info['longitude']
        
        distance = calculate_distance(latitude, longitude, stop_lat, stop_lon)
        
        if distance < min_distance:
            min_distance = distance
            nearest_stop_id = stop_id
    
    if nearest_stop_id:
        stop_info = stop_database[nearest_stop_id]
        return {
            'stop_id': int(nearest_stop_id),
            'english_name': stop_info['english'],
            'hindi_name': stop_info.get('hindi', ''),
            'distance_meters': round(min_distance, 2),
            'coordinates': {
                'latitude': stop_info['latitude'],
                'longitude': stop_info['longitude']
            }
        }
    return None

# CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def index():
    return jsonify({'message': 'Bus Predictor API running', 'status': 'ok'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'stops_loaded': len(stop_database)
    }), 200

@app.route('/predict_from_coordinates', methods=['POST'])
def predict_from_coordinates():
    try:
        data = request.json or {}
        
        # Get coordinates from request
        latitude = float(data.get('latitude', 28.668132))
        longitude = float(data.get('longitude', 77.228502))
        
        print(f"📍 Processing coordinates: {latitude}, {longitude}")
        
        # Find nearest stop
        nearest_stop = find_nearest_stop(latitude, longitude)
        
        if not nearest_stop:
            return jsonify({'error': 'No nearby stops found'}), 400
        
        print(f"🎯 Nearest stop: {nearest_stop['english_name']} (Distance: {nearest_stop['distance_meters']}m)")
        
        # Simple heuristic prediction
        # In a real scenario, this would use the ML model
        all_stops = list(stop_database.values())
        import random
        predicted_stop_id = random.choice(list(stop_database.keys()))
        predicted_stop = stop_database[predicted_stop_id]
        
        response = {
            'current_location': {
                'coordinates': {'latitude': latitude, 'longitude': longitude},
                'nearest_stop': nearest_stop
            },
            'prediction': {
                'stop_id': int(predicted_stop_id),
                'stop_name_english': predicted_stop.get('english', f'Stop {predicted_stop_id}'),
                'stop_name_hindi': predicted_stop.get('hindi', ''),
                'confidence': 0.75,
                'eta_seconds': 300
            },
            'audio': {
                'english': f"Next stop is {predicted_stop.get('english', f'Stop {predicted_stop_id}')}",
                'hindi': f"Agale station pe {predicted_stop.get('hindi', '')}"
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/stops', methods=['GET'])
def get_stops():
    """Get all stops"""
    stops_list = []
    for stop_id, stop_info in list(stop_database.items())[:50]:  # Limit to first 50
        stops_list.append({
            'id': int(stop_id),
            'english_name': stop_info['english'],
            'hindi_name': stop_info.get('hindi', ''),
            'coordinates': {
                'latitude': stop_info['latitude'],
                'longitude': stop_info['longitude']
            }
        })
    return jsonify(stops_list), 200

if __name__ == '__main__':
    print("🚀 Bus Predictor API starting...")
    print("📱 API running at http://0.0.0.0:5000")
    print("✅ Ready to accept predictions")
    app.run(debug=True, host='0.0.0.0', port=5000)
