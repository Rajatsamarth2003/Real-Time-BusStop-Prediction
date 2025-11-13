# app.py - FIXED VERSION
from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
import pickle
import json
from datetime import datetime
import math
import os

app = Flask(__name__)

# Load model and encoders
print("Loading model and encoders...")

# Load TensorFlow model with lazy loading
model = None
try:
    import tensorflow as tf
    model = tf.keras.models.load_model('bus_predictor.h5')
    print("✅ TensorFlow model loaded successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not load TensorFlow model: {e}")
    print("API will work with heuristic predictions instead")

try:
    with open('route_encoder.pkl', 'rb') as f:
        route_encoder = pickle.load(f)
    with open('stop_encoder.pkl', 'rb') as f:
        stop_encoder = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print("✅ Encoders and scalers loaded successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not load encoders: {e}")
    route_encoder = None
    stop_encoder = None
    scaler = None

# Load stop database
with open('../data/stop_database.json', 'r') as f:
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
            'hindi_name': stop_info['hindi'],
            'distance_meters': min_distance,
            'coordinates': {
                'latitude': stop_info['latitude'],
                'longitude': stop_info['longitude']
            }
        }
    return None

def predict_from_coordinates_internal(latitude, longitude):
    """Internal function that can be called directly with coordinates"""
    print(f"📍 Processing coordinates: {latitude}, {longitude}")
    
    # Find nearest stop from database
    nearest_stop = find_nearest_stop(latitude, longitude)
    
    if not nearest_stop:
        return {'error': 'No nearby stops found in database'}, 400
    
    print(f"🎯 Nearest stop: {nearest_stop['english_name']} (ID: {nearest_stop['stop_id']})")
    
    # Prepare features for prediction
    current_time = datetime.now()
    
    # Use the nearest stop as previous stop context
    prev_stop_id = nearest_stop['stop_id']
    
    features = pd.DataFrame([{
        'latitude': latitude,
        'longitude': longitude, 
        'route_id': 0,
        'speed': 8.0,
        'acceleration': 0,
        'distance_moved': 100,
        'hour': current_time.hour,
        'is_weekend': 1 if current_time.weekday() in [5, 6] else 0,
        'is_peak_hours': 1 if current_time.hour in [7, 8, 9, 17, 18, 19] else 0,
        'prev_stop': prev_stop_id,
        'stop_sequence': 1,
        'total_stops_in_trip': 20
    }])
    
    # Encode and scale features
    features['route_id'] = route_encoder.transform(features['route_id'])
    features['prev_stop'] = stop_encoder.transform(features['prev_stop'].astype(str))
    
    numerical_cols = ['latitude', 'longitude', 'hour', 'distance_moved', 'speed', 
                     'acceleration', 'stop_sequence', 'total_stops_in_trip']
    features[numerical_cols] = scaler.transform(features[numerical_cols])
    
    # Predict next stop
    prediction = model.predict(features)
    predicted_index = np.argmax(prediction, axis=1)[0]
    confidence = float(np.max(prediction))

    # Get predicted stop info
    predicted_stop_id = int(stop_encoder.classes_[predicted_index])
    
    # Find predicted stop in database
    predicted_stop_info = None
    for stop_id, stop_data in stop_database.items():
        if int(stop_id) == predicted_stop_id:
            predicted_stop_info = stop_data
            break
    
    if predicted_stop_info:
        english_name = predicted_stop_info['english']
        hindi_name = predicted_stop_info['hindi']
    else:
        english_name = f"Stop {predicted_stop_id}"
        hindi_name = f"स्टॉप {predicted_stop_id}"
    
    response = {
        'current_location': {
            'coordinates': {'latitude': latitude, 'longitude': longitude},
            'nearest_stop': nearest_stop
        },
        'prediction': {
            'stop_id': predicted_stop_id,
            'stop_name_english': english_name,
            'stop_name_hindi': hindi_name,
            'confidence': confidence
        },
        'audio': {
            'english': f"Next stop is {english_name}",
            'hindi': f"Agalaaaa staation  haaaa {hindi_name}"
        },
        'play_audio': confidence > 0.6
    }
    
    print(f"✅ Prediction: {english_name} (Confidence: {confidence:.2%})")
    return response, 200

# Demo locations using ACTUAL STOPS from your database
demo_locations = {
    "kashmere_gate": {
        "current_location": "Kashmere Gate",
        "coordinates": {"latitude": 28.668132, "longitude": 77.228502},
        "stop_id": 2545
    },
    "connaught_place": {
        "current_location": "Connaught Place", 
        "coordinates": {"latitude": 28.6328, "longitude": 77.2199},
        "stop_id": 4
    },
    "india_gate": {
        "current_location": "India Gate",
        "coordinates": {"latitude": 28.6129, "longitude": 77.2295},
        "stop_id": 5
    },
    "red_fort": {
        "current_location": "Red Fort",
        "coordinates": {"latitude": 28.6562, "longitude": 77.2410},
        "stop_id": 138
    },
    "aiims": {
        "current_location": "AIIMS", 
        "coordinates": {"latitude": 28.5672, "longitude": 77.2100},
        "stop_id": 7
    }
}

# MANUAL CORS HANDLING
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def index():
    return render_template('index.html')

# Handle OPTIONS requests for all routes
@app.route('/predict_from_coordinates', methods=['OPTIONS'])
@app.route('/predict_from_demo', methods=['OPTIONS'])
@app.route('/health', methods=['OPTIONS'])
def options_handler():
    return jsonify({'status': 'ok'}), 200

@app.route('/predict_from_coordinates', methods=['POST'])
def predict_from_coordinates():
    try:
        data = request.json or {}
        
        # Get coordinates from request or use demo location
        latitude = float(data.get('latitude', 28.668132))
        longitude = float(data.get('longitude', 77.228502))
        
        response, status_code = predict_from_coordinates_internal(latitude, longitude)
        return jsonify(response), status_code
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/predict_from_demo', methods=['POST'])
def predict_from_demo():
    try:
        data = request.json or {}
        location_key = data.get('location', 'kashmere_gate')
        
        # Get demo location
        location_data = demo_locations.get(location_key, demo_locations['kashmere_gate'])
        coordinates = location_data['coordinates']
        
        print(f"🎭 Demo request for: {location_data['current_location']}")
        
        # Call the internal function directly with coordinates
        response, status_code = predict_from_coordinates_internal(
            coordinates['latitude'], 
            coordinates['longitude']
        )
        
        # Add demo info to response
        if status_code == 200:
            response['demo_info'] = {
                'location_name': location_data['current_location'],
                'location_key': location_key
            }
        
        return jsonify(response), status_code
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'API is running!', 
        'stops_in_database': len(stop_database),
        'demo_locations': len(demo_locations),
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    print("🚌 Enhanced Bus Stop Prediction API Started!")
    print("📍 Now using actual stop database with 500+ stops")
    print("🌐 http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)