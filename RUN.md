# Hazard Perception System — Commands Guide

This document lists all the commands needed to set up, run, preprocess, and verify the Autonomous Hazard Perception System.

---

## 1. Running with Docker (Recommended)

Docker Compose manages all three services (Model Inference, Orchestrator API, Frontend Next.js Dashboard) in an isolated container network.

### Start the Platform
Builds all service containers and starts them in the background (detached mode):
```bash
docker compose up -d --build
```
Once started, the services are accessible at:
* **Frontend Dashboard**: `http://localhost:3000`
* **Orchestrator API**: `http://localhost:8000`
* **Model Inference Service**: `http://localhost:8001`

### Stop the Platform
Stops and removes the active container services:
```bash
docker compose down
```

### Tail Service Logs
Watch logs from all running containers in real-time:
```bash
docker compose logs -f
```

---

## 2. Running Locally (Without Docker)

You can run each service directly on your host machine. Use `make` (defined in the `Makefile`) or run the raw shell commands manually.

### Initial Virtual Environment Setup
Creates separate virtual environments (`venv`) for the API and Model services and installs all dependencies:
```bash
# Setup both services at once
make setup

# Or setup individually:
make setup-model
make setup-api
```

### Start Development Servers
Run each command in a separate terminal window:

1. **Start Model Inference Service** (Port `8001`):
   ```bash
   # Using Make:
   make dev-model
   
   # Or manual:
   model\venv\Scripts\uvicorn src.main:app --reload --port 8001 --app-dir model
   ```
2. **Start API Orchestrator Service** (Port `8000`):
   ```bash
   # Using Make:
   make dev-api
   
   # Or manual:
   api\venv\Scripts\uvicorn src.main:app --reload --port 8000 --app-dir api
   ```
3. **Start Frontend Next.js Web Server** (Port `3000`):
   ```bash
   # Using Make:
   make dev-frontend
   
   # Or manual (navigate to directory first):
   cd frontend
   npm run dev
   ```

---

## 3. Dataset Preprocessing & Model Scripts

Run these scripts from the project root using your host machine's Python environment.

### Download Mock Weights
Downloads a pre-trained COCO YOLO model, exports it to native ONNX, and places it at `model/weights/best.onnx` for dashboard validation:
```bash
python scripts/fetch_test_weights.py
```

### Convert BDD100K JSON to YOLO
Converts BDD100K format annotations into normalized `.txt` bounding boxes:
```bash
python scripts/bdd_to_yolo.py --json-path <path_to_bdd_json> --output-dir <path_to_yolo_labels_dir>
```

### Split Dataset
Arranges BDD100K images and converted labels into standard directories for training:
```bash
python scripts/split_dataset.py
```

### Fine-Tune YOLO Model
Launches training on the structured BDD100K dataset with custom hyperparameters and automatic ONNX export:
```bash
python scripts/train_yolo.py
```

---

## 4. Testing & Verification

Run these verification scripts from the project root to ensure system pipeline integrity:

### Verify Upgraded Backend
Validates the native ONNX runtime model loading, image pre/post-processing, and multi-object tracking logic:
```bash
python scripts/verify_upgrade.py
```

### Quick End-to-End Test
Sends a test frame from an uploaded video to the model service and reports raw detections:
```bash
python scripts/e2e_test.py
```

### Multi-Frame Check
Extracts and tests inference at key timestamps (`skip=[50, 150, 300, 500, 700]`) in the uploaded video:
```bash
python scripts/multi_frame_test.py
```

### Hash Check Weights
Compares MD5 checksums of files in `model/weights` and your active training outputs to ensure synchronization:
```bash
python scripts/check_weights.py
```
