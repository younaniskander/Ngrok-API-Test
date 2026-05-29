# Exoskeleton Test Suite & Categorized API Plan

I will merge the original folder structure plan with your new requirement for categorizing angles into three specific ranges.

## Proposed Changes

### exoskeleton_test_suite/ (New Directory)
We will create a new directory to house all files required for the end-to-end testing phase.

#### [NEW] main.py (FastAPI Backend)
I will write a FastAPI script that loads the machine learning pipeline (if requested) but specifically implements logic to return angles in three distinct ranges based on the input data:
1. **Low intensity input -> returns an angle between (0 - 30 degrees)**
2. **Medium intensity input -> returns an angle between (30 - 60 degrees)**
3. **High intensity input -> returns an angle between (60 - 90 degrees)**

The API will expose the `/predict` POST endpoint with CORSMiddleware enabled, so it can be exposed via Ngrok.

#### [NEW] index.html (Frontend Dashboard)
I will copy and isolate your existing frontend dashboard into this folder. It will use async fetch requests to communicate with the `main.py` backend.

#### [NEW] emg_pipeline.pkl
I will copy your existing `best_regressor_model.pkl` to this new folder and rename it to `emg_pipeline.pkl`. (Even if the API categorizes based on input intensity, having the model file satisfies Phase 1 of your documentation).

#### [NEW] emg_exoskeleton_data.csv
I will create a placeholder CSV file to satisfy the dataset requirement in Phase 1.

## User Review Required
> [!IMPORTANT]
> Is it okay if the `main.py` script bypasses the heavy PyCaret ML model to strictly enforce these 3 angle ranges based on input intensity? Or do you want the API to run the ML model first, and then map the ML model's prediction into one of these three ranges? 

## Verification Plan
1. Create the `exoskeleton_test_suite` directory with all 4 files.
2. Run `main.py` using Uvicorn.
3. Use the `index.html` dashboard to send varying intensities of inputs and verify that the API correctly returns angles bounded by the (0-30), (30-60), or (60-90) ranges.
