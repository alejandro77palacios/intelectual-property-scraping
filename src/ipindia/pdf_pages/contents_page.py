import re

import camelot
#import numpy as np
import pandas as pd
import pdfplumber


class Contents:
    categories = ['EARLY PUBLICATION',
                  'PUBLICATION AFTER 18 MONTHS',
                  'WEEKLY ISSUED FER',
                  'PUBLICATION UNDER SECTION 43(2) IN RESPECT OF THE GRANT']

    def __init__(self, pdf_path, contents_index):
        self.pdf_path = pdf_path
        self.contents_index = contents_index
        self.df = self._build_df()
        self._clean_df()

    def get_limits(self):
        limits_mapping = dict.fromkeys(self.categories)
        categories_to_remove = []
        for category in self.categories:
            page_ranges = self.df.loc[self.df['aux'].apply(self._matches_category, args=(category, )), 'Page number']
            page_ranges = page_ranges[page_ranges.str.strip() != '']
            limits = page_ranges.apply(lambda x: self._get_limits_in_range(x))
            if limits.empty:
                categories_to_remove.append(category)
                continue
            first = limits.iloc[0][0]
            last = limits.iloc[-1][-1]
            limits_mapping[category] = (first, last)
        if categories_to_remove:
            for category in categories_to_remove:
                print(f'The PDF seems to lack of {category} category')
                self.categories.remove(category)
        return limits_mapping

    def _build_df(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            pages = pdf.pages
            contents = pages[self.contents_index]
            table = contents.extract_table()
            if table is None:
                # table_settings = {'vertical_strategy': 'text',
                #                   'horizontal_strategy': 'text'}
                # table = contents.extract_table(table_settings=table_settings)
                # df = pd.DataFrame(table[1:], columns=table[0])
                # df['concatenada'] = df.apply(lambda row: ''.join(row.astype(str)), axis=1)
                # df = df[['concatenada']]
                # df.dropna(inplace=True)
                # df = df['concatenada'].str.split(r':', expand=True)
                # df = df.replace('', np.nan)
                # df.dropna(inplace=True)
                tables = camelot.read_pdf(str(self.pdf_path),
                                          pages=str(self.contents_index + 1),
                                          table_areas=['50,700,600,100'],
                                          edge_tol=500,
                                          columns=['410'],
                                          row_tol=15,
                                          flavor='stream')
                df = tables[0].df
                subject_series = df[df.iloc[:, 0].str.contains('Subject', na=False, case=False)]
                if subject_series.empty:
                    subject_index = 0
                else:
                    subject_index = subject_series.index[0]
                df = df[subject_index:]
                df.columns = df.iloc[0]
                df = df[1:]
            else:
                df = pd.DataFrame(table[1:], columns=table[0])
                assert len(df.columns) == 3, 'The number of columns is not 3'
        return df

    def _clean_df(self):
        self.df = self.df.iloc[:, [0, -1]]
        # self.df.drop(columns=self.df.columns[1], inplace=True)
        self.df.columns = ['Subject', 'Page number']
        self.df.replace(r'\s+', ' ', regex=True, inplace=True)
        self.df = self.df.map(lambda x: str(x).replace(':', ''))
        for col in self.df.columns:
            self.df[col] = self.df[col].str.strip()
        self.df.dropna(subset=['Subject'], inplace=True)
        self.df['aux'] = self.df['Subject'].str.replace(r'\s+', '', regex=True)

        self.df = self.df[self.df['aux'].apply(self._matches_some_category)]
        # self.df.drop(columns=['aux'], inplace=True)

    @staticmethod
    def _matches_category(text, category):
        clean_cat = category.replace(' ', '')
        return (clean_cat in text) or (text in clean_cat)

    @staticmethod
    def _matches_some_category(text):
        for category in Contents.categories:
            if Contents._matches_category(text, category):
                return True
        return False

    @staticmethod
    def _get_limits_in_range(page_range: str):
        # parts = re.split(r'[A-Za-z]', page_range)[-1]
        parts = re.split(r'\s*[-–]+\s*', page_range)
        if len(parts) == 2:
            pass
        elif len(parts) == 1:
            if ' ' in parts[0].strip():
                parts = re.split(r'\s+', parts[0])
            else:
                parts.append(parts[0])
        else:
            raise ValueError('Invalid page range')
        parts = [re.sub(r'\s+', '', part) for part in parts]
        parts = [re.sub(r'after18months', '', part, flags=re.IGNORECASE) for part in parts]
        parts = [re.sub(r'\D+', '', part) for part in parts]
        start, end = parts
        start = int(start)
        try:
            end = int(end)
        except ValueError:
            end = start

        return start, end


if __name__ == '__main__':
    from pprint import pprint

    contents = Contents('2023/2023-01-06/pdf/Part I.pdf', 2)
    pprint(contents.get_limits())
