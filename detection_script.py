import os
import uuid
import cv2
import argparse
import shutil
from ultralytics import YOLO
from transformers import pipeline
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

# =====================
# HuggingFace Token
# =====================
HUGGINGFACE_TOKEN = "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"

# =====================
# YOLO Models
# =====================
MODEL_PATH = "custommodel_best.pt"
MODEL_PATH2 = "yolov8n.pt"

custom_model = YOLO(MODEL_PATH)
pretrained_model = YOLO(MODEL_PATH2)

# =====================
# Text Generation Pipeline
# =====================
try:
    text_gen = pipeline(
        "text2text-generation",
        model="google/flan-t5-large",
        device=-1
    )
    print("✅ Using flan-t5-large")
except Exception:
    text_gen = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        device=-1
    )
    print("✅ Using flan-t5-base")


# =====================
# detect_video function
# =====================
def detect_video(video_path, output_dir, output_name=None, enable_audio=True, audio_output=None):
    os.makedirs(output_dir, exist_ok=True)

    # unique filenames
    base_id = output_name or f"final_{uuid.uuid4().hex}"
    combined_video_path = os.path.abspath(os.path.join(output_dir, f"combined_{base_id}.mp4"))
    final_video_path = os.path.abspath(os.path.join(output_dir, f"{base_id}.mp4"))
    narration_audio_path = os.path.abspath(os.path.join(output_dir, f"narration_{base_id}.mp3"))

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(combined_video_path, fourcc, fps, (width, height))

    detected_objects = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        res_custom = custom_model(frame, verbose=False)
        res_pretrained = pretrained_model(frame, verbose=False)

        custom_frame = res_custom[0].plot()
        pretrained_frame = res_pretrained[0].plot()

        if custom_frame is None:
            custom_frame = frame.copy()
        if pretrained_frame is None:
            pretrained_frame = frame.copy()

        if custom_frame.shape[2] == 4:
            custom_frame = cv2.cvtColor(custom_frame, cv2.COLOR_BGRA2BGR)
        if pretrained_frame.shape[2] == 4:
            pretrained_frame = cv2.cvtColor(pretrained_frame, cv2.COLOR_BGRA2BGR)

        combined_frame = cv2.addWeighted(custom_frame, 0.5, pretrained_frame, 0.5, 0)

        labels = []
        labels += [int(box.cls) for box in res_custom[0].boxes] if hasattr(res_custom[0], 'boxes') else []
        labels += [int(box.cls) for box in res_pretrained[0].boxes] if hasattr(res_pretrained[0], 'boxes') else []

        names = []
        for cls in labels:
            name = custom_model.names.get(cls) if cls in custom_model.names else pretrained_model.names.get(cls, "unknown")
            names.append(name)
        detected_objects.update(names)

        if combined_frame.shape[1] != width or combined_frame.shape[0] != height:
            combined_frame = cv2.resize(combined_frame, (width, height))

        out.write(combined_frame)

    cap.release()
    out.release()

    if not detected_objects or not enable_audio:
        return combined_video_path, None

    # ========== Narration Prompt ==========
    label_str = ", ".join(sorted(set(detected_objects)))
    prompt = (
        f"Generate a rich, natural, and vivid description of the scene. "
        f"The scene contains the following unique objects: {label_str}. "
        "Ensure that each object is mentioned in the narration. "
        "Describe their positions, movements, and interactions in detail, "
        "as if you are narrating the events unfolding in a video."
    )

    if "zebra crossing" in label_str.lower():
        prompt += (
            " If a zebra crossing is present, describe it as a safe passage where "
            "people may be waiting at the edge, preparing to cross, or observing "
            "the traffic before stepping forward."
        )

    if any(word in label_str.lower() for word in ["car", "vehicle"]):
        prompt += (
            " When cars or vehicles are present, describe whether they are moving, "
            "stopped, or slowing down, and how they relate to the road and pedestrians."
        )

    if any(word in label_str.lower() for word in ["person", "pedestrian"]):
        prompt += (
            " If persons or pedestrians are present, describe whether they are walking, "
            "standing, crossing, or waiting, and how they interact with vehicles and the road."
        )

    if "traffic light" in label_str.lower():
        prompt += (
            " If a traffic light is present, describe its color and how it affects the "
            "behavior of vehicles and pedestrians in the scene."
        )

    # Narration generation
    text_output = text_gen(prompt, max_length=80, do_sample=True)[0].get("generated_text", "").strip()
    print(f"📝 Narration: {text_output}")

    try:
        tts = gTTS(text_output)
        tts.save(narration_audio_path)

        # ✅ if audio_output explicitly requested, copy narration file there too
        if audio_output:
            shutil.copyfile(narration_audio_path, audio_output)

    except Exception as e:
        print("gTTS failed:", e)
        return combined_video_path, None

    # ========== Merge Video + Audio ==========
    try:
        video_clip = VideoFileClip(combined_video_path)
        audio_clip = AudioFileClip(narration_audio_path)
        final_clip = video_clip.set_audio(CompositeAudioClip([audio_clip]))

        write_kwargs = dict(
            codec="libx264",
            audio_codec="aac",
            fps=video_clip.fps or fps,
            threads=4,
            temp_audiofile=os.path.join(output_dir, f"temp-audio-{base_id}.m4a"),
            remove_temp=True,
            logger=None
        )
        final_clip.write_videofile(final_video_path, **write_kwargs)

        final_clip.close()
        video_clip.close()
        audio_clip.close()
    except Exception as e:
        print("⚠️ MoviePy merge failed, returning combined video only. Error:", e)
        return combined_video_path, narration_audio_path

    return final_video_path, narration_audio_path


# =====================
# CLI entry point
# =====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video processing with YOLO + narration")
    parser.add_argument("--input", required=True, help="Input video path")
    parser.add_argument("--output", required=True, help="Output video path")
    parser.add_argument("--audio_output", required=False, help="Optional narration audio output path")
    parser.add_argument("--enable_audio", action="store_true", help="Enable narration audio")

    args = parser.parse_args()

    output_dir = os.path.dirname(args.output) or "."
    output_name = os.path.splitext(os.path.basename(args.output))[0]

    final_path, audio_path = detect_video(
        args.input,
        output_dir,
        output_name,
        enable_audio=args.enable_audio,
        audio_output=args.audio_output
    )

    print("✅ Final video saved at:", final_path)
    if audio_path:
        print("✅ Narration audio saved at:", audio_path)
