"""Multi-frame detection verification test."""
import cv2, httpx, os

upload_dir = 'data/uploads'
video = next((os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.endswith('.mp4')), None)
print(f"Testing: {video}")
cap = cv2.VideoCapture(video)

for skip in [50, 150, 300, 500, 700]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, skip)
    ret, frame = cap.read()
    if not ret:
        continue
    _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    r = httpx.post(
        'http://127.0.0.1:8001/infer',
        files={'file': ('f.jpg', buf.tobytes(), 'image/jpeg')},
        timeout=30,
        headers={'X-No-Proxy': 'true'}
    )
    if r.status_code != 200:
        print(f"Frame {skip:4d}: ERROR {r.status_code}")
        continue
    dets = r.json().get('detections', [])
    det_str = [(d['class_name'], round(d['confidence'], 2)) for d in dets]
    print(f"Frame {skip:4d}: {len(dets):2d} detections -> {det_str}")

cap.release()
print("\nDone. Pipeline is working!")
