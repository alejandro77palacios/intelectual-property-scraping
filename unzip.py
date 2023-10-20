import shutil
from pathlib import Path


class UnZip:
    def __init__(self, id_num: int):
        self.id = str(id_num).zfill(3)
        self.id_zip = (Path('files') / self.id).with_suffix('.zip')
        self.id_dir = self.id_zip.parent / self.id
        self.pdf_zip = (self.id_dir / 'pdf').with_suffix('.zip')
        self.csv_zip = (self.id_dir / 'csv').with_suffix('.zip')
        self.validate()

    @staticmethod
    def unzip_file(zip_file: Path, main_directory=False):
        if main_directory:
            target_dir = zip_file.parent
        else:
            target_dir = zip_file.with_suffix('')
            target_dir.mkdir()
        shutil.unpack_archive(zip_file, target_dir, 'zip')
        macosx_path = target_dir / '__MACOSX'
        if macosx_path.exists():
            shutil.rmtree(macosx_path)
        zip_file.unlink()

    def unzip_all(self):
        self.unzip_file(self.id_zip, main_directory=True)
        for file in (self.pdf_zip, self.csv_zip):
            self.unzip_file(file)

    def validate(self):
        assert self.id_zip.exists(), f'{self.id_zip} does not exist'


if __name__ == '__main__':
    unzip = UnZip(5)
    unzip.unzip_all()
