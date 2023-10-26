"""
Implements the PdfPage class.
"""
import re


class PdfPage:
    """
    A class to represent a PDF page.
    It is intended to be inherited by other classes that represent specific PDF pages.
    """
    page_number_pattern = re.compile(r'(\d{1,})[a-zA-Z\s]*\Z')  # TODO: before \d{3,}

    def __init__(self, text):
        """
        Parameters
        ----------
        text: str
            The text content of the PDF page.

        Attributes
        ----------
        text : str
            The text content of the PDF page.
        page_number : int
            The page number obtained from the text content.
        """
        self.text = text
        self.page_number = self.get_page_number()

    def get_page_number(self, as_int=False):
        """
        Finds the page number in the text content of the PDF page.

        Parameters
        ----------
        as_int: bool
            If True, returns the page number as an integer. Otherwise, returns the page number as a string.

        Returns
        -------
        str or int
        """
        clean_text = re.sub(r'The Patent Office Journal(No.*Dated)?\s+\d{2}/\d{2}/\d{4}', '', self.text)
        page_number_match = self.page_number_pattern.search(clean_text.strip())
        try:
            number = page_number_match.group(1)
            if as_int:
                return int(number)
            return number
        except AttributeError:
            raise ValueError('Page number not found')
