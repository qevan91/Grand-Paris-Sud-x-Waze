import argparse
import sys
import time

from cleaning_data import data_cleaning
from fetch_api import fetch_data
from scoring import scoring
from waze_gps_global_map import waze_map_global_report
from waze_gps_map import waze_map_report


def main():
    parser = argparse.ArgumentParser(description="Pipeline d'analyse du trafic Waze - Grand Paris Sud")
    parser.add_argument("--year", type=int, default=2026, help="Année d'analyse cible (par défaut: 2026)")
    parser.add_argument("--skip-fetch", action="store_true", help="Passe l'étape de téléchargement API et utilise les données bronze existantes")
    parser.add_argument("--skip-maps", action="store_true", help="Calcule uniquement les scores sans générer les cartes Folium")
    args = parser.parse_args()

    year = args.year
    bronze_csv = f"data/bronze/waze_gps_{year}.csv"
    argent_csv = f"data/argent/waze_gps_{year}_clean.csv"
    gold_csv = f"data/gold/waze_gps_{year}_scores.csv"
    maps_dir = f"maps/rapports_{year}_score_unique"

    start_time = time.time()
    print(f"DÉMARRAGE DU PIPELINE WAZE GPS - ANNÉE {year}")

    # Récupération API
    if not args.skip_fetch:
        print("\n Téléchargement des données (Bronze)...")
        res = fetch_data(year, output_dir="data/bronze")
        if not res:
            print("Arrêt du pipeline : échec du téléchargement.")
            sys.exit(1)
    else:
        print("\n Étape de téléchargement ignorée (--skip-fetch).")

    # Nettoyage & Filtrage
    print("\n Nettoyage et normalisation territoriale (Argent)...")
    res_clean = data_cleaning(bronze_csv, argent_csv)
    if not res_clean:
        print("Arrêt du pipeline : échec du nettoyage.")
        sys.exit(1)

    # Calcul des scores
    print("\n Calcul des métriques et des scores de nuisance (Gold)...")
    res_score = scoring(argent_csv, gold_csv)
    if not res_score:
        print("Arrêt du pipeline : échec du scoring.")
        sys.exit(1)

    # Cartographie interactive
    if not args.skip_maps:
        print("\n Génération des cartes interactives HTML...")
        waze_map_global_report(argent_csv, gold_csv, maps_dir)
        waze_map_report(argent_csv, gold_csv, maps_dir)
    else:
        print("\n Génération des cartes ignorée (--skip-maps).")

    elapsed = round(time.time() - start_time, 2)
    print(f"Pipeline terminé en {elapsed} secondes")
    print(f"Cartes générées dans : {maps_dir}")


if __name__ == "__main__":
    main()