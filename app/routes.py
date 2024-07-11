import chardet
from flask import Blueprint, request, render_template, redirect, url_for, send_from_directory, current_app
import os
import csv
import pandas as pd
from .utils import generate_reports
 
main = Blueprint('main', __name__)
 
@main.route('/')
def index():
    return render_template('index.html')
 
 
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']
 
 
@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('main.index'))
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('main.process_file', filename=file.filename))
    else:
        return 'Invalid file type. Please upload a CSV file.'
 
@main.route('/process/<filename>')
def process_file(filename):
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
 
     # Detect encoding
    encoding = detect_encoding(filepath)
    print(f"Detected file encoding: {encoding}")
 
    try:
        data = pd.read_csv(filepath, encoding=encoding, quoting=csv.QUOTE_MINIMAL, on_bad_lines='error')
    except UnicodeDecodeError:
        print(f"Failed to read file with detected encoding, trying with iso-8859-1")  
        data = pd.read_csv(filepath, encoding='iso-8859-1', quoting=csv.QUOTE_MINIMAL, on_bad_lines='skip')
        print("First 3 rows of the data:") 
        print(data.head(3))
    except pd.errors.ParserError as e:
        print(f"ParserError: {e}")
        # return redirect(url_for('index'))  
 
    
    try:
         data = pd.read_csv(filepath)
    except Exception as e:
         return str(e)
 
    period = request.args.get('period')
    label_percentage = float(request.args.get('label_percentage'))
    generate_pdfs = request.args.get('generate_pdfs') == 'on'
 
    excel_path, pdf_paths = generate_reports(data, period, label_percentage, generate_pdfs)
    return redirect(url_for('main.download_report', filename=os.path.basename(excel_path)))
 
@main.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(current_app.config['REPORT_FOLDER'], filename)
 