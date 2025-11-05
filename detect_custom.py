import cv2, os
from ultralytics import YOLO

# Load custom trained model
model = YOLO("custommodel_best.pt")

SAVE_DIR = "tested"
os.makedirs(SAVE_DIR, exist_ok=True)

def run_detection(source):
    results = model.predict(source, save=True, project=SAVE_DIR, name="custom")
    print(f"✅ Results saved in: {results[0].save_dir}")

if __name__ == "__main__":
    # Change source as needed
    run_detection("test.jpg")        # image
    # run_detection("video.mp4")     # video
    # run_detection(0)               # webcam
