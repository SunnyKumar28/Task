from server import InferenceServer
from client import InferenceClient
import time

video_path = "sample_video.mp4"

server = InferenceServer(source=video_path, stream_name="cam1")
client = InferenceClient("cam1")

server.start()
client.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
finally:
    client.stop()
    server.stop()
    print("Done")
