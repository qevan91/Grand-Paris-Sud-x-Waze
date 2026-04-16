import pandas as pd
import numpy as np
import os

# Configuration
clean_data = "data/argent/waze_gps_2026_clean.csv"
scoring_data = "data/gold/waze_gps_2026_scores.csv"

def scoring(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error : Can't find {input_file}")
        return

    print("Loading clean data")
    df = pd.read_csv(input_file, sep=';', low_memory=False)

    # Aggregation by street
    street_stats = df.groupby('street').agg(
        villes_traversees=('city', lambda x: ', '.join(x.dropna().unique())),
        total_alerts=('uuid', 'count'),
        delay_moyen=('delay', 'mean'),
        speed_moyenne=('speed', 'mean')
    ).reset_index()
    # Scoring
    print("Scoring")

    # Score = Number of alerts * Delay (min) * (normal_speed / real_speed)
    street_stats['raw_impact'] = (street_stats['total_alerts'] * (street_stats['delay_moyen'] / 60) * (50 / (street_stats['speed_moyenne'] + 1)))
    street_stats['log_impact'] = np.log1p(street_stats['raw_impact'])
    max_log = street_stats['log_impact'].max()
    street_stats['score_100'] = (street_stats['log_impact'] / max_log * 100).round(1)

    # Cleaning temporary columns
    street_stats = street_stats.drop(columns=['raw_impact', 'log_impact'])

    # Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    street_stats.to_csv(output_file, index=False, sep=';')
    print(f"Scores calculated and saved in: {output_file}")

if __name__ == "__main__":
    scoring(clean_data, scoring_data)