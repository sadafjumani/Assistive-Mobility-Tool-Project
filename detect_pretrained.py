import cv2, os
from ultralytics import YOLO

# Load pretrained model
model = YOLO("yolov8n.pt")

SAVE_DIR = "tested"
os.makedirs(SAVE_DIR, exist_ok=True)

def run_detection(source):
    results = model.predict(source, save=True, project=SAVE_DIR, name="pretrained")
    print(f"✅ Results saved in: {results[0].save_dir}")

if __name__ == "__main__":
    # Change source as needed
    # Examples:
    run_detection("test.jpg")         # image
    # run_detection("video.mp4")      # video
    # run_detection(0)                # webcam
