# API Service

FastAPI backend — orchestrates the video pipeline, risk scoring, and WebSocket streaming.

## Structure

```
api/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── main.py           # FastAPI app entry point
│   ├── routes/
│   │   ├── video.py      # Upload endpoint
│   │   ├── stream.py     # WebSocket endpoint
│   │   └── events.py     # Hazard log query endpoint
│   ├── pipeline/
│   │   ├── processor.py  # Frame-by-frame processing loop
│   │   └── risk_scorer.py# Risk scoring module
│   └── models/
│       └── schemas.py    # Pydantic request/response schemas
└── uploads/              # Uploaded video files (gitignored)
    └── .gitkeep
```

## Development

```bash
cd api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```
