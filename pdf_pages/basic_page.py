"""
Implements the PdfPage class.
"""
import re


class PdfPage:
    """
    A class to represent a PDF page.
    It is intended to be inherited by other classes that represent specific PDF pages.
    """
    page_number_pattern = re.compile(r'(\d{3,})[a-zA-Z\s]*\Z')

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
        page_number_match = self.page_number_pattern.search(self.text)
        try:
            number = page_number_match.group(1)
            if as_int:
                return int(number)
            return number
        except AttributeError:
            return None
