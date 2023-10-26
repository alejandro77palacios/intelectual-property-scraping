import re

from ipindia.cleaning import SimpleFieldsCleaner, ProblematicFieldsCleaner
from ipindia.pdf_pages.basic_page import PdfPage


class InventionPage(PdfPage):
    def __init__(self, text):
        super().__init__(text)
        self.separation_pattern = re.compile('\(\d{1,2}\)')
        self.pieces = self.separation_pattern.split(self.text)[1:]
        self.data = self.get_data()

    def get_data(self):
        simple_data = SimpleFieldsCleaner(self.pieces).clean()
        problematic_data = ProblematicFieldsCleaner(self.pieces).clean()
        return {**simple_data, **problematic_data, 'Country': 'India'}

    def extract_application(self):
        key_mapping = {
            'Application No.': 'Application',
            'Date of filing of Application': 'Date of Filing',
            'Publication Date': 'Publication Date',
            'Title of the invention': 'Title of Invention',
            'International\nclassification': 'International Classification',
            'international_application_date': 'International Application Filing Date',
            'international_publication_no': 'International Publication Number',
            'patent_of_addition_number': 'Patent of Addition to Application Number',
            'divisional_to_application_number': 'Division to Application Number',
            'Abstract': 'Abstract',
            'no_pages': 'No. of Pages',
            'no_claims': 'No. of Claims'
        }
        return {new: self.data[original] for original, new in key_mapping.items()}

    def extract_applicant_names(self):
        # key_mapping = {
        #     'Application No.': 'Application No.',
        #     'name': 'Name of Inventor',
        #     'address': 'Address of Inventor',
        # }
        return self.data['Name of Applicant']

    def extract_inventor_names(self):
        return self.data['Name of Inventor']


if __name__ == '__main__':
    from pdftotext import PDF

    path = 'invent.pdf'
    with open(path, 'rb') as file:
        pdf = PDF(file)
    page = InventionPage(pdf[0])
