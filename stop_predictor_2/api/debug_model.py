import tensorflow as tf
import pickle
import numpy as np
import pandas as pd

print("🔍 Debugging model predictions...")

# Load model and encoders
model = tf.keras.models.load_model('bus_predictor.h5')
with open('route_encoder.pkl', 'rb') as f:
    route_encoder = pickle.load(f)
with open('stop_encoder.pkl', 'rb') as f:
    stop_encoder = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

print(f"Route encoder classes: {route_encoder.classes_}")
print(f"Stop encoder classes: {len(stop_encoder.classes_)} stops")
print(f"First 10 stop IDs: {stop_encoder.classes_[:10]}")

# Test prediction with sample data
sample_data = pd.DataFrame([{
    'latitude': 28.6652, 'longitude': 77.2303,
    'route_id': 0, 'speed': 8.0, 'acceleration': 0,
    'distance_moved': 100, 'hour': 14, 'is_weekend': 0,
    'is_peak_hours': 0, 'prev_stop': 2055,
    'stop_sequence': 5, 'total_stops_in_trip': 20
}])

# Transform
sample_data['route_id'] = route_encoder.transform(sample_data['route_id'])
sample_data['prev_stop'] = stop_encoder.transform(sample_data['prev_stop'].astype(str))

numerical_cols = ['latitude', 'longitude', 'hour', 'distance_moved', 'speed', 
                 'acceleration', 'stop_sequence', 'total_stops_in_trip']
sample_data[numerical_cols] = scaler.transform(sample_data[numerical_cols])

# Predict
prediction = model.predict(sample_data)
predicted_index = np.argmax(prediction, axis=1)[0]
confidence = np.max(prediction)

print(f"Predicted index: {predicted_index}")
print(f"Confidence: {confidence:.4f}")
print(f"Predicted stop ID: {stop_encoder.classes_[predicted_index]}")