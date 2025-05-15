
# main.py
import os
os.environ['OMP_NUM_THREADS'] = '1'

import cv2
import sys
import torch
torch.set_num_threads(1)

from collections import deque
import subprocess
import threading
import time
import uuid

from face_recognition_module import load_known_faces, recognize_faces
from emotion_recognition import detect_emotions
from mobile_phone_detection_module import load_mobile_net, detect_mobile_phone
from database import init_db, mark_attendance
from attendance_utils import draw_labels, draw_emotions  # renamed from utils.py
from config import FRAME_RESIZE_SCALE, ENABLE_MOBILE_DETECTION

# Use gTTS and playsound for TTS alerting.
from gtts import gTTS
from playsound import playsound

# Global alert time gap (in seconds) per recognized face.
ALERT_TIME_GAP = 10  # Adjust as needed.
last_alert_time = {}  # Dictionary to keep track of last alert time per face.

def point_in_box(point, box):
    x, y = point
    top, right, bottom, left = box
    return left <= x <= right and top <= y <= bottom

def smooth_box(new_box, prev_box, alpha=0.3):
    return tuple(int((1 - alpha) * p_prev + alpha * p_new) for p_prev, p_new in zip(prev_box, new_box))

def tts_alert(message):
    """Generates and plays an alert using gTTS and playsound, with a unique filename."""
    try:
        unique_filename = f"alert_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=message, lang='en')
        tts.save(unique_filename)
        print(f"[DEBUG] Playing alert from {unique_filename}")
        playsound(unique_filename)
        time.sleep(1)
    except Exception as e:
        print(f"[ERROR] TTS alert failed: {e}")
    finally:
        if os.path.exists(unique_filename):
            os.remove(unique_filename)

def main():
    init_db()
    known_faces, known_names = load_known_faces()
    print(f"[DEBUG] Loaded {len(known_faces)} known faces.")
    if ENABLE_MOBILE_DETECTION:
        mobile_net = load_mobile_net()
        mobile_net.to('cpu')
        mobile_net.eval()
    else:
        mobile_net = None

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Error: Could not open camera.")
        sys.exit(1)

    previous_face_locations = None
    recent_emotions = deque(maxlen=10)

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("[DEBUG] Failed to grab frame. Exiting...")
                break

            orig_h, orig_w = frame.shape[:2]
            small_frame = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE_SCALE, fy=FRAME_RESIZE_SCALE)
            small_h, small_w = small_frame.shape[:2]

            try:
                face_locations_small, face_names = recognize_faces(small_frame, known_faces, known_names)
            except Exception as e:
                print(f"[ERROR] Exception during face recognition: {e}")
                face_locations_small, face_names = [], []

            scale_y = orig_h / small_h
            scale_x = orig_w / small_w
            current_face_locations = [
                (int(top * scale_y), int(right * scale_x), int(bottom * scale_y), int(left * scale_x))
                for (top, right, bottom, left) in face_locations_small
            ]
            print(f"[DEBUG] Detected face boxes (raw): {current_face_locations}")

            if previous_face_locations is not None and len(previous_face_locations) == len(current_face_locations):
                smoothed_face_locations = [
                    smooth_box(new_box, prev_box) for new_box, prev_box in zip(current_face_locations, previous_face_locations)
                ]
            else:
                smoothed_face_locations = current_face_locations

            previous_face_locations = smoothed_face_locations
            print(f"[DEBUG] Smoothed face boxes: {smoothed_face_locations}")

            for name in face_names:
                if name != "Unknown":
                    mark_attendance(name)

            try:
                raw_emotions = detect_emotions(frame, smoothed_face_locations, margin=0.3)
            except Exception as e:
                print(f"[ERROR] Exception during emotion detection: {e}")
                raw_emotions = [(None, None)] * len(smoothed_face_locations)

            if len(raw_emotions) == 1:
                emotion, score = raw_emotions[0]
                if emotion is not None:
                    from collections import Counter
                    recent_emotions.append(emotion)
                    counter = Counter(recent_emotions)
                    smoothed_emotion = counter.most_common(1)[0][0]
                    raw_emotions[0] = (smoothed_emotion, score)

            frame = draw_labels(frame, smoothed_face_locations, face_names)
            frame = draw_emotions(frame, smoothed_face_locations, raw_emotions)

            if ENABLE_MOBILE_DETECTION and mobile_net is not None:
                try:
                    with torch.no_grad():
                        phone_boxes, frame = detect_mobile_phone(frame, mobile_net)
                except Exception as e:
                    print(f"[ERROR] Exception during phone detection: {e}")
                    phone_boxes = []
                # Instead of checking if the phone is inside a face's bounding box, 
                # check if there is at least one phone_box and at least one known face.
                if phone_boxes and any(name != "Unknown" for name in face_names):
                    # Get the first known face to use its name
                    recognized_name = next(name for name in face_names if name != "Unknown")
                    normalized_name = recognized_name.replace("_", " ")
                    alert_message = f"Please put your phone away, {normalized_name}"
                    print(f"[DEBUG] Alert triggered: {alert_message}")
                    current_time = time.time()
                    # Use a per-face alert frequency check if desired
                    last_time = last_alert_time.get(recognized_name, 0)
                    if current_time - last_time >= ALERT_TIME_GAP:
                        last_alert_time[recognized_name] = current_time
                        threading.Thread(target=tts_alert, args=(alert_message,), daemon=True).start()


            cv2.imshow("AI-Powered Attendance System", frame)
            key = cv2.waitKey(30) & 0xFF
            if key == ord("r"):
                recent_emotions.clear()
            if key == ord("q"):
                print("Quitting...")
                break

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
    except Exception as ex:
        print(f"[ERROR] Exception in main loop: {ex}")
    finally:
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

