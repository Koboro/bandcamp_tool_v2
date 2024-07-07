from flask import Blueprint, request, render_template, redirect, url_for, send_from_directory, current_app
import os
import pandas as pd
from .utils import generate_reports

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

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
