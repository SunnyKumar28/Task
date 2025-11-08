# client.py
import time, json, threading, os
from server import results_queue

class InferenceClient:
    def __init__(self, name):
        self.running = False
        self.name = name
        self.t = None
        self.out_dir = f"results_{self.name}"
        os.makedirs(self.out_dir, exist_ok=True)

    def _run(self):
        while self.running:
            try:
                r = results_queue.get(timeout=0.1)
                p = os.path.join(self.out_dir, f"{r['frame_id']}.json")
                with open(p, "w") as f:
                    json.dump(r, f, indent=2)
            except:
                time.sleep(0.01)

    def start(self):
        self.running = True
        self.t = threading.Thread(target=self._run, daemon=True)
        self.t.start()

    def stop(self):
        self.running = False
        if self.t and self.t.is_alive():
            self.t.join()
