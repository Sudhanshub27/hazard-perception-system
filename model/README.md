# Model Service

This service loads the YOLOv8 ONNX model and exposes a lightweight inference API.

## Structure

```
model/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── main.py           # FastAPI app serving inference
│   └── inference.py      # ONNX Runtime inference wrapper
├── weights/              # .onnx files go here (gitignored)
│   └── .gitkeep
└── configs/
    └── bdd100k.yaml      # Dataset config for training
```

## Development

```bash
cd model
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001
```
