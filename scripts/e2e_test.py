"""Quick e2e test: sends one frame to the running Model Service and verifies detections."""
import cv2, httpx, asyncio, os

async def test():
    upload_dir = 'data/uploads'
    video = next((os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.endswith('.mp4')), None)
    if not video:
        print("No video found in data/uploads"); return
    
    cap = cv2.VideoCapture(video)
    # Skip 100 frames (more interesting content mid-video)
    for _ in range(100): cap.read()
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Could not read frame"); return
    
    _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    frame_bytes = buf.tobytes()
    
    async with httpx.AsyncClient(trust_env=False) as client:
        r = await client.post('http://127.0.0.1:8001/infer', files={'file': ('frame.jpg', frame_bytes, 'image/jpeg')}, timeout=30)
        print(f"Status: {r.status_code}")
        data = r.json()
        dets = data.get('detections', [])
        print(f"Detections: {len(dets)}")
        for d in dets[:10]:
            print(f"  ✅ {d['class_name']} conf={d['confidence']:.3f} bbox={[round(v) for v in d['bbox']]}")

asyncio.run(test())
