FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-devel

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/SkyworkAI/SkyReels-V3 /app/SkyReels-V3

# Install deps (skip flash-attn from requirements)
RUN pip install --no-cache-dir $(grep -vi flash /app/SkyReels-V3/requirements.txt) || true

# Fix psutil then install flash-attn with pre-built wheel for PyTorch 2.4 + CUDA 12.4
RUN pip install --no-cache-dir psutil --force-reinstall && \
    pip install --no-cache-dir flash-attn==2.6.3 --no-build-isolation

RUN pip install --no-cache-dir runpod

COPY handler.py /app/handler.py

CMD ["python3", "-u", "/app/handler.py"]
