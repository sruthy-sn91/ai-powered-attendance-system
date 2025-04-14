# face_recognition_module.py
import os
import cv2
import face_recognition
import numpy as np
from config import KNOWN_FACES_DIR, TOLERANCE

def load_known_faces():
    """
    Loads known face encodings and corresponding names from the known_faces directory.
    Skips hidden files (e.g., .DS_Store).
    """
    known_faces = []
    known_names = []
    
    for name in os.listdir(KNOWN_FACES_DIR):
        person_dir = os.path.join(KNOWN_FACES_DIR, name)
        if not os.path.isdir(person_dir):
            continue
        for filename in os.listdir(person_dir):
            if filename.startswith('.'):
                continue
            filepath = os.path.join(person_dir, filename)
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_faces.append(encodings[0])
                known_names.append(name)
    return known_faces, known_names

def recognize_faces(small_frame, known_faces, known_names):
    """
    Detects faces in a resized frame, computes encodings, and compares them with known faces.
    Returns the locations and recognized names in the resized frame's coordinates.
    """
    # Convert to RGB
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect face locations and encodings
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_faces, face_encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]
        face_names.append(name)

    print(f"[DEBUG] Detected {len(face_locations)} face(s) in resized frame: {face_names}")
    return face_locations, face_names
