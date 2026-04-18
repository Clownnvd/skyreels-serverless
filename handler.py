import runpod
import subprocess
import base64
import uuid
import os
import shutil
import glob

MODEL_PATH = "/runpod-volume/models/SkyReels-V3-A2V-19B"
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

        with open(img_path, "wb") as f:
            f.write(base64.b64decode(job_input["image_b64"]))
        with open(audio_path, "wb") as f:
            f.write(base64.b64decode(job_input["audio_b64"]))

        resolution = job_input.get("resolution", "480P")
        seed = job_input.get("seed", 42)

        cmd = [
            "python3", f"{SKYREELS_DIR}/generate_video.py",
            "--task_type", "talking_avatar",
            "--model_id", MODEL_PATH,
            "--input_image", img_path,
            "--input_audio", audio_path,
            "--resolution", resolution,
            "--seed", str(seed),
        ]

        if job_input.get("low_vram", True):
            cmd.append("--low_vram")
        if job_input.get("offload", True):
            cmd.append("--offload")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=SKYREELS_DIR)

        # Find output video (generate_video.py saves to ./output/)
        output_files = glob.glob(f"{SKYREELS_DIR}/output/*.mp4") + glob.glob(f"{SKYREELS_DIR}/*.mp4")
        if not output_files:
            return {"status": "error", "message": "No output video found"}

        latest = max(output_files, key=os.path.getmtime)
        with open(latest, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        os.unlink(latest)

        return {"status": "success", "video_b64": video_b64}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)

runpod.serverless.start({"handler": handler})
