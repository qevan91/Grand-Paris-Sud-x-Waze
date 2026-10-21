import os
import unicodedata
import pandas as pd


def normalize(nom):
    """Normalise une chaîne : minuscules, suppression des accents et tirets."""
    if pd.isna(nom):
        return ""
    nfkd = unicodedata.normalize("NFKD", str(nom))
    sans_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sans_accents.lower().replace("-", " ").strip()


# Liste officielle des 23 communes de la communauté d'agglomération Grand Paris Sud
COMMUNES_GRAND_PARIS_SUD = [
    "Bondoufle",
    "Cesson",
    "Combs-la-Ville",
    "Corbeil-Essonnes",
    "Le Coudray-Montceaux",
    "Étiolles",
    "Évry-Courcouronnes",
    "Grigny",
    "Lieusaint",
    "Lisses",
    "Moissy-Cramayel",
    "Morsang-sur-Seine",
    "Nandy",
    "Réau",
    "Ris-Orangis",
    "Savigny-le-Temple",
    "Soisy-sur-Seine",
    "Saint-Pierre-du-Perray",
    "Saint-Germain-lès-Corbeil",
    "Saintry-sur-Seine",
    "Tigery",
    "Vert-Saint-Denis",
    "Villabé",
]


def data_cleaning(input_file, output_file) :
    """Filtre les communes cibles et nettoie les anomalies sur les retards et vitesses."""
    if not os.path.exists(input_file):
        print(f"Erreur : Impossible de trouver le fichier {input_file}")
        return None

    print(f"Nettoyage des données : chargement de {input_file}")
    df = pd.read_csv(input_file, sep=";", low_memory=False)
    df.columns = [c.lower() for c in df.columns]

    print("Filtrage territorial sur les 23 communes de Grand Paris Sud...")
    df["city_norm"] = df["city"].apply(normalize)
    communes_norm = {normalize(v) for v in COMMUNES_GRAND_PARIS_SUD}
    df = df[df["city_norm"].isin(communes_norm)].copy()

    # Nettoyage et cohérence des valeurs
    df["street"] = df["street"].fillna("Inconnue").str.strip()
    df["delay"] = pd.to_numeric(df["delay"], errors="coerce").fillna(0).clip(lower=0)
    df["speed"] = pd.to_numeric(df["speed"], errors="coerce").fillna(0).clip(lower=0)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, sep=";")
    print(f"Données nettoyées sauvegardées ({len(df)} lignes) dans : {output_file}")
    return output_file


if __name__ == "__main__":
    raw_path = "data/bronze/waze_gps_2026.csv"
    clean_path = "data/argent/waze_gps_2026_clean.csv"
    data_cleaning(raw_path, clean_path)