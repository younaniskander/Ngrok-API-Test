import os
import glob
import numpy as np
import pandas as pd
from pipeline import EMGPipeline
from pycaret.regression import setup, create_model, finalize_model, save_model

def parse_emg_file(filepath):
    """
    Parses a single SEMG_DB1 text file.
    Returns a numpy array of shape (N, 5) where first 4 are EMG, 5th is angle.
    """
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines or lines starting with letters (headers)
            if not line or line.startswith('File Name:') or line.startswith('Channel') or line.isalpha():
                continue
            try:
                # Some files use tabs, some might use spaces
                parts = [float(x) for x in line.split()]
                if len(parts) == 5:
                    data.append(parts)
            except ValueError:
                continue
    return np.array(data)

def generate_dataset():
    pipeline = EMGPipeline()
    window_size = 200
    all_features = []
    all_targets = []
    
    # Process both A_TXT and N_TXT folders
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folders = ['A_TXT', 'N_TXT']
    
    print("Parsing raw text files and extracting features...")
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            continue
            
        txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
        for fpath in txt_files:
            raw_data = parse_emg_file(fpath)
            if raw_data.shape[0] < window_size:
                continue
                
            # Chunk into 200-sample windows
            n_windows = raw_data.shape[0] // window_size
            for i in range(n_windows):
                start_idx = i * window_size
                end_idx = start_idx + window_size
                window = raw_data[start_idx:end_idx, :]
                
                # First 4 cols are EMG
                emg_window = window[:, 0:4]
                # 5th col is Angle
                angle_window = window[:, 4]
                
                # Extract features
                feats = pipeline.process_raw_emg(emg_window)['features'][0]
                target_angle = np.mean(angle_window)
                
                all_features.append(feats)
                all_targets.append(target_angle)
                
    feature_names = pipeline.get_feature_names()
    df = pd.DataFrame(all_features, columns=feature_names)
    df['prediction_label'] = all_targets
    return df

def main():
    print("Step 1: Generating Dataset...")
    df = generate_dataset()
    if df.empty:
        print("ERROR: No data found or parsed. Check your dataset folders.")
        return
        
    csv_path = os.path.join(os.path.dirname(__file__), "emg_exoskeleton_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path} with {len(df)} samples.")
    
    print("Step 2: Training PyCaret Model...")
    # Initialize pycaret
    # Set verbose=False to keep terminal output clean
    s = setup(data=df, target='prediction_label', session_id=123, normalize=True, verbose=False)
    
    # Train a fast Linear Regression model
    print("Training Linear Regression model...")
    lr = create_model('lr', verbose=False)
    final_model = finalize_model(lr)
    
    print("Step 3: Saving Model Pipeline...")
    model_path = os.path.join(os.path.dirname(__file__), "emg_pipeline")
    save_model(final_model, model_path)
    print(f"Model successfully saved to {model_path}.pkl")

if __name__ == "__main__":
    main()
