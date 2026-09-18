"""
Optional Standalone Mock Backend Server for Go API emulation.
Can be started via: python mock_server.py
Serves the exact API contract:
- POST /upload
- POST /record
- POST /predict
- GET  /stream
- GET  /history
- GET  /health
Listens on http://127.0.0.1:8080
"""

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket
from starlette.middleware.cors import CORSMiddleware
import random
import time
import asyncio
from datetime import datetime

app = Starlette()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def health(request):
    return JSONResponse({
        "status": "ok",
        "engine": "Go-ONNX-Daemon-Acoustic-v2.4",
        "version": "2.4.0",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": 3840
    })

async def upload(request):
    form = await request.form()
    filename = "uploaded_audio.wav"
    if "file" in form:
        filename = form["file"].filename

    classes = ["Jackhammer (Construction)", "Siren (Emergency)", "Drilling Machine", "Car Horn"]
    pred_class = random.choice(classes)
    conf = round(random.uniform(0.92, 0.99), 3)
    db = round(random.uniform(84.0, 99.5), 1)

    return JSONResponse({
        "status": "success",
        "class": pred_class,
        "confidence": conf,
        "dB": db,
        "filename": filename,
        "timestamp": datetime.now().isoformat(),
        "probabilities": [
            {"class": pred_class, "confidence": conf},
            {"class": "Drilling Machine", "confidence": round(0.04, 3)},
            {"class": "Engine Idling", "confidence": 0.02},
            {"class": "Ambient", "confidence": 0.01}
        ]
    })

async def record(request):
    try:
        body = await request.json()
        action = body.get("action", "start")
    except Exception:
        action = "start"

    return JSONResponse({
        "status": "recording" if action == "start" else "stopped",
        "session_id": f"sess_go_{int(time.time())}",
        "action": action,
        "started_at": datetime.now().isoformat()
    })

async def predict(request):
    return JSONResponse({
        "class": "Jackhammer (Construction)",
        "confidence": 0.985,
        "dB": 94.2
    })

async def history(request):
    records = [
        {"id": "rec_001", "confidence": 0.99, "category": "Jackhammer (Construction)", "path": "/audio/stream/chunk_01.wav", "db": "96.4 dB", "time": "Aug 14, 11:21 PM", "raw_db": 96.4},
        {"id": "rec_002", "confidence": 0.98, "category": "Siren (Emergency)", "path": "/audio/uploads/emergency.wav", "db": "91.8 dB", "time": "Aug 14, 11:15 PM", "raw_db": 91.8},
        {"id": "rec_003", "confidence": 0.94, "category": "Drilling Machine", "path": "/audio/stream/chunk_02.wav", "db": "88.7 dB", "time": "Aug 14, 11:02 PM", "raw_db": 88.7},
        {"id": "rec_004", "confidence": 0.92, "category": "Car Horn", "path": "/audio/stream/chunk_03.wav", "db": "93.5 dB", "time": "Aug 14, 10:48 PM", "raw_db": 93.5},
        {"id": "rec_005", "confidence": 0.89, "category": "Engine Idling", "path": "/audio/stream/chunk_04.wav", "db": "74.2 dB", "time": "Aug 14, 10:35 PM", "raw_db": 74.2}
    ]
    return JSONResponse(records)

async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            pkt = {
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-4],
                "dB": round(random.uniform(78.0, 96.5), 1),
                "class": random.choice(["Jackhammer (Construction)", "Drilling Machine", "Car Horn"]),
                "confidence": round(random.uniform(0.91, 0.99), 3),
                "frame_id": f"chk_{random.randint(1000, 9999)}"
            }
            await websocket.send_json(pkt)
            await asyncio.sleep(1.0)
    except Exception:
        pass

routes = [
    Route("/health", health, methods=["GET"]),
    Route("/upload", upload, methods=["POST"]),
    Route("/record", record, methods=["POST"]),
    Route("/predict", predict, methods=["POST"]),
    Route("/history", history, methods=["GET"]),
    WebSocketRoute("/stream", websocket_stream),
]

app.router.routes.extend(routes)

if __name__ == "__main__":
    print("Starting Go API Mock Server on http://127.0.0.1:8080 ...")
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
