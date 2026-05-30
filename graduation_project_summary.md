# Practical Implementation: Exoskeleton EMG Prediction System

## 1. System Overview
As part of the practical implementation for this graduation project, a complete end-to-end software architecture was developed to bridge the gap between raw biological signals and robotic exoskeleton actuation. The primary objective was to predict the right knee flexo-extension angle using surface Electromyography (sEMG) data collected from four lower-limb muscles: the Rectus Femoris (RF), Biceps Femoris (BF), Vastus Medialis (VM), and Semitendinosus (ST). 

The developed solution encompasses a data preprocessing pipeline, an optimized machine learning model, a high-performance backend API, and a dynamic real-time visualization dashboard.

## 2. Data Processing and Feature Engineering
To translate continuous raw voltage signals into actionable inputs, a custom digital signal processing (DSP) pipeline was implemented. 
* **Windowing:** The raw text-based dataset was algorithmically parsed and segmented into discrete overlapping blocks of 200 samples.
* **Feature Extraction:** For each window, essential time-domain features were extracted across all four channels. These features included Mean Absolute Value (MAV), Root Mean Square (RMS), and Waveform Length (WL), effectively reducing noise while preserving the core characteristics of the muscular activation patterns.

## 3. Machine Learning Integration
Using the PyCaret machine learning library, the extracted features were utilized to train a regression model designed to forecast the continuous knee joint angle. The final model pipeline—handling both feature scaling and regression—was serialized (via `joblib`) to ensure rapid loading times in a production environment. 

To improve the control schema for the exoskeleton actuators, a post-processing algorithm was introduced. The continuous ML predictions are mapped into three discrete, actionable kinematic ranges:
* **0° to 30°** (Low flexion)
* **30° to 60°** (Moderate flexion)
* **60° to 90°** (High flexion)

## 4. Real-Time API Architecture
A robust, asynchronous backend server was constructed using the FastAPI framework. The API serves as the central nervous system of the project, exposing a `/predict` endpoint capable of processing incoming multi-channel EMG arrays in real-time. 
* **Validation:** The endpoint utilizes Pydantic schemas to strictly enforce input data shapes, ensuring system stability.
* **Inference:** Upon receiving a 200-sample raw data array, the server dynamically extracts the necessary features, executes the PyCaret ML pipeline, and returns the categorized angle range with calculated sub-millisecond latency.
* **Connectivity:** Cross-Origin Resource Sharing (CORS) middleware was implemented, allowing the local server to be safely exposed to the public internet via tunneling utilities (e.g., Ngrok) for remote hardware testing.

## 5. Interactive Visualization Dashboard
To validate and demonstrate the system's capabilities, an interactive web dashboard was built using vanilla HTML, CSS, and asynchronous JavaScript. 
The interface features:
* **Virtual Signal Streaming:** Simulates raw muscle activation across the four target muscles, complete with dynamic progress bars.
* **Kinematic Simulation:** A virtual rendering of a human leg that physically rotates in real-time based on the exact predictions returned by the API.
* **Categorical Feedback:** Prominent visual badges that instantly display the current flexion category (0-30, 30-60, 60-90) corresponding to the predicted angle.

This comprehensive software stack successfully demonstrates the feasibility of real-time, non-invasive intent prediction for advanced robotic orthoses.
