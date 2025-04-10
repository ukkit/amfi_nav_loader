import requests
import os
from datetime import datetime, timedelta
from config.settings import NAVALL_BASE_URL


def get_latest_business_day(reference_date: datetime) -> datetime:
    date = reference_date - timedelta(days=1)
    while date.weekday() >= 5:  # Saturday=5, Sunday=6
        date -= timedelta(days=1)
    return date


def download_nav_file_for_date(date: datetime):
    nav_date = date.strftime('%d-%b-%Y')  # Format: 02-Apr-2025
    url = NAVALL_BASE_URL.format(nav_date, nav_date)
    response = requests.get(url)
    if response.status_code == 200 and any(char.isdigit() for char in response.text):
        file_path = f"data/navall_{date.strftime('%Y-%m-%d')}.txt"
        os.makedirs("data", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path
    else:
        raise Exception(
            f"Failed to download file. Status code: {response.status_code}")


def bulk_download_past_months(months: int = 3, start_date: datetime = None, end_date: datetime = None):
    """
    Download NAV data for the specified number of past months.
    
    Args:
        months (int): Number of past months to download data for. Default is 3 months.
        start_date (datetime): Optional start date for downloading. If not provided, will be calculated.
        end_date (datetime): Optional end date for downloading. If not provided, will be calculated.
    
    Returns:
        list: List of successfully downloaded file paths
    """
    # If dates are not provided, calculate them
    if not end_date:
        end_date = get_latest_business_day(datetime.now())
    if not start_date:
        start_date = end_date - timedelta(days=months*30)  # Approximate start date
    
    downloaded_files = []
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Calculate total business days to process
    current_date = end_date
    while current_date >= start_date:
        if current_date.weekday() < 5:  # Only weekdays
            file_path = f"data/navall_{current_date.strftime('%Y-%m-%d')}.txt"
            
            # Skip if file already exists
            if not os.path.exists(file_path):
                try:
                    print(f"Downloading NAV data for {current_date.strftime('%Y-%m-%d')}...")
                    download_nav_file_for_date(current_date)
                    downloaded_files.append(file_path)
                    print(f"Successfully downloaded: {file_path}")
                except Exception as e:
                    print(f"Failed to download for {current_date.strftime('%Y-%m-%d')}: {e}")
            else:
                print(f"File already exists: {file_path}")
                downloaded_files.append(file_path)
        
        current_date -= timedelta(days=1)
    
    # Print summary
    print(f"\nDownload Summary:")
    print(f"Start date: {start_date.strftime('%Y-%m-%d')}")
    print(f"End date: {end_date.strftime('%Y-%m-%d')}")
    print(f"Total files downloaded: {len(downloaded_files)}")
    
    return downloaded_files


def bulk_download_past_years(years: int = 15):
    today = datetime.now()
    for i in range(years * 365):
        date = today - timedelta(days=i)
        if date.weekday() >= 5:  # Skip weekends
            continue
        file_path = f"data/navall_{date.strftime('%Y-%m-%d')}.txt"
        if not os.path.exists(file_path):
            try:
                print(f"Downloading for {date.strftime('%Y-%m-%d')}...")
                download_nav_file_for_date(date)
            except Exception as e:
                print(f"Failed for {date.strftime('%Y-%m-%d')}: {e}")
