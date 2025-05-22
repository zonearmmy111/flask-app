FROM python:3.11-slim

# ติดตั้ง libGL สำหรับ OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    tesseract-ocr \
 && rm -rf /var/lib/apt/lists/*

# Copy และติดตั้งโค้ด
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# สั่งรัน
CMD ["gunicorn", "-b", "0.0.0.0:10000", "arm:app"]
