# # attendance_utils.py
# import cv2
# from config import FRAME_RESIZE_SCALE

# def draw_labels(frame, face_locations, face_names):
#     """
#     Draws bounding boxes and names for each detected face.
#     """
#     for (top, right, bottom, left), name in zip(face_locations, face_names):
#         cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#         cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#         cv2.putText(
#             frame, 
#             name, 
#             (left + 6, bottom - 6),
#             cv2.FONT_HERSHEY_DUPLEX, 
#             1.0, 
#             (255, 255, 255), 
#             1
#         )
#     return frame

# def draw_emotions(frame, face_locations, emotions):
#     """
#     Draws the detected emotion and its confidence near the corresponding face.
#     """
#     for ((top, right, bottom, left), (emotion, score)) in zip(face_locations, emotions):
#         if emotion is None or score is None:
#             text = "No emotion"
#         else:
#             text = f"{emotion} ({score:.2f})"
#         cv2.putText(
#             frame, 
#             text, 
#             (left, max(top - 10, 0)), 
#             cv2.FONT_HERSHEY_SIMPLEX, 
#             0.5, 
#             (255, 0, 0), 
#             2
#         )
#     return frame


# attendance_utils.py
import cv2
from datetime import timedelta
import sqlite3
import pandas as pd
from config import DATABASE_PATH

def draw_labels(frame, face_locations, face_names):
    """
    Draws bounding boxes and names on the frame.
    The name is drawn on a filled black rectangle for better legibility.
    """
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        text = name
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        cv2.rectangle(frame, (left, bottom - text_height - baseline), (left + text_width, bottom), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, text, (left, bottom - baseline), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    return frame

def draw_emotions(frame, face_locations, emotions):
    """
    Draws the detected emotion and its confidence near each face.
    """
    for ((top, right, bottom, left), (emotion, score)) in zip(face_locations, emotions):
        text = f"{emotion} ({score:.2f})" if emotion and score is not None else "No emotion"
        cv2.putText(frame, text, (left, max(top - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    return frame

def compute_attendance_summary_for_student(student_name, db_path=DATABASE_PATH):
    """
    Computes the attendance summary for a given student.
    It groups records by the hour slot (using floor('H')) and:
      - Sums total seconds attended.
      - Counts an hour as “present” if seconds >= 2700 (75% of an hour).
    Returns a summary string.
    """
    conn = sqlite3.connect(db_path)
    query = "SELECT timestamp FROM attendance WHERE name = ? ORDER BY timestamp"
    df = pd.read_sql_query(query, conn, params=(student_name,))
    conn.close()
    if df.empty:
        return "No attendance records."
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Floor timestamp to the hour
    df['hour_slot'] = df['timestamp'].dt.floor('H')
    # Count records per hour slot (each record is assumed to be logged once per second)
    grouped = df.groupby('hour_slot').size().reset_index(name='seconds_attended')
    total_duration_seconds = grouped['seconds_attended'].sum()
    duration_str = str(timedelta(seconds=int(total_duration_seconds)))
    # Count eligible hours (>=2700 seconds)
    eligible_hours = (grouped['seconds_attended'] >= 2700).sum()
    total_slots = grouped['hour_slot'].nunique()
    summary = f"Total eligible hours present: {eligible_hours} out of {total_slots}, Duration attended: {duration_str}"
    return summary
