# config.py
import os

# Path for the SQLite attendance database
DATABASE_PATH = os.path.join(os.getcwd(), "attendance.db")

# Directory where images of known faces are stored.
KNOWN_FACES_DIR = os.path.join(os.getcwd(), "known_faces")

# Tolerance level for face comparison (lower is more strict)
TOLERANCE = 0.6

# Scale factor for frame resizing (adjust for detail)
FRAME_RESIZE_SCALE = 0.75

# --- YOLO Model Configuration for Mobile Phone Detection ---
YOLO_CFG = os.path.join(os.getcwd(), "yolo", "yolov3.cfg")
YOLO_WEIGHTS = os.path.join(os.getcwd(), "yolo", "yolov3.weights")
YOLO_NAMES = os.path.join(os.getcwd(), "yolo", "coco.names")
# In the COCO dataset, the label for mobile phones is "cell phone"
MOBILE_PHONE_CLASS = "cell phone"
# Confidence threshold for YOLO detections (try lowering if needed)
YOLOV5_CONF_THRESHOLD = 0.2
ENABLE_MOBILE_DETECTION = True

