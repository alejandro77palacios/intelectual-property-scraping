"""
Implements a class to lead with the contents page of a PDF document.
Since it has a complicated structure, there is a need to implement a specific class for it.
"""
import re

from pdf_pages.basic_page import PdfPage


class ContentsPage(PdfPage):
    """
    The `ContentsPage` class represents a contents page extracted from a PDF document. It extends the `PdfPage` class.

    Attributes:
        categories (list): List of categories specified in the contents page.
        pages_range_pattern (re.Pattern): Regular expression pattern to match page ranges.
    """
    categories = ['EARLY PUBLICATION',
                  'PUBLICATION AFTER 18 MONTHS',
                  'WEEKLY ISSUED FER',
                  'PUBLICATION UNDER SECTION 43(2) IN RESPECT OF THE GRANT']
    pages_range_pattern = re.compile(r'\d{4,}\s*[-–]\s*\d{4,}')

    def __init__(self, text):
        """
        Parameters
        ----------
        text: str
            The text content of the PDF page.
        """
        super().__init__(text)
        self.records = self.get_records()
        self.limit_pages = dict.fromkeys(self.categories[:-1])

    def get_records(self):
        """The table is separated by colons, so we split the text by colons to get the records"""
        return [record.strip() for record in self.text.split(':')]

    def get_limits(self):
        """
        Main method. Get the limits for each category in the ContentsPage.

        This method iterates over each category in the limit_pages dictionary and calls the
        _get_category_limits method to retrieve the limits for that category. It then updates
        the limit_pages dictionary with the retrieved limits. Finally, it processes the last
        category in a separate way.
        """
        for category in self.limit_pages:
            self.limit_pages[category] = self._get_category_limits(category)
        self._process_last_category()

    def _get_category_limits(self, category):
        """
        Get the first and last page numbers for a given category.

        Parameters
        ----------
        category : str
            The category for which to retrieve limits.

        Returns
        -------
        tuple
            The first and last page numbers for the given category.
        """
        all_bounds = self._get_all_bounds_in_category(category)
        first_page_number, last_page_number = self._get_first_and_last_pages(all_bounds)
        return first_page_number, last_page_number

    def _process_last_category(self):
        """
        Since the name of the last category is too long, the text extracted from the original table is chaotic.

        In particular, the last category is not followed by a colon, so we have to process it separately.
        """
        last_page = self.limit_pages[self.categories[-2]][1]
        first_page_last_category = int(last_page) + 1
        formatted_page = str(first_page_last_category).zfill(len(last_page))
        self.limit_pages[self.categories[-1]] = formatted_page, float('inf')

    @staticmethod
    def _get_first_and_last_pages(bounds: list):
        """
        Extracts the first and last page numbers from a list of bounds.

        Parameters
        ----------
        bounds : list
            A list containing tuples of page bounds.
            Each tuple represents the start and end page of a section in the PDF.

        Returns
        -------
        tuple
            The first page and last page from the list of bounds.
        """
        first_page = bounds[0][0]
        last_page = bounds[-1][1]
        return first_page, last_page

    def _get_all_bounds_in_category(self, category):
        """We have to go through all the records to know which ones contain the category.

        We split the text by colons to get the records, so the structure of the table looks
        weird. In consequence, when a record contains the category, the next one contains the bounds.
        """
        all_bounds = []
        for i in range(len(self.records)):
            current_record = self.records[i]
            if category in current_record:
                # due to the structure, the next record is the one that contains the bounds
                next_record = self.records[i + 1]
                bounds = self._get_bounds_of_record(next_record)
                all_bounds.append(bounds)
        return all_bounds

    def _get_bounds_of_record(self, record):
        """The text contains the page range in a string, but the page range pattern follows a clear pattern like
        67765 – 67808, so we have to split the string by the dash to get the bounds.
        """
        page_range_match = self.pages_range_pattern.search(record)
        bounds = re.split(r'\s*[-–]\s*', page_range_match.group())
        return tuple(bounds)


if __name__ == '__main__':
    from pprint import pprint
    from pdftotext import PDF

    path = '../contents.pdf'
    with open(path, 'rb') as file:
        pdf = PDF(file)
    processor = ContentsPage(pdf[0])
    processor.get_limits()
    pprint(processor.limit_pages)
