import io
import os
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()


def fetch_data(target_year, output_dir = "data/bronze") :
    """Télécharge les données Waze depuis l'API Grand Paris Sud pour une année donnée."""
    api_key = os.environ.get("API_KEY", "")
    url_base = "https://data.grandparissud.fr/api/explore/v2.1/catalog/datasets/2019-04-07-waze-traffic/exports/csv"

    url_csv = f"{url_base}?apikey={api_key}" if api_key else url_base

    params = {
        "where": f"start_time >= '{target_year}-01-01' AND start_time <= '{target_year}-12-31'",
        "limit": -1,
        "delimiter": ";",
        "use_labels": "true",
    }

    try:
        print(f"Téléchargement des données pour l'année {target_year}...")
        response = requests.get(url_csv, params=params, timeout=120)

        if response.status_code == 404:
            print(f"Dataset introuvable (Code HTTP 404)")
            return None

        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text), sep=";", low_memory=False)

    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return None

    if df.empty:
        print(f"Aucune donnée retournée pour l'année {target_year}.")
        return None

    print(f"Téléchargement réussi : {len(df)} lignes récupérées.")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"waze_gps_{target_year}.csv")
    df.to_csv(output_file, index=False, sep=";")
    print(f"Fichier sauvegardé : {output_file}")
    return output_file


if __name__ == "__main__":
    fetch_data(2026)