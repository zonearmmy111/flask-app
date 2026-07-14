# ใช้ base image Python
FROM python:3.11-slim

# สร้าง working directory
WORKDIR /app

# คัดลอกไฟล์ทั้งหมดเข้า container
COPY . .

# ติดตั้ง Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ระบุพอร์ตที่เปิด
EXPOSE 10000

# รัน Gunicorn โดยใช้พอร์ต 10000
CMD ["gunicorn", "arm:app", "--bind", "0.0.0.0:10000"]
