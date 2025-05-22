FROM python:3.11-slim

# ติดตั้ง Tesseract OCR และ libGL ที่จำเป็น
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# ตั้ง working directory
WORKDIR /app

# คัดลอกไฟล์ทั้งหมด
COPY . .

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# สั่งรันแอป
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "arm:app"]
