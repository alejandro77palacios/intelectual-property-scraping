import pandas as pd
from pdftotext import PDF

from join_pdfs import PDFSorter
from pdf_pages.basic_page import PdfPage
from pdf_pages.contents_page import ContentsPage
from pdf_pages.invention_page import InventionPage


def boundaries_extraction(boundaries_category, boundaries_pdf):
    start_category, end_category = [float(b) for b in boundaries_category]
    start_pdf, end_pdf = [float(b) for b in boundaries_pdf]
    category_starts_in_pdf = start_pdf <= start_category
    category_ends_in_pdf = end_pdf <= end_category
    if category_starts_in_pdf:
        start_extraction = start_category
        if category_ends_in_pdf:
            end_extraction = end_category
        else:
            end_extraction = end_pdf
    else:
        start_extraction = start_pdf
        if category_ends_in_pdf:
            end_extraction = end_category
        else:
            end_extraction = end_pdf
    return start_extraction, end_extraction


def load_pdf(path):
    with open(path, 'rb') as file:
        pdf = PDF(file)
    return pdf


def is_contents_page(text):
    return 'CONTENTS' in text


def is_invention_page(text):
    return 'Title of the invention' in text


class DateProcessor:
    def __init__(self, path):
        self.path = path
        self.pdf_directory = self.path / 'pdf'
        self.csv_directory = self.path / 'csv'
        self.csv_directory.mkdir(exist_ok=True)
        self.pdfs_paths = PDFSorter(self.pdf_directory).sort_pdf_files()
        self.pdf_files = [load_pdf(path) for path in self.pdfs_paths]
        self.categories = None
        self.boundary_pages_per_category = None
        self.boundary_pages_per_pdf = []

    def export_data(self):
        self.find_contents_page()
        self.find_boundaries_pages_per_pdf()
        self.boundary_pages_per_pdf = dict(enumerate(self.boundary_pages_per_pdf))
        for category in self.categories:
            self.export_category(category)

    def export_category(self, category):
        datasets = self.process_category(category)
        names = ('applications', 'applicant_names', 'inventor_names')
        category_directory = self.csv_directory / category
        category_directory.mkdir(exist_ok=True)
        for name, dataset in zip(names, datasets):
            df = pd.DataFrame(dataset)
            df.replace('NA', '', inplace=True)
            destination_path = self.csv_directory / category / f'{name}.csv'
            if destination_path.exists():
                print(f'{destination_path} already exists')
                continue
            df.to_csv(destination_path, index=False)
            print(f'Successful export {destination_path}')

    def process_category(self, category):
        pdf_indices = self.get_pdf_files_per_category(category)
        applications_in_category = []
        applicant_names_in_category = []
        inventor_names_in_category = []
        for i in pdf_indices:
            boundaries_pdf = self.boundary_pages_per_pdf[i]
            boundaries_category = self.boundary_pages_per_category[category]
            start_extraction, end_extraction = boundaries_extraction(boundaries_category, boundaries_pdf)
            pdf = self.pdf_files[i]
            for page in pdf:
                if not is_invention_page(page):
                    continue
                invention_page = InventionPage(page)
                page_number = invention_page.get_page_number(as_int=True)
                if start_extraction <= page_number <= end_extraction:
                    application = invention_page.extract_application()
                    applicant_names = invention_page.extract_applicant_names()
                    inventor_names = invention_page.extract_inventor_names()
                    applications_in_category.append(application)
                    applicant_names_in_category.extend(applicant_names)
                    inventor_names_in_category.extend(inventor_names)
        return applications_in_category, applicant_names_in_category, inventor_names_in_category

    def get_pdf_files_per_category(self, category):
        start_category, end_category = [float(b) for b in self.boundary_pages_per_category[category]]
        pdf_indices_in_category = []
        for i in self.boundary_pages_per_pdf:  # use indices to preserve the order
            start_pdf, end_pdf = [float(b) for b in self.boundary_pages_per_pdf[i]]
            start_condition = start_pdf <= start_category <= end_pdf
            end_condition = start_pdf <= end_category <= end_pdf
            if start_condition or end_condition:
                pdf_indices_in_category.append(i)
        return pdf_indices_in_category

    def find_contents_page(self):
        first_pdf = self.pdf_files[0]
        for page in first_pdf:
            if is_contents_page(page):
                contents = ContentsPage(page)
                contents.get_limits()
                self.categories = contents.categories
                self.boundary_pages_per_category = contents.limit_pages
                return
        raise ValueError('No contents page found in the first pdf file')

    def find_boundaries_pages_per_pdf(self):
        for pdf in self.pdf_files:
            boundary_pages = [pdf[0], pdf[-1]]
            boundary_page_numbers = [PdfPage(page).get_page_number() for page in boundary_pages]
            self.boundary_pages_per_pdf.append(tuple(boundary_page_numbers))

    def process_pdf(self, pdf):
        for page in pdf:
            if is_contents_page(page):
                contents = ContentsPage(page)
                self.boundary_pages_per_category = contents.get_limits()
                break
        raise ValueError('No contents page found in the first pdf file')


if __name__ == '__main__':
    from pathlib import Path

    path = Path('files') / '001'
    processor = DateProcessor(path)
    processor.export_data()
