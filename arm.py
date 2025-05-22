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
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'text': ''})

    image_data = data['image'].split(',')[1]
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Preprocessing
    open_cv_image = cv2.resize(open_cv_image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

    # OCR (ใช้ image_to_string เหมือนเดิม)
    text = pytesseract.image_to_string(thresh, config='--psm 6 -c tessedit_char_whitelist=0123456789')

    # แยกเฉพาะเลข 2 หลัก
    numbers = re.findall(r'\d{2}', text)

    return jsonify({'text': ' '.join(numbers)})

