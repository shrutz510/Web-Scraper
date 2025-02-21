import os
import scrapy
from urllib.parse import urljoin
from webscraper.spiders.extract_pdf import extract_pdf_data
from datetime import datetime

class WebScraperSpider(scrapy.Spider):
    name = "webscraper_spider"
    allowed_domains = ["pa.gov"]
    start_urls = [
        "https://www.pa.gov/agencies/dli/programs-services/workers-compensation/wc-health-care-services-review/wc-fee-schedule/part-b-fee-schedules.html"
    ]
    
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    PDF_FOLDER = os.path.join(BASE_DIR, "pdf_downloads")
    PROCESSED_FOLDER = os.path.join(PDF_FOLDER, "processed")
    OUTPUT_CSV = os.path.join(BASE_DIR, "webscraper_schedule.csv")
    LOG_FILE = os.path.join(BASE_DIR, "spider_logs.txt")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(self.PROCESSED_FOLDER, exist_ok=True)
        self.pending_pdfs = 0  
        self.log_message("Spider initialized. Checking for new PDFs.")
        self.process_unprocessed_pdfs()

    def log_message(self, message, final=False):
        """Write log messages to spider_logs.txt."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        if final:
            log_entry += "\n\n"
        else:
            log_entry += "\n" 

        with open(self.LOG_FILE, "a") as log_file:
            log_file.write(log_entry) # Write logs

    def process_unprocessed_pdfs(self):
        """Extract data from existing pdfs."""
        unprocessed_pdfs = [
            f for f in os.listdir(self.PDF_FOLDER) 
            if f.endswith(".pdf")
        ] # Check for unprocessed files in pdf_downloads folder

        if not unprocessed_pdfs:
            self.log_message("No leftover PDFs found for processing.")
            return

        self.log_message(f"Found {len(unprocessed_pdfs)} unprocessed PDFs. Processing now.")

        for pdf_name in unprocessed_pdfs:
            pdf_path = os.path.join(self.PDF_FOLDER, pdf_name)
            processed_path = os.path.join(self.PROCESSED_FOLDER, pdf_name)

            if os.path.exists(processed_path):
                self.log_message(f"Duplicate found: {pdf_name} already processed. Deleting duplicate.") 
                os.remove(pdf_path) # Delete already processed files
            else:
                self.log_message(f"Processing leftover PDF: {pdf_name}")
                extract_pdf_data(pdf_path, pdf_name) # Process pending file
                os.rename(pdf_path, processed_path)
                self.log_message(f"Moved {pdf_name} to {self.PROCESSED_FOLDER}")

    def parse(self, response):
        """Extract PDF links to be downloaded."""
        pdf_links = [
            urljoin(response.url, href) 
            for href in response.css("a::attr(href)").getall() 
            if href.endswith(".pdf")
        ] # Find the pdf links in the url

        self.log_message(f"Found {len(pdf_links)} PDF links on the page.")
        self.pending_pdfs = sum(
            not os.path.exists(os.path.join(self.PDF_FOLDER, os.path.basename(pdf_url))) and
            not os.path.exists(os.path.join(self.PROCESSED_FOLDER, os.path.basename(pdf_url)))
            for pdf_url in pdf_links
        ) # Check for existing pdfs

        if self.pending_pdfs == 0:
            self.log_message("No new PDFs to process.", final=True)
            return

        for pdf_url in pdf_links:
            pdf_name = os.path.basename(pdf_url)
            download_path = os.path.join(self.PDF_FOLDER, pdf_name)
            processed_path = os.path.join(self.PROCESSED_FOLDER, pdf_name)

            if os.path.exists(download_path) or os.path.exists(processed_path):
                self.log_message(f"Skipping (Already Exists): {pdf_name}")
            else:
                self.log_message(f"Downloading: {pdf_name}")
                yield scrapy.Request(url=pdf_url, callback=self.save_pdf, meta={"pdf_name": pdf_name}) # Scrapy response after parsing urls

    def save_pdf(self, response):
        """Download the PDF and process its data."""
        pdf_name = response.meta["pdf_name"]
        pdf_path = os.path.join(self.PDF_FOLDER, pdf_name)
        processed_path = os.path.join(self.PROCESSED_FOLDER, pdf_name)

        with open(pdf_path, "wb") as f:
            f.write(response.body) # Write the contents of the pdf file

        self.log_message(f"Extracting data from {pdf_name}")
        extract_pdf_data(pdf_path, pdf_name) # Get table data for pdf
        os.rename(pdf_path, processed_path) # Move processed file
        self.log_message(f"Moved {pdf_name} to {self.PROCESSED_FOLDER}")
        self.pending_pdfs -= 1
        
        if self.pending_pdfs == 0:
            self.log_message("Finished processing all PDFs.", final=True)