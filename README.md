# Web-Scraper

This project is a Scrapy-based web scraper that extracts PDF files from the Pennsylvania government website, processes their content, and stores structured data in a CSV file.

The scraper:

    Extracts PDF links from a webpage.

    Downloads the PDFs (if not already processed).

    Processes the PDF data to extract relevant table information.

    Saves the extracted data into a structured CSV file (webscraper_schedule.csv).

    Logs progress and errors into spider_logs.txt and cron_log.log.

## Project Structure

```
/webscraper
│── scrapy.cfg
│── /webscraper
│   │── /spiders
│   │   │── webscraper_spider.py     # Main Scrapy spider
│   │   │── extract_pdf.py          # PDF processing script
│   │── webscraper_schedule.csv      # Extracted data (output file)
│   │── spider_logs.txt             # Spider logs
│   │── cron_log.log                # Cron job logs
│   │── /pdf_downloads              # Folder for downloaded PDFs
│   |   │── /processed              # Processed PDFs
│── /venv                           # Python virtual environment
│── requirements.txt                # Installation requirements

```

## Installation and Setup

1. Install python

    Check if python is installed
```
python3 --version
```

2. Clone the Repository
```
git clone git@github.com:shrutz510/Web-Scraper.git
cd Web-Scraper
```

4. Create a Virtual Environment
```
python3 -m venv venv
source venv/bin/activate
```

5. Install Dependencies
```
pip install -r requirements.txt
```

### Running the Scraper

1. Run manually
```
source venv/bin/activate
python3 -m scrapy crawl webscraper_spider
```

2. Schedule a cron job

    To run the scraper every Monday at 06:00 AM:
```
crontab -e
00 06 * * 1 cd ~/Web-Scraper && ~/Web-Scraper/venv/bin/python3 -m scrapy crawl webscraper_spider 2>> ~/Web-Scraper/webscraper/cron_log.log
```
