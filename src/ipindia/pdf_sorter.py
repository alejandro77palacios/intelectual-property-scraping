import re
from pathlib import Path


class PDFSorter:
    roman_numbers = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

    def __init__(self, directory: Path):
        self.directory = directory
        self.pdf_files = self.get_pdf_files()
        self.uses_roman_numbers = False

    def get_pdf_files(self):
        return list(self.directory.glob('*.pdf'))

    def get_pdf_file_by_roman_number(self, roman_number: str):
        for pdf_file in self.pdf_files:
            if 'design' in pdf_file.stem.lower():
                continue
            raw_num = pdf_file.stem.strip().split(' ')[-1].upper()
            raw_num = raw_num.rstrip('.PDF')
            if '-' in raw_num:
                raw_num = raw_num.split('-')[-1]
            elif '–' in raw_num:
                raw_num = raw_num.split('–')[-1]
            num = re.sub('[^a-zA-Z]', '', raw_num).upper()
            if num == roman_number:
                return pdf_file
        raise FileNotFoundError

    def get_pdf_file_by_normal_number(self, number: str):
        for pdf_file in self.pdf_files:
            if 'design' in pdf_file.stem.lower():
                continue
            if bool(re.search(number, pdf_file.stem)):
                return pdf_file
        raise FileNotFoundError

    def sort_pdf_files(self):
        self._detect_numbers_type()
        if len(self.pdf_files) == 1:
            max_number = 1
        else:
            max_number = len(self.pdf_files) # TODO: updante restar 1
        sorted_files = []
        for i in range(max_number):
            if self.uses_roman_numbers:
                current_roman = self.roman_numbers[i]
                file = self.get_pdf_file_by_roman_number(current_roman)
            else:
                current_number = str(i + 1)
                file = self.get_pdf_file_by_normal_number(current_number)
            sorted_files.append(file)
        return sorted_files

    def _detect_numbers_type(self):
        for pdf_file in self.pdf_files:
            if 'design' in pdf_file.stem.lower():
                continue
            if bool(re.search(r'\d', pdf_file.stem)):
                self.uses_roman_numbers = False
                return
        self.uses_roman_numbers = True


if __name__ == '__main__':
    first = Path('../../files') / '001'
    pdf_sorter = PDFSorter(first)
    sorted_pdfs = pdf_sorter.sort_pdf_files()
    print(sorted_pdfs)
