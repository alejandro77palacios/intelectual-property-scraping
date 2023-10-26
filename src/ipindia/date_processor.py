import pandas as pd
from pdftotext import PDF

from ipindia.cleaning.tables import process_data
from ipindia.pdf_pages.basic_page import PdfPage
from ipindia.pdf_pages.contents_page import Contents
from ipindia.pdf_pages.invention_page import InventionPage
from ipindia.pdf_sorter import PDFSorter


def load_pdf(path):
    with open(path, 'rb') as file:
        pdf = PDF(file)
    return pdf


def is_contents_page(text):
    return 'CONTENT' in text


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
        self.contents_page = self._find_contents_page()
        self.boundary_pages_per_category = self._find_boundaries_pages_per_category()
        self.categories = self._find_categories()
        self.boundary_pages_in_all_pdfs = self._find_boundary_pages_in_all_pdfs()

    def export_data(self):

        for category in ['EARLY PUBLICATION', 'PUBLICATION AFTER 18 MONTHS']:
            if category not in self.categories:
                continue
            print(f'Exporting {category}', end='\n' * 2)
            self.export_invent_category(category)
            print()
        for category in ['WEEKLY ISSUED FER', 'PUBLICATION UNDER SECTION 43(2) IN RESPECT OF THE GRANT']:
            if category not in self.categories:
                continue
            print(f'Exporting {category}', end='\n' * 2)
            self.export_table_category(category)
            print()

    def export_table_category(self, category):
        category_boundaries = self.boundary_pages_per_category[category]
        pdf_indices = self._gather_pdf_indices_in_category(category)
        if len(pdf_indices) == 0:
            raise ValueError(f'No PDFs gathered for {category}')
        for i in pdf_indices:
            pdf_boundaries = self.boundary_pages_in_all_pdfs[i]
            extraction_start, extraction_end = self._compute_extraction_boundaries(category_boundaries, pdf_boundaries)
            pdf = self.pdf_files[i]
            pdf_path = self.pdfs_paths[i]
            first_index = self.get_first_index(pdf, extraction_start)
            last_index = self.get_last_index(pdf, extraction_end)
            if category == 'PUBLICATION UNDER SECTION 43(2) IN RESPECT OF THE GRANT':
                df = process_data(pdf_path, first_index, last_index, correct_serial_number=True)
            else:
                df = process_data(pdf_path, first_index, last_index)
            target_path = self.csv_directory / f'{category}.csv'
            if target_path.exists():
                print(f'{target_path} already exists')
            else:
                print(f'Successful export {target_path}')
                df.to_csv(self.csv_directory / f'{category}.csv', index=False)

    @staticmethod
    def get_first_index(pdf, extraction_start):
        index = 0
        for page in pdf:
            page_number = PdfPage(page).get_page_number(as_int=True)
            if extraction_start <= page_number:
                return index
            index += 1
        raise ValueError('No first index')

    @staticmethod
    def get_last_index(pdf, extraction_end):
        index = 0
        for page in pdf:
            page_number = PdfPage(page).get_page_number(as_int=True)
            if extraction_end <= page_number:
                return index
            index += 1
        raise ValueError('No last index')

    def export_invent_category(self, category):
        datasets = self.produce_datasets(category)
        names = ('applications', 'applicant_names', 'inventor_names')
        category_directory = self.csv_directory / category
        category_directory.mkdir(exist_ok=True)
        for name, dataset in zip(names, datasets):
            df = pd.DataFrame(dataset)
            df.replace('NA', '', inplace=True)
            destination_path = category_directory / f'{name}.csv'
            if destination_path.exists():
                print(f'{destination_path} already exists')
                continue
            df.to_csv(destination_path, index=False)
            print(f'Successful export {destination_path}')

    def produce_datasets(self, category):
        category_boundaries = self.boundary_pages_per_category[category]
        pdf_indices = self._gather_pdf_indices_in_category(category)
        applications_in_category = []
        applicant_names_in_category = []
        inventor_names_in_category = []
        for i in pdf_indices:
            pdf_boundaries = self.boundary_pages_in_all_pdfs[i]
            extraction_start, extraction_end = self._compute_extraction_boundaries(category_boundaries, pdf_boundaries)
            pdf = self.pdf_files[i]
            for page in pdf:
                if not is_invention_page(page):
                    continue
                invention_page = InventionPage(page)
                page_number = invention_page.get_page_number(as_int=True)
                if extraction_start <= page_number <= extraction_end:
                    applications_in_category.append(invention_page.extract_application())
                    applicant_names_in_category.extend(invention_page.extract_applicant_names())
                    inventor_names_in_category.extend(invention_page.extract_inventor_names())
        return applications_in_category, applicant_names_in_category, inventor_names_in_category

    # ------------------------------
    # Preparation methods
    # ------------------------------

    def _gather_pdf_indices_in_category(self, category):
        """
        A PDF contains a category if the category starts or ends in it.
        """
        category_start, category_end = [float(b) for b in self.boundary_pages_per_category[category]]
        pdf_indices = []
        for i in range(len(self.boundary_pages_in_all_pdfs)):
            # use pdf indices instead of pdfs themselves to preserve the order
            current_boundaries = self.boundary_pages_in_all_pdfs[i]
            pdf_start, pdf_end = [float(b) for b in current_boundaries]
            category_starts_in_pdf = pdf_start <= category_start <= pdf_end
            category_ends_in_pdf = pdf_start <= category_end <= pdf_end
            if category_starts_in_pdf or category_ends_in_pdf:
                pdf_indices.append(i)
        return pdf_indices

    def _find_contents_page(self):
        first_pdf = self.pdf_files[0]
        for i, page in enumerate(first_pdf):
            if is_contents_page(page):
                return Contents(self.pdfs_paths[0], i)
        raise ValueError('No contents page found in the first pdf file')

    def _find_categories(self):
        return self.contents_page.categories

    def _find_boundaries_pages_per_category(self):
        return self.contents_page.get_limits()

    def _find_boundary_pages_in_all_pdfs(self):
        result = []
        for pdf in self.pdf_files:
            boundary_pages = [pdf[0], pdf[-1]]
            boundary_page_numbers = [PdfPage(page).get_page_number() for page in boundary_pages]
            result.append(tuple(boundary_page_numbers))
        return result

    @staticmethod
    def _compute_extraction_boundaries(category_boundaries, pdf_boundaries):
        category_start, category_end = [int(b) for b in category_boundaries]
        pdf_start, pdf_end = [int(b) for b in pdf_boundaries]
        category_starts_in_pdf = pdf_start <= category_start
        category_ends_in_pdf = category_end <= pdf_end
        if category_starts_in_pdf:
            extraction_start = category_start
            if category_ends_in_pdf:
                extraction_end = category_end
            else:
                extraction_end = pdf_end
        else:
            extraction_start = pdf_start
            if category_ends_in_pdf:
                extraction_end = category_end
            else:
                extraction_end = pdf_end
        return extraction_start, extraction_end
