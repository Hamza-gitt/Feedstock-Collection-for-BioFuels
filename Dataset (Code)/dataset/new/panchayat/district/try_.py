import pandas as pd
import requests
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the Excel file
file_path = 'farmer_panchayat-try.xlsx'  # Change this to your file path
df = pd.read_excel(file_path)

# Initialize columns for Latitude and Longitude
df['Latitude'] = None
df['Longitude'] = None

# Define a more robust function to query Nominatim API with error handling and retry logic
def get_lat_long_retry(panchayat, block, district, retries=5, backoff_factor=1):
    address = f"{panchayat}, {block}, {district}, Haryana, India"
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyGeoApp/1.0; +http://mygeoapp.com)'}
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                if response.text.strip():
                    response_json = response.json()
                    if response_json:
                        return response_json[0]['lat'], response_json[0]['lon']
                else:
                    logging.warning(f"Empty response for {address}")
            else:
                logging.warning(f"Non-200 status code {response.status_code} for {address}")
        except requests.ConnectionError as e:
            logging.warning(f"Connection error for {address}: {e}")
        except requests.Timeout as e:
            logging.warning(f"Timeout error for {address}: {e}")
        except requests.RequestException as e:
            logging.error(f"Request error for {address}: {e}")
        except ValueError as e:
            logging.error(f"Error parsing JSON response for {address}: {e}")
        
        time.sleep(backoff_factor * (2 ** attempt))  # Exponential backoff
    return None, None

# Query Nominatim API for each panchayat with retries
for index, row in df.iterrows():
    panchayat = row['Gram Panchayat & Equivalent']
    block = row['Panchayat_Block']
    district = row['District']
    lat, lon = get_lat_long_retry(panchayat, block, district)
    df.at[index, 'Latitude'] = lat
    df.at[index, 'Longitude'] = lon
    time.sleep(1)  # Sleep to respect Nominatim's usage policy

# Save the updated dataframe back to Excel
output_file_path = 'farmer_panchayat_updated.xlsx'  # Change this to your desired output path
df.to_excel(output_file_path, index=False)
