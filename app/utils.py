import os
import pandas as pd
from fpdf import FPDF
from zipfile import ZipFile

def generate_reports(data, period, label_percentage, generate_pdfs):
    report_folder = current_app.config['REPORT_FOLDER']
    excel_path = os.path.join(report_folder, f'Sales_Report_{period}.xlsx')
    
    data['Label Share'] = data['Total Sales'] * (label_percentage / 100)
    data['Artist Share'] = data['Total Sales'] - data['Label Share']
    
    summary = data.groupby('Artist').sum()
    summary.to_excel(excel_path)

    pdf_paths = []
    if generate_pdfs:
        for artist, group in data.groupby('Artist'):
            pdf_path = os.path.join(report_folder, f'{artist}_{period}.pdf')
            generate_pdf(artist, group, pdf_path)
            pdf_paths.append(pdf_path)
        
        with ZipFile(os.path.join(report_folder, f'PDF_Reports_{period}.zip'), 'w') as zipf:
            for pdf_path in pdf_paths:
                zipf.write(pdf_path, os.path.basename(pdf_path))
    
    return excel_path, pdf_paths

def generate_pdf(artist, data, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, f'Sales Report for {artist}')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    
    for index, row in data.iterrows():
        pdf.cell(40, 10, f"{row['Title']}: {row['Total Sales']}")
        pdf.ln(10)
    
    pdf.output(output_path)
