import pandas as pd
import pdfplumber


def extract_data(path, start_index=0, end_index=None, correct_serial_number=False):
    with pdfplumber.open(path) as pdf:
        pages = pdf.pages
        first_page = pages[start_index]
        first_table = first_page.extract_table()
        df = pd.DataFrame(first_table[1:], columns=first_table[0])
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)
        df.columns = df.columns.str.strip()
        if correct_serial_number:
            df.rename(columns={df.columns[0]: 'Serial Number'}, inplace=True)
        for page in pages[start_index + 1:end_index]:
            table = page.extract_table()
            new_df = pd.DataFrame(table)
            try:
                new_df.columns = df.columns
            except ValueError:
                break
            df = pd.concat([df, new_df], ignore_index=True)
    return df


def clean_data(df):
    df.replace(r'\s+', ' ', regex=True, inplace=True)
    df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
    df.dropna(subset=[df.columns[0]], inplace=True)
    df.iloc[:, 0] = df.iloc[:, 0].astype(int)


def process_data(path, start_index=0, end_index=None, correct_serial_number=False):
    df = extract_data(path, start_index, end_index, correct_serial_number)
    clean_data(df)
    return df
