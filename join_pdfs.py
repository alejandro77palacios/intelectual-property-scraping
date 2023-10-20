from pathlib import Path


class PDFSorter:
    roman_numbers = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

    def __init__(self, directory: Path):
        self.directory = directory
        self.pdf_files = self.get_pdf_files()

    def get_pdf_files(self):
        return list(self.directory.glob('*.pdf'))

    def get_pdf_file_by_roman_number(self, roman_number: str):
        for pdf_file in self.pdf_files:
            if 'design' in pdf_file.stem.lower():
                continue
            if pdf_file.stem.strip().split(' ')[-1] == roman_number:
                return pdf_file
        raise FileNotFoundError

    def sort_pdf_files(self):
        max_number = len(self.pdf_files) - 1
        sorted_files = []
        for i in range(max_number):
            current_roman = self.roman_numbers[i]
            file = self.get_pdf_file_by_roman_number(current_roman)
            sorted_files.append(file)
        return sorted_files


first = Path('files') / '001'
pdf_sorter = PDFSorter(first)
sorted_pdfs = pdf_sorter.sort_pdf_files()
print(sorted_pdfs)