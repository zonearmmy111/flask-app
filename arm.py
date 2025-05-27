from flask import Flask, render_template, request, jsonify
import pytesseract
import cv2
import numpy as np
import base64
import re
from io import BytesIO
from PIL import Image
from collections import Counter

app = Flask(__name__)
def extract_double_digits(text):
    return re.findall(r'\d{2}', text)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = []
    duplicates = []
    original_input = ''
    win_input = ''
    win_data = {
        "win2_no_double": [],
        "win2_with_double": [],
        "win3_no_double": [],
        "win3_with_double": []
    }

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'count':
            original_input = request.form.get('numbers', '')
            result_raw = re.findall(r'\d{2}', original_input)
            result = list(dict.fromkeys(result_raw))
            counter = Counter(result_raw)
            duplicates = [num for num, count in counter.items() if count > 1]
            win_input = request.form.get('prev_win_input', '')
            digits = ''.join(filter(str.isdigit, win_input))
            if len(digits) >= 2:
                win_data = get_win_combinations(digits)

        elif form_type == 'win':
            win_input = request.form.get('win_input', '')
            digits = ''.join(filter(str.isdigit, win_input))
            if len(digits) >= 2:
                win_data = get_win_combinations(digits)
            original_input = request.form.get('prev_original_input', '')
            result_raw = re.findall(r'\d{2}', original_input)
            result = list(dict.fromkeys(result_raw))
            counter = Counter(result_raw)
            duplicates = [num for num, count in counter.items() if count > 1]

    return render_template('index.html',
                           result=result,
                           duplicates=duplicates,
                           original_input=original_input,
                           win_data=win_data,
                           win_input=win_input)

def get_win_combinations(digits):
    digits = list(dict.fromkeys(digits))
    win2 = [a + b for i, a in enumerate(digits) for b in digits[i+1:]]
    win2_with_double = [a + b for i, a in enumerate(digits) for j, b in enumerate(digits) if i <= j]
    win3_no_double = [
        a + b + c
        for i, a in enumerate(digits)
        for j, b in enumerate(digits[i+1:], start=i+1)
        for c in digits[j+1:]
    ]
    win3_with_double = [a + b + c for i, a in enumerate(digits) for j, b in enumerate(digits) for k, c in enumerate(digits) if i <= j <= k]
    return {
        "win2_no_double": win2,
        "win2_with_double": win2_with_double,
        "win3_no_double": win3_no_double,
        "win3_with_double": win3_with_double,
    }

@app.route('/ocr-image', methods=['POST'])
def ocr_image():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image data provided', 'text': ''})

        # แยกส่วน base64 header ออก
        try:
            image_data = data['image'].split(',')[1]
        except IndexError:
            return jsonify({'error': 'Invalid image format', 'text': ''})

        # แปลง base64 เป็นรูปภาพ
        try:
            image = Image.open(BytesIO(base64.b64decode(image_data)))
        except Exception as e:
            return jsonify({'error': f'Cannot decode image: {str(e)}', 'text': ''})

        # แปลงเป็น OpenCV format
        try:
            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            return jsonify({'error': f'Cannot convert image: {str(e)}', 'text': ''})

        # Preprocessing
        try:
            # ปรับขนาดภาพให้ใหญ่ขึ้น
            open_cv_image = cv2.resize(open_cv_image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            
            # แปลงเป็นภาพขาวดำ
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
            
            # ปรับความคมชัด
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # ปรับ threshold แบบ adaptive
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # เพิ่ม dilation เพื่อทำให้ตัวเลขชัดขึ้น
            kernel = np.ones((2,2), np.uint8)
            thresh = cv2.dilate(thresh, kernel, iterations=1)
            
        except Exception as e:
            return jsonify({'error': f'Image preprocessing failed: {str(e)}', 'text': ''})

        # OCR
        try:
            # ใช้ค่า PSM ที่เหมาะสมกับการอ่านตัวเลข และเพิ่ม config เพื่อเพิ่มความแม่นยำ
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(thresh, config=custom_config)
        except Exception as e:
            return jsonify({'error': f'OCR process failed: {str(e)}', 'text': ''})

        # แยกเฉพาะเลข 2 หลัก
        numbers = re.findall(r'\d{2}', text)
        
        if not numbers:
            return jsonify({'warning': 'No two-digit numbers found in image', 'text': ''})

        return jsonify({'text': ' '.join(numbers)})

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}', 'text': ''})

