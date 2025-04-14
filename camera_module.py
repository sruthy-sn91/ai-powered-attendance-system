# camera_module.py
import cv2
import time
import threading
import queue
import numpy as np
from face_recognition_module import recognize_faces
from emotion_recognition import detect_emotions
from mobile_phone_detection_module import detect_mobile_phone
from database import mark_attendance
from attendance_utils import draw_labels, draw_emotions

class Camera:
    def __init__(self, known_faces, known_names, mobile_net, frame_resize_scale=0.5, alert_callback=None):
        self.cap = cv2.VideoCapture(0)
        self.frame_resize_scale = frame_resize_scale
        self.known_faces = known_faces
        self.known_names = known_names
        self.mobile_net = mobile_net
        self.alert_callback = alert_callback  # function to call on phone detection
        self.stopped = False
        self.frame_queue = queue.Queue(maxsize=2)
        self.recognized_student = None

        # Start the update thread
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            processed_frame = self.process_frame(frame)
            if not self.frame_queue.full():
                self.frame_queue.put(processed_frame)

    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resize_scale, fy=self.frame_resize_scale)
        face_locations_small, face_names = recognize_faces(small_frame, self.known_faces, self.known_names)
        # Update recognized student (take the first recognized, if any)
        if face_names:
            self.recognized_student = face_names[0]
        else:
            self.recognized_student = None

        scale = 1.0 / self.frame_resize_scale
        face_locations = []
        for (top, right, bottom, left) in face_locations_small:
            face_locations.append((
                int(top * scale),
                int(right * scale),
                int(bottom * scale),
                int(left * scale)
            ))
        for name in face_names:
            if name != "Unknown":
                mark_attendance(name)
        emotions = detect_emotions(frame, face_locations, margin=0.3)
        frame = draw_labels(frame, face_locations, face_names)
        frame = draw_emotions(frame, face_locations, emotions)
        phone_boxes, annotated = detect_mobile_phone(frame, self.mobile_net)
        if phone_boxes:
            for (startX, startY, endX, endY) in phone_boxes:
                phone_center = ((startX + endX) // 2, (startY + endY) // 2)
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    if name != "Unknown" and left <= phone_center[0] <= right and top <= phone_center[1] <= bottom:
                        if self.alert_callback:
                            self.alert_callback(name)
                        break
        return annotated

    def get_frame(self):
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        return None

    def get_recognized_student(self):
        return self.recognized_student

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.cap.release()

if __name__ == "__main__":
    # Test the camera module standalone
    cam = Camera([], [], None)
    while True:
        frame = cam.get_frame()
        if frame:
            img = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow("Test Camera", img)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
    cam.stop()
    cv2.destroyAllWindows()
