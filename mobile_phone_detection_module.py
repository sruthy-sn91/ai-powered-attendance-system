# mobile_phone_detection_module.py
import cv2
import torch
import numpy as np
from config import YOLOV5_CONF_THRESHOLD, MOBILE_PHONE_CLASS

def load_mobile_net():
    """
    Loads the YOLOv5 model from torch.hub.
    This will automatically download the 'yolov5s' model and its weights.
    """
    # Load the small version of YOLOv5 (yolov5s). For better accuracy, you might choose 'yolov5m' or 'yolov5l'.
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    return model

def detect_mobile_phone(frame, model):
    """
    Uses YOLOv5 to detect mobile phones (cell phones) in the frame.
    Returns a tuple (phone_boxes, annotated_frame) where phone_boxes is a list of bounding boxes.
    """
    # Convert the frame from BGR to RGB (YOLOv5 expects RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Run inference
    results = model(rgb_frame)
    # Get detections as a numpy array. Each row: [x1, y1, x2, y2, confidence, class]
    detections = results.xyxy[0].cpu().numpy()
    phone_boxes = []
    
    # Print debug information for each detection.
    print("[DEBUG] YOLOv5 detections:")
    for detection in detections:
        x1, y1, x2, y2, conf, cls = detection
        label = model.names[int(cls)]
        print(f"  Detected: {label}, Confidence: {conf:.2f}")
        if conf > YOLOV5_CONF_THRESHOLD and label == MOBILE_PHONE_CLASS:
            phone_boxes.append((int(x1), int(y1), int(x2), int(y2)))
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
            cv2.putText(frame, "Mobile Phone", (int(x1), max(int(y1)-10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    if phone_boxes:
        print(f"[DEBUG] Detected mobile phone(s): {phone_boxes}")
    return phone_boxes, frame
