import runpod
import subprocess
import base64
import uuid
import os
import shutil

MODEL_PATH = "/workspace/models/SkyReels-V3-A2V-19B"
SKYREELS_DIR = "/app/SkyReels-V3"
WORK_DIR = "/tmp/jobs"
os.makedirs(WORK_DIR, exist_ok=True)

def handler(job):
    job_input = job["input"]
    job_id = str(uuid.uuid4())
    job_dir = f"{WORK_DIR}/{job_id}"
    os.makedirs(job_dir)

    try:
        img_path = f"{job_dir}/input.jpg"
        audio_path = f"{job_dir}/input.wav"
        out_path = f"{job_dir}/output.mp4"

        with open(img_path, "wb") as f:
            f.write(base64.b64decode(job_input["image_b64"]))
        with open(audio_path, "wb") as f:
            f.write(base64.b64decode(job_input["audio_b64"]))

        resolution = job_input.get("resolution", "720P")

        cmd = [
            "python3", f"{SKYREELS_DIR}/generate_video.py",
            "--model_path", MODEL_PATH,
            "--input_image", img_path,
            "--input_audio", audio_path,
            "--resolution", resolution,
            "--output_path", out_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        with open(out_path, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()

        return {"status": "success", "video_b64": video_b64}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr}
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)

runpod.serverless.start({"handler": handler})
