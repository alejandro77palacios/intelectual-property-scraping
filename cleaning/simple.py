import re


class SimpleFieldsCleaner:
    def __init__(self, detected_pieces):
        self.detected_pieces = detected_pieces
        self.field_cleaning_methods = {
            'Application No.': self.clean_application_no,
            'Date of filing of Application': self.clean_date_of_filing,
            'Publication Date': self.clean_publication_date,
            'Title of the invention': self.clean_title_of_the_invention,
            'International\nclassification': self.clean_international_classification,
            'Abstract': self.clean_abstract,
        }
        self.people_cleaning_methods = {
            'Name of Applicant': self.clean_name_of_applicant,
            'Name of Inventor': self.clean_name_of_inventor,
        }
        self.subfield_cleaning_methods = {
            'no_pages': self.clean_no_pages,
            'no_claims': self.clean_no_claims,
        }
        self.raw_data = {}
        self.clean_data = {}

    def clean(self):
        self.find_all_data()
        self.preprocess_fields()
        self.clean_fields()
        return self.clean_data

    def find_all_data(self):
        self.raw_data = {field: self._find_field_data(field) for field in self.field_cleaning_methods}

    def preprocess_fields(self):
        self.raw_data = {field: self.remove_field_from_data(field) for field in self.field_cleaning_methods}

    def clean_fields(self):
        fields_data = {field: self.field_cleaning_methods[field]() for field in self.field_cleaning_methods}
        people_data = {field: self.people_cleaning_methods[field]() for field in self.people_cleaning_methods}
        subfields_data = {sub: self.subfield_cleaning_methods[sub]() for sub in self.subfield_cleaning_methods}
        self.clean_data = {**fields_data, **subfields_data, **people_data}

    # ------------------------------
    # Cleaning main fields
    # ------------------------------

    def clean_application_no(self):
        text = self.raw_data['Application No.']
        return self._safe_extract(text, r'\d{5,}')

    def clean_date_of_filing(self):
        text = self.raw_data['Date of filing of Application']
        return self._safe_extract(text, r'(\d{2}/\d{2}/\d{4})')

    def clean_publication_date(self):
        text = self.raw_data['Publication Date']
        return self._safe_extract(text, r'(\d{2}/\d{2}/\d{4})')

    def clean_title_of_the_invention(self):
        text = self.raw_data['Title of the invention']
        return re.sub('\s+', ' ', text)

    def clean_international_classification(self):
        text = self.raw_data['International\nclassification']
        if text is None:
            return None
        clean_codes = [code.strip() for code in text.split(',')]
        return ', '.join(clean_codes)

    def clean_abstract(self):
        text = self.raw_data['Abstract']
        first_part = text.split('No. of Pages')[0].strip()
        cleaned = re.sub(r'^Abstract[\s.,:]*', '', first_part, flags=re.IGNORECASE)
        return re.sub(r'\s+', ' ', cleaned).strip()

    # ------------------------------
    # Cleaning people fields
    # ------------------------------

    def clean_name_of_applicant(self):
        all_applicants = self._process_people('Name of Applicant')
        return self._re_structure_people(all_applicants)

    def clean_name_of_inventor(self):
        all_applicants = self._process_people('Name of Inventor')
        return self._re_structure_people(all_applicants)

    def _process_people(self, people_field: str):
        list_people = re.split(r'\d+\)\s*', self._find_field_data(people_field))[1:]
        values = []
        for person in list_people:
            all_data = [re.sub(r'\s', ' ', p).strip() for p in person.split('Address of Applicant')]
            if len(all_data) >= 2:
                name, address = all_data[:2]
                name = re.sub(r'\s*:\s*NA\s*', ' ', name)
                name = re.split(r'[-–]{4,}', name)[0].strip()
                name = re.split(r':', name)[0].strip()
                address = re.split(r'[-–]{4,}', address)[0]
                address = re.sub(r':', ' ', address).strip()
                values.append((name, address))
            elif len(all_data) == 1:
                name = all_data[0]
                values.append((name, None))
            else:
                values.append((None, None))
        return values

    def _re_structure_people(self, all_people):
        app_key = 'Application No.'
        return [{'name': name, 'address': address, app_key: self.clean_application_no()} for name, address in
                all_people]

    # ------------------------------
    # Sub fields
    # ------------------------------

    def clean_no_pages(self):
        return self._clean_subfield_abstract(r'No\. of Pages\s*:\s*(\d+)')

    def clean_no_claims(self):
        return self._clean_subfield_abstract(r'No\. of Claims\s*:\s*(\d+)')

    def _clean_subfield_abstract(self, pattern):
        match = re.search(pattern, self.raw_data['Abstract'])
        return match.group(1) if match else None

    # ------------------------------
    # Auxiliary methods
    # ------------------------------

    def remove_field_from_data(self, field):
        extra_characters = r'[\s.,:]*'
        pattern_to_remove = extra_characters + field + extra_characters
        try:
            return re.sub(pattern_to_remove, '', self.raw_data[field]).strip()
        except TypeError:
            return self.raw_data[field]

    @staticmethod
    def _safe_extract(texto, pattern):
        match = re.search(pattern, texto)
        return match.group(0) if match else None

    def _find_field_data(self, field: str):
        for piece in self.detected_pieces:
            if field in piece:
                return re.sub(r'^[\s.,:]*', '', piece).strip()
        return None
