import shutil
from pathlib import Path


class Zip:
    def __init__(self, id_num: int):
        self.id = str(id_num).zfill(3)
        self.directory_id = Path('../files') / self.id
        self.directory_pdf = self.directory_id / 'pdf'
        self.directory_csv = self.directory_id / 'csv'
        self.validate()

    def zip_dir(self, directory: Path):
        output_filename = str(directory)
        shutil.make_archive(output_filename, 'zip', directory)
        shutil.rmtree(directory)

    def zip_all(self):
        # self.directory_pdf.mkdir()
        # for pdf in self.directory_id.glob('*.pdf'):
        #     shutil.move(pdf, self.directory_pdf)
        # for dir in (self.directory_pdf, self.directory_id):
        #     self.zip_dir(dir)
        self.zip_dir(self.directory_pdf)
        new = Path('../files') / 'new'
        new.mkdir()
        shutil.move(self.directory_id, new)
        shutil.make_archive(str(new), 'zip', new)
        zip_result = Path('../files') / 'new.zip'
        zip_result.rename(self.directory_id.parent / f'{self.id}.zip')
        shutil.rmtree(new)

    def validate(self):
        return True
        # for dir in (self.directory_pdf, self.directory_csv, self.directory_id):
        #     assert dir.exists(), f'{dir} does not exist'


if __name__ == '__main__':
    # for i in range(3, 82):
    #     Zip(i).zip_all()
    zip = Zip(5)
    zip.zip_all()
