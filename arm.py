from flask import Flask, render_template, request
from collections import Counter
import itertools
import threading
import webbrowser

app = Flask(__name__)

def format_input(input_str):
    if ' ' in input_str:
        numbers = input_str.split()
    else:
        numbers = [input_str[i:i+2] for i in range(0, len(input_str), 2)]
    counter = Counter(numbers)
    duplicates = [num for num, count in counter.items() if count > 1]
    unique_numbers = list(dict.fromkeys(numbers))
    return unique_numbers, duplicates
def win3_with_double_ordered(digits):
    results = []
    for i in range(len(digits)):
        for j in range(i, len(digits)):
            for k in range(j, len(digits)):
                results.append(digits[i] + digits[j] + digits[k])
    return results
def win2_with_double_ordered(digits):
    results = []
    n = len(digits)
    for i in range(n):
        for j in range(i, n):
            pair = digits[i] + digits[j]
            results.append(pair)
    return results


def get_win_combinations(digits):
    digits = list(dict.fromkeys(digits))  # ลบเลขซ้ำแต่รักษาลำดับ

    # วิน 2 ตัว ไม่รวมเบิ้ล
    win2 = [a + b for i, a in enumerate(digits) for b in digits[i+1:]]

    # วิน 2 ตัว รวมเบิ้ล (แบบเรียงลำดับจากซ้ายไปขวา)
    win2_with_double = win2_with_double_ordered(digits)

    # วิน 3 ตัว ไม่รวมเบิ้ล
    win3_no_double = [
        a + b + c
        for i, a in enumerate(digits)
        for j, b in enumerate(digits[i+1:], start=i+1)
        for c in digits[j+1:]
    ]

    # วิน 3 ตัว รวมเบิ้ล (แบบเรียงลำดับ)
    win3_with_double = win3_with_double_ordered(digits)

    return {
        "win2_no_double": win2,
        "win2_with_double": win2_with_double,
        "win3_no_double": win3_no_double,
        "win3_with_double": win3_with_double,
    }





@app.route('/', methods=['GET', 'POST'])
def index():
    result = []
    duplicates = []
    original_input = ''
    win_data = {
    "win2_no_double": [],
    "win2_with_double": [],
    "win3_no_double": [],
    "win3_with_double": []
}

    win_input = ''

    if request.method == 'POST':
        if 'numbers' in request.form:
            original_input = request.form['numbers']
            result, duplicates = format_input(original_input)

        if 'win_input' in request.form:
            win_input = request.form['win_input']
            digits = ''.join(filter(str.isdigit, win_input))
            if 3 <= len(set(digits)) <= 9:
                win_data = get_win_combinations(digits)

    return render_template(
        'index.html',
        result=result,
        duplicates=duplicates,
        original_input=original_input,
        win_input=win_input,
        win_data=win_data
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

