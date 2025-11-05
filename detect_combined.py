import cv2, os
from ultralytics import YOLO

# Load both models
custom_model = YOLO("custommodel_best.pt")   # your trained model
pretrained_model = YOLO("yolov8n.pt")            # pretrained YOLOv8n

SAVE_DIR = "tested"
os.makedirs(SAVE_DIR, exist_ok=True)


# =====================
# Detect on Image
# =====================
def detect_image(image_path):
    img = cv2.imread(image_path)

    # Run both models
    res_custom = custom_model(img, verbose=False)
    res_pretrained = pretrained_model(img, verbose=False)

    # Get annotated results separately
    custom_img = res_custom[0].plot()
    pretrained_img = res_pretrained[0].plot()

    # Blend the two (50% + 50%)
    combined_img = cv2.addWeighted(custom_img, 0.5, pretrained_img, 0.5, 0)

    save_path = os.path.join(SAVE_DIR, "combined_test.jpg")
    cv2.imwrite(save_path, combined_img)
    print(f"✅ Combined image saved: {save_path}")


# =====================
# Detect on Video
# =====================
def detect_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(os.path.join(SAVE_DIR, "combined_output.mp4"),
                          fourcc, cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        res_custom = custom_model(frame, verbose=False)
        res_pretrained = pretrained_model(frame, verbose=False)

        custom_frame = res_custom[0].plot()
        pretrained_frame = res_pretrained[0].plot()

        combined_frame = cv2.addWeighted(custom_frame, 0.5, pretrained_frame, 0.5, 0)

        out.write(combined_frame)

    cap.release()
    out.release()
    print("🎥 Combined video saved: tested/combined_output.mp4")


# =====================
# Detect on Webcam
# =====================
def detect_webcam():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        res_custom = custom_model(frame, verbose=False)
        res_pretrained = pretrained_model(frame, verbose=False)

        custom_frame = res_custom[0].plot()
        pretrained_frame = res_pretrained[0].plot()

        combined_frame = cv2.addWeighted(custom_frame, 0.5, pretrained_frame, 0.5, 0)

        cv2.imshow("Combined Detection", combined_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# =====================
# Run test
# =====================
if __name__ == "__main__":
    # Uncomment only one depending on what you want to test:

    #detect_image("test.jpg")          # For image
    detect_video("trafficvideo.mp4")       # For video
    #detect_webcam()                 # For webcam
