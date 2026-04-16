import pandas as pd
import json
import folium
from folium import plugins
import os
import re

# Configuration
path_clean_data = "data/argent/waze_gps_2026_clean.csv"
path_scoring_data = "data/gold/waze_gps_2026_scores.csv"
dir_maps = "maps/rapports_2026_score_unique"

def waze_map_report(clean_data, score_data, output_file):
    if not os.path.exists(clean_data):
        print(f"Can't find {clean_data}")
        return
    elif not os.path.exists(score_data):
        print(f"Can't find {score_data}")
        return
    elif not os.path.exists(clean_data) and not os.path.exists(score_data):
        print(f"Can't find {clean_data} and {score_data}")
        return

    print("Loading data")
    df = pd.read_csv(clean_data, sep=';', low_memory=False)
    street_stats = pd.read_csv(score_data, sep=';')

    os.makedirs(output_file, exist_ok=True)
    villes_presentes = df['city'].unique()

    print("Map generation")
    for ville in villes_presentes:
        if "202" in str(ville): continue

        df_v = df[df['city'] == ville].copy()
        rues_de_la_ville = df_v['street'].unique()
        stats_v = street_stats[street_stats['street'].isin(rues_de_la_ville)]

        if df_v.empty or stats_v.empty:
            continue

        # Centering the map
        try:
            raw_point = str(df_v['geo_point_2d'].iloc[0])
            if ',' in raw_point:
                lat, lon = map(float, raw_point.split(','))
            else:
                point_data = json.loads(raw_point.replace("'", '"'))
                lat, lon = point_data['lat'], point_data['lon']
        except:
            continue

        m = folium.Map(location=[lat, lon], zoom_start=14, tiles='CartoDB positron')
        plugins.Fullscreen(position='topleft').add_to(m)

        # Layers
        fg_noirs = folium.FeatureGroup(name="Points Noirs (Score > 75/100)", show=True)
        fg_reguliers = folium.FeatureGroup(name="Problèmes Réguliers (Score 40-75/100)", show=True)
        fg_occasionnels = folium.FeatureGroup(name="Problèmes Occasionnels (Score < 40/100)", show=True)

        for _, row_stat in stats_v.iterrows():
            street_name = row_stat['street']
            score = row_stat['score_100']
            alerts = int(row_stat['total_alerts'])
            delay = int(row_stat['delay_moyen'])
            speed = round(row_stat['speed_moyenne'], 1)

            # Category assignment
            if score >= 75:
                color, weight, fg = '#b71c1c', 7, fg_noirs
                badge = "Point Noir"
            elif score >= 40:
                color, weight, fg = '#f57c00', 5, fg_reguliers
                badge = "Régulier"
            else:
                color, weight, fg = '#4caf50', 3, fg_occasionnels
                badge = "Occasionnel"

            tooltip_text = f"<span style='font-size:14px;'><b>{street_name}</b><br>Score Global: {score}/100</span>"

            popup_html = f"""
            <div style="min-width: 240px; font-family: Arial, sans-serif;">
                <h4 style="margin-bottom:8px; color:{color}; font-size:16px;">📍 {street_name}</h4>
                <span style="background-color:{color}; color:white; padding:3px 6px; border-radius:4px; font-size:12px; font-weight:bold;">
                    {badge}
                </span>
                <hr style="margin:12px 0; border: 0; border-top: 1px solid #ccc;">
                <p style="font-size:13px; line-height:1.6;">
                    <b>🏆 Score de Nuisance :</b> {score} / 100<br>
                    <b>🚨 Alertes dans l'année :</b> {alerts}<br>
                    <b>⏱️ Retard moyen :</b> {delay} secondes<br>
                    <b>🚗 Vitesse moyenne :</b> {speed} km/h<br>
                </p>
            </div>
            """

            segments_rue = df_v[df_v['street'] == street_name]['line'].unique()

            for line_raw in segments_rue:
                try:
                    line_data = json.loads(line_raw.replace("'", '"')) if isinstance(line_raw, str) else line_raw
                    coords_list = line_data['coordinates'] if 'coordinates' in line_data else line_data['geometry']['coordinates']
                    coords = [[p[1], p[0]] for p in coords_list]
                    folium.PolyLine(coords, color=color, weight=weight, opacity=0.85, tooltip=tooltip_text, popup=folium.Popup(popup_html, max_width=300)).add_to(fg)
                except:
                    continue

        fg_noirs.add_to(m)
        fg_reguliers.add_to(m)
        fg_occasionnels.add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)

        # Save
        safe_name = re.sub(r'[^a-zA-Z0-9\-_]', '', str(ville).replace(' ', '_'))
        file_path = os.path.join(output_file, f"carte_{safe_name}.html")
        m.save(file_path)
        print(f"Map generated for : {ville}")

    print("Map generation complete")

if __name__ == "__main__":
    waze_map_report(path_clean_data, path_scoring_data, dir_maps)