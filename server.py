# server.py
import cv2, time, threading, queue, json
from ultralytics import YOLO

results_queue = queue.Queue()

class InferenceServer:
    def __init__(self, model_path="yolov8n.pt", source="sample.mp4", stream_name="stream1"):
        self.model = YOLO(model_path)
        self.source = source
        self.name = stream_name
        self.running = False
        self.count = 0
        self.t = None
        self.start_time = time.time()

    def _run(self):
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            print("Could not open video source:", self.source)
            self.running = False
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            t0 = time.time()
            r = self.model(frame)

            out = {
                "timestamp": time.time(),
                "frame_id": self.count,
                "stream_name": self.name,
                "latency_ms": (time.time() - t0) * 1000,
                "detections": []
            }

            for x in r:
                for b in x.boxes:
                    out["detections"].append({
                        "label": self.model.names[int(b.cls)],
                        "conf": float(b.conf),
                        "bbox": [int(v) for v in b.xyxy[0].tolist()]
                    })

            results_queue.put(out)
            self.count += 1

        cap.release()

    def start(self):
        self.running = True
        self.t = threading.Thread(target=self._run, daemon=True)
        self.t.start()

    def stop(self):
        self.running = False
        if self.t and self.t.is_alive():
            self.t.join()

    def get_metrics(self):
        dt = time.time() - self.start_time
        fps = self.count / dt if dt > 0 else 0
        return {"fps": fps}
