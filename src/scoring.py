import os
import numpy as np
import pandas as pd


def scoring(input_file, output_file):
    """Calcule le score de congestion par commune et par rue pour éviter les homonymies."""
    if not os.path.exists(input_file):
        print(f"Erreur : Impossible de trouver {input_file}")
        return None

    print(f"Calcul des scores à partir de : {input_file}")
    df = pd.read_csv(input_file, sep=";", low_memory=False)

    # Agrégation par couple (ville, rue)
    street_stats = (
        df.groupby(["city", "street"], as_index=False)
        .agg(
            total_alerts=("uuid", "count"),
            delay_moyen=("delay", "mean"),
            speed_moyenne=("speed", "mean"),
        )
    )

    # Formule d'impact : Volume d'alertes * Durée moyenne (min) * Ratio de ralentissement
    street_stats["raw_impact"] = (
        street_stats["total_alerts"]
        * (street_stats["delay_moyen"] / 60)
        * (50 / (street_stats["speed_moyenne"] + 1))
    )

    street_stats["log_impact"] = np.log1p(street_stats["raw_impact"])
    max_log = street_stats["log_impact"].max()

    if max_log > 0:
        street_stats["score_100"] = (street_stats["log_impact"] / max_log * 100).round(1)
    else:
        street_stats["score_100"] = 0.0

    # Nettoyage des colonnes techniques
    street_stats = street_stats.drop(columns=["raw_impact", "log_impact"])

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    street_stats.to_csv(output_file, index=False, sep=";")
    print(f"Scores calculés sauvegardés ({len(street_stats)} tronçons) dans : {output_file}")
    return output_file


if __name__ == "__main__":
    clean_path = "data/argent/waze_gps_2026_clean.csv"
    scoring_path = "data/gold/waze_gps_2026_scores.csv"
    scoring(clean_path, scoring_path)