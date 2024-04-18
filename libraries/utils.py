import os
import re
import zipfile
from datetime import datetime
import logging
from RPA.HTTP import HTTP

def zip_files(directory, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

def initialize_directories(base_path='images'):
    """Ensure the directory exists for image downloads."""
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    return base_path

def download_image(url, download_path):
    """Download images using RPA.HTTP and return the local path."""
    http = HTTP()
    filename = url.split('/')[-1].split('?')[0]  # Basic cleaning to remove URL parameters
    filepath = os.path.join(download_path, filename)
    http.download(url, filepath)
    return filepath

def get_previous_months(n=0):
    """Calculate month names and years for the past 'n' months."""
    try:
        n = max(n, 1)
    except:
        n = 1
    current_date = datetime.now()
    months = []
    for _ in range(n):
        months.append((str(current_date.strftime('%B'))[:3], str(current_date.year)))
        if current_date.month == 1:
            current_date = current_date.replace(month=12, year=current_date.year-1)
        else:
            current_date = current_date.replace(month=current_date.month-1)
    
    return months

def has_money(text):
    """Select a news topic based on the specified option."""
    money_pattern = re.compile(r"\$[0-9]{1,3}(,[0-9]{3})*(\.[0-9]{0,2})? | [0-9]+(?:\s(?:dollars|USD))")
    return bool(money_pattern.search(text))
