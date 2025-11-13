#Using the final_training_data.csv, we will create features for model training and prepare the data.

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in meters"""
    R = 6371000  # Earth radius in meters
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def create_features(df):
    print("Creating features for next stop prediction...")
    
    # Sort by route and timestamp to maintain sequence
    df = df.sort_values(['route_id', 'timestamp']).reset_index(drop=True)
    
    # Convert timestamp to datetime features
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_peak_hours'] = df['hour'].isin([7, 8, 9, 17, 18, 19]).astype(int)
    
    # Movement features
    df['lat_diff'] = df.groupby('route_id')['latitude'].diff()
    df['lon_diff'] = df.groupby('route_id')['longitude'].diff()
    df['distance_moved'] = np.sqrt(df['lat_diff']**2 + df['lon_diff']**2) * 111000  # Convert to meters
    
    # Time features
    df['time_diff'] = df.groupby('route_id')['timestamp'].diff()
    
    # Speed (meters per second)
    df['speed'] = df['distance_moved'] / (df['time_diff'] + 1)
    
    # Acceleration
    df['acceleration'] = df.groupby('route_id')['speed'].diff() / (df['time_diff'] + 1)
    
    # Previous stop context (CRITICAL for sequence prediction)
    df['prev_stop'] = df.groupby('route_id')['next_stop_id'].shift(1)
    
    # Journey progress features
    df['stop_sequence'] = df.groupby('route_id').cumcount() + 1
    df['total_stops_in_trip'] = df.groupby('route_id')['next_stop_id'].transform('nunique')
    
    # Fill NaN values
    df = df.fillna(0)
    
    print("Features created successfully!")
    return df

def prepare_model_data(df):
    print("Preparing data for model training...")
    
    # Select features for next stop prediction
    feature_columns = [
        # Current position
        'latitude', 'longitude',
        
        # Route context
        'route_id',
        
        # Movement state
        'speed', 'acceleration', 'distance_moved',
        
        # Time context
        'hour', 'is_weekend', 'is_peak_hours',
        
        # Journey context (most important!)
        'prev_stop', 'stop_sequence', 'total_stops_in_trip'
    ]
    
    X = df[feature_columns]
    y = df['next_stop_id']
    
    # Encode categorical variables
    route_encoder = LabelEncoder()
    stop_encoder = LabelEncoder()
    
    X['route_id'] = route_encoder.fit_transform(X['route_id'])
    X['prev_stop'] = stop_encoder.fit_transform(X['prev_stop'].astype(str))
    y_encoded = stop_encoder.fit_transform(y)
    
    # Scale numerical features
    scaler = StandardScaler()
    numerical_cols = ['latitude', 'longitude', 'hour', 'distance_moved', 'speed', 'acceleration', 'stop_sequence', 'total_stops_in_trip']
    X[numerical_cols] = scaler.fit_transform(X[numerical_cols])
    
    # Save encoders and scaler
    with open('route_encoder.pkl', 'wb') as f:
        pickle.dump(route_encoder, f)
    with open('stop_encoder.pkl', 'wb') as f:
        pickle.dump(stop_encoder, f)
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"Final features shape: {X.shape}")
    print(f"Number of unique stops to predict: {len(np.unique(y_encoded))}")
    print("Encoders and scaler saved!")
    
    return X, y_encoded

# Main execution
if __name__ == "__main__":
    print("Loading sampled data...")
    df = pd.read_csv('../data/bus_data_sampled.csv')
    
    print("Creating features...")
    df_with_features = create_features(df)
    
    print("Preparing for model...")
    X, y = prepare_model_data(df_with_features)
    
    # Save processed data
    df_with_features.to_csv('../data/processed_bus_data.csv', index=False)
    print("Processed data saved as '../data/processed_bus_data.csv'")
    
    print("\nFeature engineering completed! Ready for model training.")