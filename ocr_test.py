import pytesseract
import cv2
import re
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Tesseract-OCR\tesseract.exe"

def remove_red_text(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # กำหนดช่วงสีแดง (ทั้ง 2 ขอบของวงสี)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # ขยาย mask ให้ครอบคลุมตัวอักษร
    kernel = np.ones((3, 3), np.uint8)
    red_mask_dilated = cv2.dilate(red_mask, kernel, iterations=2)

    # ทำให้ pixel สีแดงกลายเป็นสีขาว
    img[red_mask_dilated > 0] = (255, 255, 255)
    return img

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img = remove_red_text(img)  # <== กรองตัวแดงออกก่อน
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh

def read_text_from_image(image_path):
    preprocessed = preprocess_image(image_path)
    config = "--psm 6 -c tessedit_char_whitelist=0123456789"

    return pytesseract.image_to_string(preprocessed, config=config)

def extract_double_digits(text):
    return re.findall(r'\b\d{2}\b', text)

# 🔄 เปลี่ยนชื่อไฟล์ตรงนี้
image_path = "test.png"

text = read_text_from_image(image_path)
print("📄 ผลลัพธ์จาก OCR:\n", text)

digits = extract_double_digits(text)
print("\n🔢 เลข 2 หลักทั้งหมดที่เจอ:", digits)
