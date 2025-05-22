# ใช้ base image ที่มี Tesseract และ OpenCV
FROM python:3.11-slim

# ติดตั้ง dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# สร้าง working directory
WORKDIR /app

# คัดลอกไฟล์ทั้งหมดเข้า container
COPY . .

# ติดตั้ง Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ระบุพอร์ตที่เปิด
EXPOSE 8000

# รัน Gunicorn โดยใช้พอร์ต 8000
CMD ["gunicorn", "arm:app", "--bind", "0.0.0.0:8000"]
