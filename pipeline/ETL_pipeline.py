import requests
import pandas as pd
import logging
import sys
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, String, BigInteger, Text

# Logging to file and console
logging.basicConfig(
    level=logging.INFO, 
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log', mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
# Requesting 10 fields due to API limits
API_URL = 'https://restcountries.com/v3.1/all?fields=name,cca3,currencies,languages,capital,flags,timezones,population,tld,subregion'

def raw_from_api_to_json() -> List[Dict[str, Any]]:
    """
    Extract: Loads country data from the API

    Return: JSON-файл
    """
    try:
        logging.info('Loading data from the API...')
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        message_error = f'API request error: {e}'
        logging.error(message_error)
        raise SystemExit(message_error)
    
def transform_data(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transform: Normalizes nested JSON into flat format for a Pandas DataFrame

    Return: Normalized DataFrame
    """
    logging.info('Data transformation...')
    normalized_records = []

    for country in raw_data:
        try:
            # Handle currencies separately because it requires more code
            currencies_raw: Dict[str, Any] = country.get('currencies', {})
            currencies_str: Optional[str] = None
            if currencies_raw:
                currency_list: List[str] = [f"{info.get('name')} ({code})" for code, info in currencies_raw.items()]
                currencies_str = ', '.join(currency_list)
            
            row = {
                'common_name': country.get('name', {}).get('common', None),
                'country_code': country.get("cca3"),
                'currencies': currencies_str,
                'languages': ', '.join(country.get('languages', {}).values()) if country.get('languages') else None,
                'capital': ', '.join(country.get('capital', [])) if country.get('capital') else None,
                'flag_url_png': country.get('flags', {}).get('png', None),
                'timezone': ", ".join(country.get('timezones', [])) if country.get('timezones') else None,
                'population': country.get('population', None),
                'tld': ', '.join(country.get('tld', [])) if country.get('tld') else None,
                'subregion': country.get('subregion', None),
            }

            normalized_records.append(row)
        except Exception as e:
            logging.error(f"Error processing country data {country.get('name', {}).get('common', 'Unknown')}: {e}")
            continue

    df = pd.DataFrame(normalized_records)
    logging.info(f'Transformation JSON -> Dataframe complete. Rows: {len(df)}')
    return df


def save_to_database(df: pd.DataFrame) -> bool:
    """
    Load: Saving data in PostgreSQL
    
    Returns: True if successful, False otherwise
    """
    if df.empty:
        logging.warning("DataFrame is empty, saving to database was skipped.")
        return False

    try:
        # Connecting to the database
        DB_URL = "postgresql://user:password@localhost:5432/countries_db"
        engine = create_engine(DB_URL)

        logging.info("Saving data to the database...")
        # Use "with" to close the connection automatically
        with engine.connect() as con:
            df.to_sql(
                "countries", 
                con, 
                if_exists="replace", 
                index=False,
                dtype={
                    "country_code": String(3),
                    "common_name": String(100),
                    "capital": String(100),
                    "population": BigInteger(),
                    "subregion": String(100),
                    "currencies": Text(),
                    "languages": Text(),
                    "flag_url_png": Text(),
                    "timezone": Text(),
                    "tld": String(50)
                }
            )
        logging.info("The data has been successfully saved to the table 'countries'.")
        return True
    except Exception as e:
        logging.error(f"Error saving to DB: {e}")
        return False


def run_pipeline() -> None:
    """
    The main function for running all stages of the pipeline
    """
    #Extract
    raw_data = raw_from_api_to_json()
    #Transform
    df = transform_data(raw_data)
    #Load
    save_to_database(df)

if __name__ == '__main__':
    run_pipeline()