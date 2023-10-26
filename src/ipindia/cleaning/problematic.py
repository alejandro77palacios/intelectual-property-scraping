import re


class ProblematicFieldsCleaner:
    def __init__(self, detected_pieces):
        self.detected_pieces = detected_pieces
        self.field_cleaning_methods = {
            'international_application_no': self.clean_international_application_no,
            'international_application_date': self.clean_international_application_date,
            'international_publication_no': self.clean_international_publication_no,
            'patent_of_addition_number': self.clean_patent_of_addition_number,
            'patent_of_addition_date': self.clean_patent_of_addition_date,
            'divisional_to_application_number': self.clean_divisional_to_application_number,
            'divisional_to_application_date': self.clean_divisional_to_application_date,
        }

    def clean(self):
        return {field: self.field_cleaning_methods[field]() for field in self.field_cleaning_methods}

    # ------------------------------
    # Clean fields
    # ------------------------------

    def clean_international_application_no(self):
        text = self._find_international_application()
        return self._extract_from_problematic(text, 1, 'Application No')

    def clean_international_application_date(self):
        text = self._find_international_application()
        raw = self._extract_from_problematic(text, 2, 'Filing Date')
        return self._extract_date(raw)

    def clean_international_publication_no(self):
        text = self._find_international_publication()
        return self._extract_from_problematic(text, 1, 'Publication No')

    def clean_patent_of_addition_number(self):
        text = self._find_patent_addition()
        return self._extract_from_problematic(text, 1, 'to Application Number')

    def clean_patent_of_addition_date(self):
        text = self._find_patent_addition()
        raw = self._extract_from_problematic(text, 2, 'Filing Date')
        return self._extract_date(raw)

    def clean_divisional_to_application_number(self):
        text = self._find_divisional_application()
        return self._extract_from_problematic(text, 1, 'Application Number')

    def clean_divisional_to_application_date(self):
        text = self._find_divisional_application()
        raw = self._extract_from_problematic(text, 2, 'Filing Date')
        return self._extract_date(raw)

    # ------------------------------
    # Find fields
    # ------------------------------

    def _find_international_application(self):
        return self._find_field('International', 'Application No')

    def _find_international_publication(self):
        return self._find_field('International', 'Publication No', filing_date=False)

    def _find_patent_addition(self):
        return self._find_field('Patent of Addition', 'Application Number')

    def _find_divisional_application(self):
        return self._find_field('Divisional', 'Application Number')

    # ------------------------------
    # Auxiliary methods
    # ------------------------------
    @staticmethod
    def _extract_from_problematic(text, index_part, string_to_remove):
        if text is None:
            return None
        try:
            clean_text = re.sub(r'\s+', ' ', text)
            target = clean_text.split(':')[index_part]
        except IndexError:
            return None
        if 'NA' in target:
            return None
        return re.sub(string_to_remove, '', target).strip()

    def _find_field(self, first_line, second_line, filing_date=True):
        for piece in self.detected_pieces:
            condition = (first_line in piece) and (second_line in piece)
            if filing_date:
                condition = condition and 'Filing Date' in piece
            if condition:
                return piece
        return None

    @staticmethod
    def _extract_date(text):
        if text is None:
            return None
        try:
            return re.findall(r'\d{2}/\d{2}/\d{4}', text)[0]
        except IndexError:
            return None
