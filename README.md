# Assistive-Mobility-Tool-Project

Enhancing mobility and independence through AI
Overview-:

This project presents an AI-powered assistive mobility system designed to help visually impaired individuals navigate safely.
It uses a camera for real-time object detection through YOLOv8, processes the feed using Python and OpenCV, and provides audio feedback via Text-to-Speech (TTS) to alert users about nearby obstacles.
A simple frontend interface visualizes detections for caregivers or testing purposes.

Key Features-:

1. Real-Time Object Detection using YOLOv8
2. Audio Feedback System for obstacle alerts
3. Priority-Based Warning for critical objects (e.g., vehicles, stairs)
4. Lightweight Frontend for visual monitoring
5. Multi-Language Voice Support for accessibility

Tech Stack-:

Component	Tools / Technologies
Programming Language	Python
AI/ML Model	YOLOv8 (Ultralytics)
Libraries	OpenCV, pyttsx3 / gTTS, Flask, NumPy
Dataset Tool	Roboflow (annotation & augmentation)
Frontend	HTML, CSS, JavaScript
Development Platform	Google Colab

System Workflow-:

Camera Input → YOLOv8 Detection → Python Backend → TTS Audio Output
                             ↓
                      Frontend Visualization

Implementation Summary-:

1. Collected and annotated a custom dataset (stairs, poles, doors, pedestrians, vehicles).
2. Applied augmentation for brightness, rotation, and environmental variation.
3. Trained YOLOv8 model on Google Colab, achieving ~85% mAP.
4. Integrated real-time video detection and voice feedback using Python.
5. Built a simple frontend UI for demonstration and caregiver view.

Challenges Overcome-:

1. Lack of domain-specific dataset → built a custom dataset using Roboflow.
2. Low-light and glare detection issues → solved using augmentation techniques.
3. Real-time lag → optimized with YOLOv8-nano and backend code tuning.
4. Backend–frontend synchronization → implemented Flask-based API communication.

Results-:

1. Real-time detection with low latency and clear audio feedback.
2. Robust performance across indoor/outdoor and varied lighting conditions.
3. Demonstrated strong potential for real-world assistive use.



