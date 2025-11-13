#From feature engineered data, create new encoders and train the model afresh.

import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
import time

print("Starting model training with fresh encoders...")

# Load prepared data
df = pd.read_csv('../data/final_training_data.csv')

# Fix prev_stop column
df['prev_stop'] = df['prev_stop'].fillna(0).astype(int)

# Prepare features and target
feature_columns = [
    'latitude', 'longitude', 'route_id', 'speed', 'acceleration', 
    'distance_moved', 'hour', 'is_weekend', 'is_peak_hours', 
    'prev_stop', 'stop_sequence', 'total_stops_in_trip'
]

X = df[feature_columns]
y = df['next_stop_id']

# Create NEW encoders with current data
route_encoder = LabelEncoder()
stop_encoder = LabelEncoder()

X_encoded = X.copy()
X_encoded['route_id'] = route_encoder.fit_transform(X_encoded['route_id'])
X_encoded['prev_stop'] = stop_encoder.fit_transform(X_encoded['prev_stop'].astype(str))
y_encoded = stop_encoder.fit_transform(y)

# Scale numerical features
scaler = StandardScaler()
numerical_cols = ['latitude', 'longitude', 'hour', 'distance_moved', 'speed', 'acceleration', 'stop_sequence', 'total_stops_in_trip']
X_encoded[numerical_cols] = scaler.fit_transform(X_encoded[numerical_cols])

# Save the NEW encoders
with open('route_encoder.pkl', 'wb') as f:
    pickle.dump(route_encoder, f)
with open('stop_encoder.pkl', 'wb') as f:
    pickle.dump(stop_encoder, f)
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print(f"Training samples: {len(X_encoded):,}")
print(f"Number of unique stops: {len(np.unique(y_encoded))}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Build and train model (same as before)
model = tf.keras.Sequential([
    tf.keras.layers.Dense(256, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(len(np.unique(y_encoded)), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

print("\nStarting training...")
history = model.fit(X_train, y_train, epochs=30, batch_size=64, validation_data=(X_test, y_test), verbose=1)

test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"\nFinal Test Accuracy: {test_accuracy:.4f}")

model.save('bus_predictor.h5')
print("Model saved as 'bus_predictor.h5'")