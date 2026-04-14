import pandas as pd
import requests
import io
from dotenv import load_dotenv
import os

# Load the environment variables from .env file
load_dotenv()

# Configuration
api_key = os.environ.get('API_KEY')
url_csv = f"https://data.grandparissud.fr/api/explore/v2.1/catalog/datasets/2019-04-07-waze-traffic/exports/csv?apikey={api_key}"
dir_datalake = "../data/bronze"


def fetch_data(target_year):
    params = {
        'where': f"start_time >= '{target_year}-01-01' AND start_time <= '{target_year}-12-31'",
        'limit': -1,
        'delimiter': ';',
        'use_labels': 'true'
    }

    try:
        print("Fetch data. The process can take a long time")
        response = requests.get(url_csv, params=params)
        if response.status_code == 404:
            print(f"Dataset not found : {response.status_code}")
            return None
        response.raise_for_status()

        # Read the CSV content
        df = pd.read_csv(io.StringIO(response.text), sep=';')

    except Exception as e:
        print(f"Connexion error : {e}")
        return None

    if df.empty:
        print(f"No data for {target_year}.")
        return None

    print(f"Successful fetch")

    # Save
    if not os.path.exists(dir_datalake):
        os.makedirs(dir_datalake, exist_ok=True)
        print(f"Folder created : {dir_datalake}")

    output_file = os.path.join(dir_datalake, f"waze_gps_{target_year}.csv")

    df.to_csv(output_file, index=False, sep=';')
    print(f"File saved : {output_file}")
    return df

df_2026 = fetch_data(2026)