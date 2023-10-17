import re


def extract_data(text: str):
    extractor = Extractor(text)
    return extractor.clean_data()


class Extractor:
    fields = {
        'application_no': 'Application No.',
        'date_of_filing': 'Date of filing of Application',
        'publication_date': 'Publication Date',
        'title_of_the_invention': 'Title of the invention',
        'international_classification': 'International\nclassification',  # process
        # international application no it's always empty
        # international publication no it's always empty
        'patent_of_addition': 'Patent of Addition',  # process something like: 01/01/1900
        # divisional_to_application it's always empty
        'name_of_applicant': 'Name of Applicant',
        'name_of_inventor': 'Name of Inventor',
        'abstract': 'Abstract',
    }
    separation_pattern = r'\(\d{1,2}\)'

    def __init__(self, text: str):
        self.text = text
        self.pieces = re.split(self.separation_pattern, self.text)[1:]
        self.data = {key: self.find_info(key) for key in self.fields}

    def find_info(self, field_key: str):
        field = self.fields[field_key]
        for piece in self.pieces:
            if field in piece:
                info = piece.replace(self.fields[field_key], '')
                return re.sub(r'^[\s.,:]*', '', info).strip()
        return None

    def process_people(self, people_key: str):
        assert people_key in ('name_of_applicant', 'name_of_inventor')
        list_people = re.split(r'\d+\)\s*', self.data[people_key])[1:]
        result = []
        for person in list_people:
            name = person.split('Address of Applicant')[0].strip()
            clean_name = re.sub(r'\s', ' ', name)
            result.append(clean_name)
        return result

    def process_application_no(self):
        return re.findall(r'\d{3,}', self.data['application_no'])[0]

    def process_abstract(self):
        return self.data['abstract'].split('No. of Pages')[0].strip()

    def clean_data(self):
        result = {}
        for key in self.fields:
            print(f'Field: {self.fields[key]}')
            if key == 'application_no':
                info = self.process_application_no()
            elif key in ('name_of_applicant', 'name_of_inventor'):
                info = self.process_people(key)
            else:
                info = self.data[key]
            result[key] = info
            print(info, end='\n' + '-' * 30 + '\n\n')
        return result
