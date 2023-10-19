"""
This script implements a class which handle the logic to download all the PDF files from the IPIndia website.
"""
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class DownloaderDriver:
    """
    Class to download files from a web table using Selenium WebDriver.
    It handles the download of all the PDF files.
    """
    url_ipindia = 'https://search.ipindia.gov.in/IPOJournal/Journal/Patent'
    path_downloads_directory = '/Users/alejandropalacios/programacion/freelancer/ipindia/files'
    downloads_directory = Path(path_downloads_directory)

    def __init__(self, first_record=1, last_record=878):
        """
        Parameters
        ----------
        first_record: int, optional
            The first record to download. The default is 1.
        last_record: int, optional
            The last record to download. The default is 878.
        """
        self.driver = webdriver.Chrome(options=self.prepare_options())
        self.first_record = first_record
        self.last_record = last_record
        if not self.downloads_directory.exists():
            self.downloads_directory.mkdir()

    def download_records(self):
        """
        Main method. Download records from a web table.

        This method downloads the records from a web table using Selenium WebDriver.
        It loops through the specified range of records and calls the _download_record method for each record.
        If a file already exists for a record, it skips the download and continues to the next record.
        Finally, it quits the WebDriver.
        """
        table_records = self.driver.find_elements(By.CSS_SELECTOR, 'tbody>tr')[self.first_record - 1:self.last_record]
        for record in table_records:
            try:
                self._download_record(record)
            except FileExistsError:
                continue
        print('Done!')
        self.driver.quit()

    def _download_record(self, record):
        """
        Detects the serial number of the record, creates a directory for the record, and downloads its PDFs.

        Parameters
        ----------
        record : WebElement
            The WebElement containing the record to be downloaded.
        """
        first_field = record.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
        serial_number = first_field.text.strip().zfill(3)
        print(f'Current row: {serial_number}\n')
        record_directory = self.prepare_record_directory(serial_number)
        pdf_links = record.find_elements(By.XPATH, './/td[last()]//button[@type="submit"]')
        for pdf_counter, pdf_element in enumerate(pdf_links, start=1):
            print(f'File number {pdf_counter}\n')
            self.process_pdf_element(pdf_element, record_directory)
            print('-' * 30 + '\n')

    def prepare_record_directory(self, serial_num: str):
        """
        Creates the directory for the given record through its serial number.

        Parameters
        ----------
        serial_num: str
            The serial number used to create the record directory.

        Returns
        -------
        directory: pathlib.Path
            The created record directory.

        Raises
        ------
        FileExistsError
            If the directory for the given serial number already exists.
        """
        assert len(serial_num) == 3, 'The serial number must have 3 digits'
        directory = self.downloads_directory / serial_num / 'pdf'
        if directory.exists():
            print(f'Row {serial_num} already exists')
            raise FileExistsError
        else:
            directory.mkdir(parents=True)
        return directory

    @staticmethod
    def show_waiting_time(path_download):
        """
        Show the waiting time for a file to download.

        Parameters
        ----------
        path_download : str or pathlib.Path
            The path of the file which is expected to be downloaded.

        """
        print('Waiting for file to download...')
        time_waited = 0
        while not path_download.exists():
            extra_time = 5
            print(f'Total time waited: {time_waited} seconds')
            print(f'We will wait {extra_time} more seconds')
            time_waited += extra_time
            time.sleep(extra_time)

    def download_pdf(self, download_element):
        """
        Download a PDF file.

        Parameters
        ----------
        download_element : WebElement
            The web element that represents the download button for the specific PDF.

        Returns
        ----------
        pdf_file : Path
            The path to the downloaded PDF file.

        """
        download_element.click()
        pdf_file = self.downloads_directory / 'ViewJournal.pdf'
        self.show_waiting_time(pdf_file)
        print('\nSuccess: file downloaded')
        return pdf_file

    def process_pdf_element(self, element, directory):
        """
        Get the name of the PDF file, download it and move it to the specified directory.

        Parameters
        ----------
        element : WebElement
            The element containing the name of the PDF file to download.

        directory : Path
            The directory where the downloaded PDF file will be saved.

        """
        file_name = element.text.strip()
        print(f'File name: {file_name}')
        pdf_file = self.download_pdf(element)
        new_file_path = directory / f'{file_name}.pdf'
        pdf_file.rename(new_file_path)

    def visit_ipindia(self):
        """
        Visits the IPIndia website using a Selenium webdriver and shows all the records.
        """
        self.driver.get(self.url_ipindia)
        time.sleep(3)
        selector_number_entries = self.driver.find_element(By.XPATH, '//*[@id="Journal_length"]/label/select')
        Select(selector_number_entries).select_by_visible_text('All')

    def prepare_options(self):
        """
        Prepares and returns Chrome options for the WebDriver.
        It sets various configuration options for the Chrome browser, so that the download process doesn't
        show any pop-up window.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--verbose')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.path_downloads_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "plugins.always_open_pdf_externally": True,
            "safebrowsing.enabled": True
        })
        return chrome_options


if __name__ == '__main__':
    downloader = DownloaderDriver(first_record=136, last_record=878)
    downloader.visit_ipindia()
    downloader.download_records()
