# emotion_recognition_module.py
from fer import FER
import cv2

# Toggle MTCNN usage; set to True or False based on your testing.
emotion_detector = FER(mtcnn=True)

def detect_emotions(frame, face_locations, margin=0.3):
    """
    For each detected face, crop the face area (with margin) and detect the dominant emotion.
    Returns a list of (emotion, score) tuples.
    """
    emotions = []
    for idx, (top, right, bottom, left) in enumerate(face_locations):
        # Expand bounding box by margin
        width = right - left
        height = bottom - top
        m_w = int(width * margin)
        m_h = int(height * margin)

        top_crop = max(top - m_h, 0)
        left_crop = max(left - m_w, 0)
        bottom_crop = min(bottom + m_h, frame.shape[0])
        right_crop = min(right + m_w, frame.shape[1])

        face_image = frame[top_crop:bottom_crop, left_crop:right_crop]

        # Debug lines removed to prevent window pop-ups
        # cv2.imshow(f"Face_{idx}", face_image)
        # cv2.waitKey(500)
        # cv2.destroyWindow(f"Face_{idx}")

        if face_image.size == 0:
            print(f"[DEBUG] Face {idx}: Empty crop, skipping emotion detection.")
            emotions.append((None, None))
            continue

        emotion, score = emotion_detector.top_emotion(face_image)
        print(f"[DEBUG] Face {idx} (margin={margin}): Emotion={emotion}, Score={score}")
        emotions.append((emotion, score))
    return emotions
