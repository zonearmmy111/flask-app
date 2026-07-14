# ใช้ base image Python
FROM python:3.11-slim

# สร้าง working directory
WORKDIR /app

# คัดลอกไฟล์ทั้งหมดเข้า container
COPY . .

# ติดตั้ง Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# รัน Gunicorn โดยอิงตามพอร์ตที่ Cloud แต่ละที่กำหนดให้ (Koyeb = 8000, Render = 10000)
CMD ["sh", "-c", "gunicorn arm:app --bind 0.0.0.0:${PORT:-8000}"]
