import psutil
import logging
import pandas as pd
from datetime import datetime
from db.models import get_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/db_insert.log'),
        logging.StreamHandler()
    ]
)

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean the NAV data before insertion.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing NAV data
        
    Returns:
        pd.DataFrame: Cleaned and validated DataFrame
    """
    if df.empty:
        raise ValueError("Empty DataFrame received")
    
    # Check if first row contains header values
    if df.iloc[0, 0] == 'Scheme Code':
        df = df.iloc[1:].reset_index(drop=True)
        logging.warning("Header row detected and removed")
    
    # Validate required columns
    required_columns = ['Scheme Code', 'Scheme Name', 'Net Asset Value', 'Date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Convert data types and handle invalid values
    try:
        # Convert NAV to numeric, handling non-numeric values
        df['Net Asset Value'] = pd.to_numeric(df['Net Asset Value'], errors='coerce')
        
        # Log rows with invalid NAV values
        invalid_nav_rows = df[df['Net Asset Value'].isna()]
        if not invalid_nav_rows.empty:
            logging.warning(f"Found {len(invalid_nav_rows)} rows with invalid NAV values")
            for idx, row in invalid_nav_rows.iterrows():
                logging.warning(f"Row {idx}: Invalid NAV value '{row['Net Asset Value']}' for scheme {row['Scheme Name']}")
        
        # Remove rows with invalid NAV values
        df = df.dropna(subset=['Net Asset Value'])
        
        # Convert date to datetime
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y', errors='coerce')
        
        # Log rows with invalid dates
        invalid_date_rows = df[df['Date'].isna()]
        if not invalid_date_rows.empty:
            logging.warning(f"Found {len(invalid_date_rows)} rows with invalid dates")
            for idx, row in invalid_date_rows.iterrows():
                logging.warning(f"Row {idx}: Invalid date '{row['Date']}' for scheme {row['Scheme Name']}")
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['Date'])
        
        # Ensure NAV values are within valid range for DECIMAL(10,4)
        max_nav = 999999.9999
        invalid_range_rows = df[df['Net Asset Value'] > max_nav]
        if not invalid_range_rows.empty:
            logging.warning(f"Found {len(invalid_range_rows)} rows with NAV values exceeding {max_nav}")
            for idx, row in invalid_range_rows.iterrows():
                logging.warning(f"Row {idx}: NAV value {row['Net Asset Value']} exceeds maximum allowed value for scheme {row['Scheme Name']}")
        
        # Remove rows with NAV values exceeding maximum
        df = df[df['Net Asset Value'] <= max_nav]
        
        # Round NAV values to 4 decimal places
        df['Net Asset Value'] = df['Net Asset Value'].round(4)
        
        # Log summary of validation
        logging.info(f"Data validation complete. Remaining rows: {len(df)}")
        if len(df) > 0:
            logging.info(f"Sample of first row after validation: {df.iloc[0].to_dict()}")
        
    except Exception as e:
        logging.error(f"Error during data validation: {str(e)}")
        logging.error(f"Error converting data types: {str(e)}")
        return False
    
    # Remove rows with invalid data
    invalid_rows = df[df['Net Asset Value'].isna() | df['Date'].isna()]
    if not invalid_rows.empty:
        logging.warning(f"Found {len(invalid_rows)} rows with invalid data. Removing...")
        df = df.dropna(subset=['Net Asset Value', 'Date'])
    
    return df

def insert_nav(df):
    # Validate and clean data
    df = validate_data(df)
    if df is False:
        logging.error("Data validation failed. Aborting insertion.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # First, let's check how many rows already exist for these scheme_code and nav_date combinations
    check_sql = """
        SELECT scheme_code, nav_date 
        FROM nav_data 
        WHERE (scheme_code, nav_date) IN (%s)
    """
    
    insert_sql = """
        INSERT INTO nav_data (
            scheme_type, scheme_category, scheme_sub_category, scheme_code,
            isin_growth, isin_reinv, scheme_name, nav, nav_date, fund_structure
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nav = VALUES(nav),
            scheme_name = VALUES(scheme_name),
            fund_structure = VALUES(fund_structure)
    """

    # Log start of insertion process
    logging.info(f"Starting data insertion process. Total rows to process: {len(df)}")
    logging.info(f"First row sample: {df.iloc[0].to_dict() if not df.empty else 'No data'}")

    # Prepare rows for insertion
    rows = []
    for _, row in df.iterrows():
        try:
            rows.append((
                row.get('Scheme Type', ''),
                row.get('Scheme Category', ''),
                row.get('Scheme Sub-Category', ''),
                row['Scheme Code'],
                row.get('ISIN Div Payout/ISIN Growth', ''),
                row.get('ISIN Div Reinvestment', ''),
                row.get('Scheme Name', ''),
                float(row['Net Asset Value']),
                row['Date'].strftime('%Y-%m-%d'),
                row.get('Fund Structure', '')
            ))
        except Exception as e:
            logging.error(f"Error processing row: {str(e)}")
            continue

    if not rows:
        logging.error("No valid rows to insert after processing")
        return

    total_memory = psutil.virtual_memory().available
    estimated_row_size = 1000  # bytes per row estimate
    chunk_size = max(
        500, min(len(rows), total_memory // estimated_row_size // 2))
    
    logging.info(f"Using chunk size of {chunk_size} rows")

    total_inserted = 0
    total_updated = 0
    start_time = datetime.now()

    try:
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i+chunk_size]
            try:
                # Execute the insert
                cursor.executemany(insert_sql, chunk)
                conn.commit()
                
                # Get the number of affected rows
                affected_rows = cursor.rowcount
                
                # For ON DUPLICATE KEY UPDATE:
                # - If a row is inserted, it counts as 1
                # - If a row is updated, it counts as 2
                inserted = sum(1 for _ in chunk if cursor.rowcount == 1)
                updated = sum(1 for _ in chunk if cursor.rowcount == 2)
                
                total_inserted += inserted
                total_updated += updated
                
                logging.info(
                    f"Chunk {i//chunk_size + 1}: "
                    f"Affected rows: {affected_rows}, "
                    f"Inserted: {inserted}, "
                    f"Updated: {updated}"
                )
                
            except Exception as chunk_error:
                logging.error(f"Error processing chunk {i//chunk_size + 1}: {str(chunk_error)}")
                conn.rollback()
                raise

        # Log final results
        duration = (datetime.now() - start_time).total_seconds()
        logging.info(
            f"Insertion completed. "
            f"Total rows processed: {len(rows)}, "
            f"Inserted: {total_inserted}, "
            f"Updated: {total_updated}, "
            f"Duration: {duration:.2f} seconds"
        )

    except Exception as e:
        conn.rollback()
        logging.error(f"Fatal error during insertion: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()
        logging.info("Database connection closed")

def get_earliest_nav_date() -> datetime:
    """
    Get the earliest NAV date from the database.
    
    Returns:
        datetime: The earliest date found in the database, or None if no data exists
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT MIN(nav_date) FROM nav_data"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        if result:
            logging.info(f"Earliest NAV date in database: {result}")
            return result
        else:
            logging.warning("No NAV data found in database")
            return None
            
    except Exception as e:
        logging.error(f"Error getting earliest NAV date: {str(e)}")
        raise
