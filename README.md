# AI-Powered Automatic Attendance System

An automated attendance and monitoring system that leverages computer vision to recognize faces, detect emotions, and monitor for mobile phone usage. The system logs attendance data in a database and generates detailed reports by integrating real-time recognition with academic records.

## Table of Contents

Overview
Features
Project Structure
Installation
Usage
Modules Description
Configuration
Reporting
Contributing
License
Acknowledgments

## Overview
This project provides an end-to-end solution for capturing and processing attendance using a webcam. The system:

**Recognizes Faces:** 
Uses the face_recognition library to detect and compare live faces with pre-stored images.
**Detects Emotions:** 
Uses an emotion detection module to analyze facial expressions.
**Monitors Mobile Phone Usage: 
Utilizes a YOLOv5 model to detect mobile phones in video frames.
**Logs Attendance:**
Records attendance data along with timestamps in an SQLite database.
**Generates Reports:**
Collates attendance and academic data to produce PDF reports for individual students.

## Features

**Real-Time Face Recognition:**
Quickly identifies students through live video capture.
**Emotion Analysis:**
Detects and overlays emotion information for detected faces.
**Mobile Phone Detection:**
Alerts users if a mobile phone is detected near recognized faces.
**Attendance Logging:**
Records precise attendance data, including time-based metrics.
**Automated Reporting:**
Generates comprehensive PDF reports by merging attendance records and academic performance from CSV files.
**Configurable Parameters:**
Centralized configurations via config.py to adjust detection tolerances, file paths, and processing scales.


## Project Structure
.
├── known_faces/                 # Directory containing subfolders for each known person

│   ├── Student_1/

│   ├── Student_2/
│   ├── Student_3/

│   ├── Student_4/

│   └── Student_5/

├── yolov5/                      # YOLOv5 model files (if using local model files)

├── attendance_utils.py          # Utility functions for visualizing and processing attendance data

├── camera_module.py             # Handles real-time video capture and frame processing

├── config.py                    # Global configuration parameters (paths, thresholds, etc.)

├── database.py                  # Initializes and logs data to the SQLite attendance database

├── emotion_recognition.py       # Detects emotions from faces using the FER library

├── face_recognition_module.py   # Loads known face encodings and recognizes faces in frames

├── mobile_phone_detection_module.py   # Uses a YOLOv5 model to detect mobile phones in video frames

├── read_attendance.py           # Reads and processes attendance data from the database for reporting

├── report_generator.py          # Generates PDF reports combining attendance and academic data

├── main.py                      # Main entry point of the application, integrating all modules

├── requirements.txt             # List of all project dependencies

└── yolov5s.pt                   # Pretrained YOLOv5 weights (if used)


## Installation

**Prerequisites**
Python 3.7+
OpenCV
PyTorch
face_recognition (built on dlib)
FER (Facial Expression Recognition)
gTTS, playsound
fpdf
pandas, numpy
SQLite (bundled with Python)

## Setup Instructions
**1. Clone the Repository**
git clone https://github.com/yourusername/ai-powered-attendance-system.git
cd ai-powered-attendance-system

**2. Install Dependencies**
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

**3. Prepare Known Faces**
Place images of known individuals in the known_faces directory. Create one folder per person (named accordingly).

**4. YOLOv5 Setup**
The project loads the yolov5s model via torch.hub. If you prefer to run it locally, ensure you have the YOLOv5 folder and weights file (yolov5s.pt) in place.

**5. Academic Data**
For report generation, ensure you have an academic_data.csv file formatted with a "Name" column and a "Sem1_TEE","Sem2_TEE",.. fields that holds the GPA information of the corresponding semesters.

## Usage
**Running the Real-Time Attendance System**
python main.py

The system will open a webcam window labeled "AI-Powered Attendance System".
Press "q" to quit.
Press "r" to clear recent emotion data when needed.

**Generating Reports**
To generate a PDF report for a specific student, run:

python report_generator.py

This will create a PDF (e.g., SRUTHY NATH_report.pdf) in the current directory containing both attendance and academic performance summaries.

## Modules Description
**attendance_utils.py:**
Contains functions for annotating frames with bounding boxes and labels, and for summarizing attendance durations.
**camera_module.py:**
Captures video from the webcam, processes frames for face recognition, emotion detection, and mobile phone detection, and handles real-time attendance marking.
**config.py:**
Centralizes configuration parameters, including paths to resources, thresholds for face matching and YOLOv5 detection, and frame scaling factors.
**database.py:**
Manages the SQLite database by initializing necessary tables and recording attendance events with timestamps.
**emotion_recognition.py:**
Leverages the FER library to analyze and determine the dominant emotions from detected face regions.
**face_recognition_module.py:**
Loads known faces from the designated directory and recognizes faces in live frames based on precomputed embeddings.
**mobile_phone_detection_module.py:**
Uses a YOLOv5 model loaded via torch.hub to detect mobile phones, drawing bounding boxes around detected devices.
**read_attendance.py:**
Reads and groups attendance records from the database, and prepares data for report generation.
**report_generator.py:**
Merges attendance data with academic records and creates a formatted PDF report for individual students.
**main.py:**
Serves as the central entry point, orchestrating all modules for real-time face recognition, emotion detection, attendance logging, and mobile phone monitoring.

## Configuration

All configurable parameters (e.g., file paths, detection thresholds, frame resize scale) are stored in config.py. Adjust these values to fine-tune system performance according to your environment and requirements.

## Reporting

The system's reporting capabilities include detailed daily and hourly attendance tracking, along with academic performance summaries. Reports are generated as PDFs via report_generator.py and can be used for administrative review.

## Contributing

Contributions, improvements, and suggestions are welcome! Please open an issue or submit a pull request if you have any ideas:

1. Fork the repository.
2. Create a new branch (git checkout -b feature/your-feature).
3. Commit your changes.
4. Push to your branch and open a pull request.

## Acknowledgments

**face_recognition** for providing an easy-to-use face recognition API.
**ultralytics/yolov5** for the YOLOv5 model and its implementation.
**FER** for the facial expression recognition library.
Various contributors and maintainers who helped make these libraries robust and accessible.
