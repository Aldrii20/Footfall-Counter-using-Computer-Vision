import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = BASE_DIR / "videos"
VIDEO_FILE = BASE_DIR / "People entering and leaving modern building.mp4"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"


VIDEOS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


YOLO_MODEL = "yolov8n.pt"  
DETECTION_CONFIDENCE = 0.45
NMS_THRESHOLD = 0.5


MAX_CENTROID_DISTANCE = 50  
MAX_DISAPPEARED_FRAMES = 40


LINE_POSITION = 0.5  
LINE_THICKNESS = 2
LINE_COLOR = (0, 255, 0)


SHOW_FRAME = True
FRAME_DISPLAY_SIZE = (1280, 720)
FPS_DISPLAY_INTERVAL = 30


OUTPUT_FPS = 30
OUTPUT_CODEC = "mp4v"

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
DEBUG_MODE = True