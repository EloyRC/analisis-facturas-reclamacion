import pdfplumber
import re
from datetime import datetime
import os
import csv
import argparse

mapa_eventos = {
    '2018111519233ES0031102442324002CJ0F': '(a) Inicio Facturas estimadas',
    '2020071606452ES0031102442324002CJ0F': '(b) Incremento consumo estimado',
    '2021110328107ES0031102442324002CJ0F': '(c) Cambio periodos de facturacion (31-05-2021)',
    '2022072805183ES0031102442324002CJ0F': '(d) Fecha inicio regularizacion e-distribucion (31-05-2022)',
    '2023022205548': '(e) Fecha fin regularizacion e-distribucion (31-01-2023)',
    '2024022707484': '(f) Fecha cambio de contador (9-02-2024)'
}

def extract_fenie(text):
    '''Extráe el consumo facturado por Fenie Energía de una factura'''
    # Regex pattern with explanation:
    pattern = r'''
    P(\d+):                       # Match P1/P2/P3
    (?:.*?)                       # Skip intermediate content
    x\s*                          # Multiplication symbol
    ([ \d\.,]+?)                  # Capture value with spaces, commas, and dots
    kWh                           # kWh unit
    '''
    results = []
    
    # Search for matches using regex
    matches = re.findall(pattern, text, re.VERBOSE | re.IGNORECASE)
    
    for p_number, raw_value in matches:
        # Clean the value: remove spaces, convert EU to US number format
        cleaned = (
            raw_value.replace(' ', '')
            .replace('.', '')  # Remove thousand separators
            .replace(',', '.') # Convert decimal comma to dot
        )
        results.append(cleaned)
    
    return results

def extract_endesa(text):
    '''Extráe las lecturas aportadas por E-distribucion de una factura'''
    lines = text.split('\n')
    c = ''
    for l in lines:
        if 'Consumo' in l:
            c = l
            break
    
    r = []
    for raw_value in c.split(' ')[1:]:
        # Clean the value: remove spaces, convert EU to US number format
        cleaned = (
            raw_value.replace(' ', '')
            .replace('.', '')  # Remove thousand separators
            .replace(',', '.') # Convert decimal comma to dot
        )
        r.append(cleaned)

    return r

def extract_tpl(text):
    '''Extráe si la lectura es directa del contador (TPL) o estimada en una factura'''
    lines = text.split('\n')
    c = ''
    for l in lines:
        if 'TPL' in l:
            return 'True'
    
    return ''

def extract_number_of_days(text):
    '''Extráe el número de días facturados en una factura'''
    pattern = r"(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})"
    match = re.search(pattern, text)
    if match:
        start_date_str, end_date_str = match.groups()
        date_format = "%d/%m/%Y"
        start_date = datetime.strptime(start_date_str, date_format)
        end_date = datetime.strptime(end_date_str, date_format)
        return start_date_str, end_date_str, (end_date - start_date).days
    return 0

def extract_consumo(pdf_path):
    '''Extráe los datos de consumo de una factura'''
    r1 = []
    r2 = []
    tpl = ''
    with pdfplumber.open(pdf_path) as pdf:
        # Iterate through all pages in the PDF
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if i == 0:
                r1 = extract_fenie(text)
            elif i == 1:
                r2 = extract_endesa(text)
                tpl = extract_tpl(text)
                start_date_str, end_date_str, n_days = extract_number_of_days(text)

    return r1, r2, tpl, start_date_str, end_date_str, n_days

def extract_bill_number(pdf_path):
    '''Extráe el núero de la factura del nombre del PDF'''
    # Extract the bill name from the PDF path
    bill_name_full = pdf_path.split('/')[-1].split('.')[0]
    # Case 'Factura Nз 2015060201569ES0031102442324002CJ0F'
    if bill_name_full[0] == 'F':
        bill_name = bill_name_full.split(' ')[-1]
    # Case 'factura_2023042701022'
    elif bill_name_full[0] == 'f':
        bill_name = bill_name_full.split('_')[1]

    return bill_name


def main():
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Extract data from Fenie Energía invoices')
    parser.add_argument('path_invoices', help='Directory path containing PDF invoices')
    args = parser.parse_args()
    
    # Get files from the provided path
    onlyfiles = []
    for root, dirs, files in os.walk(args.path_invoices):
        for file in files:
            if file.lower().endswith('.pdf'):
                onlyfiles.append(os.path.join(root, file))
    onlyfiles.sort()
    
    # Extract consumo from all files and write them to a .csv file
    with open('consumo.csv', mode='w', newline='') as csvfile:
        fieldnames = ['bill_number', 'eP1', 'eP2', 'eP3', 'eP4', 'eP5', 'eP6', 'fP1', 'fP2', 'fP3', 'fP4', 'fP5', 'fP6', 
                      'start_date', 'end_date', 'tpl', 'n_days', 'Evento']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for pdf_path in onlyfiles:
            bill_number = extract_bill_number(pdf_path)
            print(f"Procesando {bill_number}")
            r1, r2, tpl, start_date_str, end_date_str, n_days = extract_consumo(pdf_path)
            # Assuming the order of values is P1, P2, P3
            if len(r1) == 3 and len(r2) == 3:
                writer.writerow({'bill_number': bill_number,
                                'eP1': r2[0], 'eP2': r2[1], 'eP3': r2[2], 'eP4': 0, 'eP5': 0, 'eP6': 0,
                                'fP1': r1[0], 'fP2': r1[1], 'fP3': r1[2], 'fP4': 0, 'fP5': 0, 'fP6': 0, 
                                'start_date': start_date_str, 'end_date': end_date_str, 'tpl': tpl, 'n_days': n_days,
                                'Evento': mapa_eventos.get(bill_number, '')})
            elif len(r1) == 6 and len(r2) == 6:
                writer.writerow({'bill_number': bill_number,
                                'eP1': r2[0], 'eP2': r2[1], 'eP3': r2[2], 'eP4': r2[3], 'eP5': r2[4], 'eP6': r2[5],
                                'fP1': r1[0], 'fP2': r1[1], 'fP3': r1[2], 'fP4': r1[3], 'fP5': r1[4], 'fP6': r1[5],
                                'start_date': start_date_str, 'end_date': end_date_str, 'tpl': tpl, 'n_days': n_days,
                                'Evento': mapa_eventos.get(bill_number, '')})
            else:
                print(f"Not enough values extracted from {pdf_path}")
                print(f"r1: {r1}, r2: {r2}")

if __name__ == "__main__":
    main()
