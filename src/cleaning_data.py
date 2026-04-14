import pandas as pd
import os

# Configuration
raw_data = "../data/bronze/waze_gps_2026.csv"
clean_data = "../data/argent/waze_gps_2026_clean.csv"

def data_cleaning(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error : Can't find {input_file}")
        return

    print("Loading raw data")
    df = pd.read_csv(input_file, sep=';', low_memory=False)
    df.columns = [c.lower() for c in df.columns]

    # Grand Paris Sud cities
    communes = [
        "Bondoufle", "Cesson", "Combs-la-Ville", "Corbeil-Essonnes", "Le Coudray-Montceaux", "Étiolles",
        "Évry-Courcouronnes", "Grigny", "Lieusaint", "Lisses", "Moissy-Cramayel", "Morsang-sur-Seine",
        "Nandy", "Réau", "Ris-Orangis", "Savigny-le-Temple", "Soisy-sur-Seine",
        "Saint-Pierre-du-Perray", "Saint-Germain-lès-Corbeil", "Saintry-sur-Seine",
        "Tigery", "Vert-Saint-Denis", "Villabé"
    ]

    print("Data filtering and cleaning")
    df['city_norm'] = df['city'].apply(normalize)
    communes_norm = [normalize(v) for v in communes]
    df = df[df['city_norm'].isin(communes_norm)].copy()

    # Cleaning
    df['street'] = df['street'].fillna("Inconnue")
    df['delay'] = df['delay'].clip(0)
    df['speed'] = df['speed'].clip(0)

    # Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, sep=';')
    print("Cleaned data saved")

def normalize(nom):
    if pd.isna(nom):
        return ""
    else:
        return str(nom).lower().replace('-', ' ').replace('é', 'e').replace('è', 'e')

if __name__ == "__main__":
    data_cleaning(raw_data, clean_data)