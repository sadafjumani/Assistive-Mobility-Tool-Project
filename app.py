# import os
# import uuid
# import subprocess
# import sys
# from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# # Folders
# UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
# OUTPUT_FOLDER = os.path.join(app.static_folder, "outputs")  # inside static
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# # In-memory dummy users (for demo; replace with DB in production)
# USERS = {
#     "admin": {"password": "admin123", "email": "admin@example.com"}
# }

# # ---------- ROUTES ----------

# @app.route("/")
# def home():
#     return render_template("home.html", logged_in=session.get("logged_in"))

# @app.route("/about")
# def about():
#     return render_template("about.html", logged_in=session.get("logged_in"))

# @app.route("/technology")
# def technology():
#     return render_template("technology.html", logged_in=session.get("logged_in"))

# @app.route("/contact")
# def contact():
#     return render_template("contact.html", logged_in=session.get("logged_in"))

# @app.route("/upload")
# def upload():
#     if not session.get("logged_in"):
#         return redirect(url_for("login_page"))
#     return render_template("upload.html", logged_in=session.get("logged_in"))

# @app.route("/login", methods=["GET", "POST"])
# def login_page():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         user = USERS.get(username)
#         if user and user["password"] == password:
#             session["logged_in"] = True
#             session["username"] = username
#             return redirect(url_for("upload"))
#         else:
#             return render_template("login.html", error="Invalid credentials", logged_in=False)

#     return render_template("login.html", logged_in=session.get("logged_in"))

# @app.route("/logout")
# def logout():
#     session.pop("logged_in", None)
#     session.pop("username", None)
#     return redirect(url_for("home"))

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         confirm = request.form.get("confirm")

#         if not username or not email or not password:
#             return render_template("register.html", error="All fields are required", logged_in=False)

#         if password != confirm:
#             return render_template("register.html", error="Passwords do not match", logged_in=False)

#         if username in USERS:
#             return render_template("register.html", error="Username already exists", logged_in=False)

#         USERS[username] = {"password": password, "email": email}
#         return redirect(url_for("login_page"))

#     return render_template("register.html", logged_in=session.get("logged_in"))

# # ---------- VIDEO PROCESSING ----------

# @app.route("/process", methods=["POST"])
# def process_video():
#     if "video" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["video"]
#     if file.filename == "":
#         return jsonify({"error": "Empty filename"}), 400

#     enable_audio = request.form.get("enable_audio", "0") == "1"

#     # Save uploaded file
#     input_filename = f"{uuid.uuid4()}.mp4"
#     input_path = os.path.join(UPLOAD_FOLDER, input_filename)
#     file.save(input_path)

#     # Generate output paths
#     output_filename = f"processed_{uuid.uuid4()}.mp4"
#     output_path = os.path.join(OUTPUT_FOLDER, output_filename)

#     audio_filename = f"narration_{uuid.uuid4()}.mp3"
#     audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)

#     try:
#         cmd = [
#             sys.executable, "detection_script.py",
#             "--input", input_path,
#             "--output", output_path,
#             "--audio_output", audio_path
#         ]
#         if enable_audio:
#             cmd.append("--enable_audio")

#         subprocess.run(cmd, check=True)

#     except subprocess.CalledProcessError as e:
#         return jsonify({"error": f"Processing failed: {str(e)}"}), 500

#     return jsonify({
#         "output_url": url_for("static", filename=f"outputs/{output_filename}"),
#         "audio_url": url_for("static", filename=f"outputs/{audio_filename}")
#     })

# # Webcam feed endpoint (optional placeholder)
# @app.route("/webcam_feed")
# def webcam_feed():
#     return "Webcam stream not implemented yet", 501


# # ---------- MAIN ----------
# if __name__ == "__main__":
#     app.run(debug=True)

import os
import uuid
import subprocess
import sys
import time
import cv2
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Folders
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
OUTPUT_FOLDER = os.path.join(app.static_folder, "outputs")  # inside static
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# In-memory dummy users (for demo; replace with DB in production)
USERS = {
    "admin": {"password": "admin123", "email": "admin@example.com"}
}

# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("home.html", logged_in=session.get("logged_in"))

@app.route("/about")
def about():
    return render_template("about.html", logged_in=session.get("logged_in"))

@app.route("/technology")
def technology():
    return render_template("technology.html", logged_in=session.get("logged_in"))

@app.route("/contact")
def contact():
    return render_template("contact.html", logged_in=session.get("logged_in"))

@app.route("/upload")
def upload():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))
    return render_template("upload.html", logged_in=session.get("logged_in"))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = USERS.get(username)
        if user and user["password"] == password:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("upload"))
        else:
            return render_template("login.html", error="Invalid credentials", logged_in=False)

    return render_template("login.html", logged_in=session.get("logged_in"))

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not username or not email or not password:
            return render_template("register.html", error="All fields are required", logged_in=False)

        if password != confirm:
            return render_template("register.html", error="Passwords do not match", logged_in=False)

        if username in USERS:
            return render_template("register.html", error="Username already exists", logged_in=False)

        USERS[username] = {"password": password, "email": email}
        return redirect(url_for("login_page"))

    return render_template("register.html", logged_in=session.get("logged_in"))

# ---------- VIDEO PROCESSING ----------

@app.route("/process", methods=["POST"])
def process_video():
    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    enable_audio = request.form.get("enable_audio", "0") == "1"

    # Save uploaded file
    input_filename = f"{uuid.uuid4()}.mp4"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    # Generate output paths
    output_filename = f"processed_{uuid.uuid4()}.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    audio_filename = f"narration_{uuid.uuid4()}.mp3"
    audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)

    try:
        cmd = [
            sys.executable, "detection_script.py",
            "--input", input_path,
            "--output", output_path,
            "--audio_output", audio_path
        ]
        if enable_audio:
            cmd.append("--enable_audio")

        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

    return jsonify({
        "raw_url": url_for("uploads_file", filename=input_filename),
        "output_url": url_for("static", filename=f"outputs/{output_filename}"),
        "audio_url": url_for("static", filename=f"outputs/{audio_filename}")
    })

# ---------- WEBCAM CAPTURE (15 SEC) + PROCESS ----------

@app.route("/start_webcam")
def start_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return jsonify({"error": "Webcam not found"}), 500

    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    raw_filename = f"webcam_raw_{uuid.uuid4()}.mp4"
    raw_path = os.path.join(UPLOAD_FOLDER, raw_filename)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(raw_path, fourcc, fps, (width, height))

    # Record full 15 seconds
    start_time = time.time()
    while time.time() - start_time < 15:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()

    # Process with detection_script.py
    output_filename = f"processed_webcam_{uuid.uuid4()}.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    audio_filename = f"narration_webcam_{uuid.uuid4()}.mp3"
    audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)

    try:
        cmd = [
            sys.executable, "detection_script.py",
            "--input", raw_path,
            "--output", output_path,
            "--audio_output", audio_path,
            "--enable_audio"
        ]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Webcam processing failed: {str(e)}"}), 500

    return jsonify({
        "raw_url": url_for("uploads_file", filename=raw_filename),
        "output_url": url_for("static", filename=f"outputs/{output_filename}"),
        "audio_url": url_for("static", filename=f"outputs/{audio_filename}")
    })

# ---------- SERVE UPLOADS ----------

@app.route("/uploads/<path:filename>")
def uploads_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True)
