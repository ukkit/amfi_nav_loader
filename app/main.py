from downloader.download_nav import download_nav_file_for_date, get_latest_business_day, bulk_download_past_years, bulk_download_past_months
from parser.parse_nav import parse_nav_file
from db.insert_nav import insert_nav, get_earliest_nav_date
from datetime import datetime, timedelta
import logging
import os
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monthly_job.log'),
        logging.StreamHandler()
    ]
)

def run_daily_job():
    try:
        date = get_latest_business_day(datetime.now())
        file_path = download_nav_file_for_date(date)
        df = parse_nav_file(file_path)
        df.to_csv("nav_data.csv", index=False)
        insert_nav(df)
        print("NAV data updated successfully.")
    except Exception as e:
        with open("logs/error_log.txt", "a") as log:
            log.write(f"{datetime.now()} - Error: {e}\n")

def run_monthly_job(months: int = 3):
    """
    Run the monthly job to download and process NAV data.
    
    Args:
        months (int): Number of months to process. Default is 3 months.
    """
    start_time = datetime.now()
    logging.info(f"Starting monthly job for {months} months")
    
    try:
        # Get the earliest date from database
        earliest_date = get_earliest_nav_date()
        if earliest_date:
            # Calculate the date range
            end_date = earliest_date - timedelta(days=1)  # One day before earliest date
            start_date = end_date - timedelta(days=months*30)  # months ago
            
            logging.info(f"Processing data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Download NAV files
            downloaded_files = bulk_download_past_months(months, start_date=start_date, end_date=end_date)
            if not downloaded_files:
                logging.warning("No files were downloaded")
                return
                
            logging.info(f"Downloaded {len(downloaded_files)} files")
            
            # Process each downloaded file
            success_count = 0
            failed_count = 0
            failed_files = []
            
            for file_path in downloaded_files:
                try:
                    logging.info(f"Processing file: {file_path}")
                    
                    # Parse the NAV file
                    df = parse_nav_file(file_path)
                    if df is None or df.empty:
                        logging.warning(f"No data found in file: {file_path}")
                        continue
                    
                    # Save parsed data to CSV (for backup/verification)
                    csv_path = file_path.replace('.txt', '.csv')
                    df.to_csv(csv_path, index=False)
                    logging.info(f"Saved parsed data to: {csv_path}")
                    
                    # Insert data into database
                    insert_nav(df)  # Pass the DataFrame directly
                    success_count += 1
                    logging.info(f"Successfully processed: {file_path}")
                    
                except Exception as e:
                    failed_count += 1
                    failed_files.append(file_path)
                    logging.error(f"Error processing {file_path}: {str(e)}")
            
            # Print summary
            duration = datetime.now() - start_time
            logging.info("\nMonthly Job Summary:")
            logging.info(f"Total files processed: {len(downloaded_files)}")
            logging.info(f"Successfully processed: {success_count}")
            logging.info(f"Failed to process: {failed_count}")
            if failed_files:
                logging.info("Failed files:")
                for file in failed_files:
                    logging.info(f"  - {file}")
            logging.info(f"Total duration: {duration}")
            
        else:
            logging.info("No existing data in database. Processing default date range.")
            # If no data exists, use the default behavior
            downloaded_files = bulk_download_past_months(months)
            if not downloaded_files:
                logging.warning("No files were downloaded")
                return
                
            logging.info(f"Downloaded {len(downloaded_files)} files")
            
            # Process each downloaded file
            success_count = 0
            failed_count = 0
            failed_files = []
            
            for file_path in downloaded_files:
                try:
                    logging.info(f"Processing file: {file_path}")
                    
                    # Parse the NAV file
                    df = parse_nav_file(file_path)
                    if df is None or df.empty:
                        logging.warning(f"No data found in file: {file_path}")
                        continue
                    
                    # Save parsed data to CSV (for backup/verification)
                    csv_path = file_path.replace('.txt', '.csv')
                    df.to_csv(csv_path, index=False)
                    logging.info(f"Saved parsed data to: {csv_path}")
                    
                    # Insert data into database
                    insert_nav(df)  # Pass the DataFrame directly
                    success_count += 1
                    logging.info(f"Successfully processed: {file_path}")
                    
                except Exception as e:
                    failed_count += 1
                    failed_files.append(file_path)
                    logging.error(f"Error processing {file_path}: {str(e)}")
            
            # Print summary
            duration = datetime.now() - start_time
            logging.info("\nMonthly Job Summary:")
            logging.info(f"Total files processed: {len(downloaded_files)}")
            logging.info(f"Successfully processed: {success_count}")
            logging.info(f"Failed to process: {failed_count}")
            if failed_files:
                logging.info("Failed files:")
                for file in failed_files:
                    logging.info(f"  - {file}")
            logging.info(f"Total duration: {duration}")
            
    except Exception as e:
        logging.error(f"Error in monthly job: {str(e)}")
        raise
    finally:
        # Clean up temporary CSV files
        try:
            for file_path in downloaded_files:
                csv_path = file_path.replace('.txt', '.csv')
                if os.path.exists(csv_path):
                    os.remove(csv_path)
                    logging.info(f"Cleaned up temporary file: {csv_path}")
        except Exception as e:
            logging.error(f"Error cleaning up temporary files: {str(e)}")
        
        logging.info("Monthly job completed")

if __name__ == "__main__":
    # run_daily_job()
    
    # Uncomment below to run historical download
    # from downloader.download_nav import bulk_download_past_years
    # bulk_download_past_years(15)
    
    # Run monthly job for past 3 months
    run_monthly_job(1)
