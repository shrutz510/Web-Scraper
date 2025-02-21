import os
import pdfplumber
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
OUTPUT_CSV = os.path.join(BASE_DIR, "webscraper_schedule.csv")

HEADER = [
    "ID",  
    "CPT/HCPC Code", 
    "Modifier", 
    "Medicare Location", 
    "Global Surgery Indicator",
    "Multiple Surgery Indicator", 
    "Prevailing Charge Amount", 
    "Fee Schedule Amount", 
    "Site of Service Amount", 
    "PDF Name", 
    "Timestamp"
]

def load_existing_data():
    """Load existing CSV data."""
    if os.path.exists(OUTPUT_CSV):
        df = pd.read_csv(OUTPUT_CSV) # Read data in webscraper_schedule.csv
        existing_pdfs = set(df["PDF Name"]) if "PDF Name" in df else set() # Create a set of all PDFs that have already been parsed
    else:
        df = pd.DataFrame(columns=HEADER) # Create new dataframe
        existing_pdfs = set()

    return df, existing_pdfs

def append_data(existing_df, new_data):
    """Append new data to the CSV file."""
    if not new_data:
        print("No new data to append.")
        return
    
    new_df = pd.DataFrame(new_data, columns=HEADER[1:])  # New data to be inserted into csv
    new_df.insert(0, "ID", range(len(existing_df), len(existing_df) + len(new_df)))  
    key_columns = HEADER[1:-1] # Get all columns except ID and Timestamp
    combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=key_columns) # Check for any duplicate entries
    combined_df.to_csv(OUTPUT_CSV, index=False) # Save data to csv
    print(f"Successfully appended {len(new_df)} new records to {OUTPUT_CSV}")

def extract_pdf_data(pdf_path, pdf_name):
    """Extract table data from a PDF."""
    existing_df, existing_pdfs = load_existing_data()  # Load csv data

    if pdf_name in existing_pdfs:
        print(f"Skipping extraction for {pdf_name} (already processed).") # Pass over already processed files
        return  

    new_data = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Get date & time

    HEADER_KEYWORDS = {
        "CPT/HCPC Code", "Modifier", "Medicare Location",
        "Global Surgery Indicator", "Multiple Surgery Indicator",
        "Prevailing Charge Amount", "Fee Schedule Amount",
        "Site of Service Amount"
    } # Define header keywords to skip

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:  
            table = page.extract_table() # Extract the table from the pdf using pdfplumber
            if table:
                header = table[0] # Exclude the first row which is the header
                for row in table[1:]:  
                    row_text = " ".join(str(cell).strip().lower() for cell in row if cell) # Check for any headers that don't fit the norm
                    if any(header.lower() in row_text for header in HEADER_KEYWORDS):
                        print(f"Skipping header row in {pdf_name}: {row}") # Pass over remaining headers 
                        continue
                    if len(row) >= 8 and row != header:  
                        new_data.append(row[:8] + [pdf_name, timestamp]) # Append new data

    if new_data:
        append_data(existing_df, new_data) 
