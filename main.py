from pathlib import Path

import pandas as pd
from pdftotext import PDF

from extraction import extract_data


def process_row(row_id):
    row_id = str(row_id).zfill(3)
    directory_row = Path('files') / row_id
    directory_data = directory_row / 'data'
    if not directory_data.exists():
        directory_data.mkdir()
    pdf_files = directory_row.glob('*.pdf')
    for file in pdf_files:
        if 'Design' not in file.name:
            df = process_pdf(file)
            csv_path = directory_data / file.name.replace('.pdf', '.csv')
            excel_path = directory_data / file.name.replace('.pdf', '.xlsx')
            df.to_csv(csv_path, index=False)
            df.to_excel(excel_path, index=False)


def process_pdf(path):
    with open(path, 'rb') as file:
        pdf = PDF(file)
    records = []
    for page in pdf:
        if 'Title of the invention' in page:
            records.append(extract_data(page))
    return pd.DataFrame(records)


if __name__ == '__main__':
    process_row(1)
