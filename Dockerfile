FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-devel

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/SkyworkAI/SkyReels-V3 /app/SkyReels-V3

# Uninstall broken flash-attn, then rebuild from source
RUN pip uninstall -y flash-attn flash-attn-2-cuda 2>/dev/null; \
    pip install --no-cache-dir -r /app/SkyReels-V3/requirements.txt --ignore-installed flash-attn 2>/dev/null || true

RUN pip install --no-cache-dir flash-attn --no-build-isolation --force-reinstall

RUN pip install --no-cache-dir runpod

COPY handler.py /app/handler.py

CMD ["python3", "-u", "/app/handler.py"]
