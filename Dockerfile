# ใช้ image ที่มี Tesseract ติดตั้งไว้แล้ว
FROM python:3.11-slim

# ติดตั้ง Tesseract และ lib ที่จำเป็น
RUN apt-get update && \
    apt-get install -y tesseract-ocr libglib2.0-0 libsm6 libxrender1 libxext6 && \
    apt-get clean

# ตั้ง working directory
WORKDIR /app

# คัดลอกโค้ดทั้งหมดเข้าไป
COPY . .

# ติดตั้ง dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ระบุ entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "arm:app"]
