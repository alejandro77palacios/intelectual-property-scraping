import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

url_ipindia = 'https://search.ipindia.gov.in/IPOJournal/Journal/Patent'
path_downloads_directory = '/Users/alejandropalacios/programacion/freelancer/ipindia/files'

downloads_directory = Path(path_downloads_directory)
if not downloads_directory.exists():
    downloads_directory.mkdir()

chrome_options = Options()
chrome_options.add_argument('--verbose')
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": path_downloads_directory,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing_for_trusted_sources_enabled": False,
    "plugins.always_open_pdf_externally": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=chrome_options)
driver.get(url_ipindia)
time.sleep(3)
selector_number_entries = driver.find_element(By.XPATH, '//*[@id="Journal_length"]/label/select')
Select(selector_number_entries).select_by_visible_text('All')

first_row = 52
last_row = 878

table_rows = driver.find_elements(By.CSS_SELECTOR, 'tbody>tr')[first_row - 1:last_row]
for row in table_rows:
    # Serial number
    first_column = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
    serial_number = first_column.text.strip().zfill(3)
    print(f'Current row: {serial_number}\n')
    # Create directory for current row
    row_directory = downloads_directory / serial_number
    if row_directory.exists():
        print(f'Row {serial_number} already exists')
        continue
    else:
        row_directory.mkdir()
    # Download PDFs in current row
    pdf_columns = row.find_elements(By.XPATH, './/td[last()]//button[@type="submit"]')
    for col_num, form_column in enumerate(pdf_columns, start=1):
        file_name = form_column.text.strip()
        print(f'File number {col_num}: {file_name}\n')
        # Download PDF
        form_column.click()
        original_file_path = downloads_directory / 'ViewJournal.pdf'
        # Wait for file to download
        print('Waiting for file to download...')
        time_waited = 0
        while not original_file_path.exists():
            extra_time = 5
            print(f'Total time waited: {time_waited} seconds')
            print(f'We will wait {extra_time} more seconds')
            time_waited += extra_time
            time.sleep(extra_time)
        print('\nSuccess: file downloaded')
        new_file_path = row_directory / f'{file_name}.pdf'
        original_file_path.rename(new_file_path)
        print('-'*30 + '\n')
print('Done!')
driver.quit()
