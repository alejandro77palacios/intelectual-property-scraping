from pathlib import Path

from ipindia.date_processor import DateProcessor

year_path = Path('2005')
date_directories = sorted(item for item in year_path.iterdir() if item.is_dir())
for date_directory in date_directories[:]:
    print(f'-----Processing {date_directory}-----')
    processor = DateProcessor(date_directory)
    processor.export_data()
