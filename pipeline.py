import numpy as np

class EMGPipeline:
    def __init__(self, original_fs=1000.0, target_fs=1000.0, window_size=200, overlap=0.0):
        self.original_fs = original_fs
        self.target_fs = target_fs
        self.window_size = window_size
        self.overlap = overlap
        self.channel_names = ["RF", "BF", "VM", "ST"]
        
    def _extract_time_features(self, window):
        """Extract MAV, RMS, and WL for each channel in the window."""
        features = {}
        for i, ch_name in enumerate(self.channel_names):
            ch_data = window[:, i]
            features[f"{ch_name}_mav"] = np.mean(np.abs(ch_data))
            features[f"{ch_name}_rms"] = np.sqrt(np.mean(ch_data**2))
            features[f"{ch_name}_wl"] = np.sum(np.abs(np.diff(ch_data)))
        return features

    def process_raw_emg(self, raw_data, return_features=True):
        """
        Process a window of raw EMG data.
        raw_data shape should be (N_samples, 4) where N_samples >= 200.
        """
        feats = self._extract_time_features(raw_data)
        feature_vector = np.array([list(feats.values())])
        return {'features': feature_vector, 'feature_names': list(feats.keys())}
        
    def get_feature_names(self):
        names = []
        for ch in self.channel_names:
            names.extend([f"{ch}_mav", f"{ch}_rms", f"{ch}_wl"])
        return names
