FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-devel

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Remove pre-installed flash-attn if any
RUN pip uninstall -y flash-attn 2>/dev/null || true

RUN git clone https://github.com/SkyworkAI/SkyReels-V3 /app/SkyReels-V3

# Install deps WITHOUT flash-attn first
RUN pip install --no-cache-dir -r /app/SkyReels-V3/requirements.txt 2>/dev/null || \
    pip install --no-cache-dir $(grep -v flash /app/SkyReels-V3/requirements.txt)

# Build flash-attn from source matching this PyTorch
RUN pip install --no-cache-dir flash-attn --no-build-isolation

RUN pip install --no-cache-dir runpod

COPY handler.py /app/handler.py

CMD ["python3", "-u", "/app/handler.py"]
