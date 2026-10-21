import json
import os
import re
import folium
from folium import plugins
import pandas as pd

# Tuiles Esri Canvas : gratuites, sans clé API, sans blocage 403
ESRI_GRAY_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
ESRI_ATTR = "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ"


def waze_map_report(clean_data, score_data, output_dir):
    """Génère une carte interactive Folium par commune."""
    if not os.path.exists(clean_data) or not os.path.exists(score_data):
        print(f"Fichiers requis introuvables : {clean_data} ou {score_data}")
        return

    print("Génération des cartes communales...")
    df = pd.read_csv(clean_data, sep=";", low_memory=False)
    street_stats = pd.read_csv(score_data, sep=";")
    os.makedirs(output_dir, exist_ok=True)

    villes_presentes = df["city"].dropna().unique()

    for ville in villes_presentes:
        df_v = df[df["city"] == ville]
        stats_v = street_stats[street_stats["city"] == ville]

        if df_v.empty or stats_v.empty:
            continue

        # Récupération du centre de la commune
        lat, lon = 48.6238, 2.4418
        try:
            raw_point = str(df_v["geo_point_2d"].dropna().iloc[0])
            if "," in raw_point:
                lat, lon = map(float, raw_point.split(","))
            else:
                pt = json.loads(raw_point.replace("'", '"'))
                lat, lon = pt["lat"], pt["lon"]
        except Exception:
            pass

        m = folium.Map(
            location=[lat, lon],
            zoom_start=13,
            tiles=ESRI_GRAY_URL,
            attr=ESRI_ATTR,
        )
        plugins.Fullscreen(position="topleft").add_to(m)

        fg_noirs = folium.FeatureGroup(name="Points Noirs (Score > 75/100)", show=True)
        fg_reguliers = folium.FeatureGroup(name="Problèmes Réguliers (Score 40-75/100)", show=True)
        fg_occasionnels = folium.FeatureGroup(name="Problèmes Occasionnels (Score < 40/100)", show=True)

        # Indexation des tracés par rue pour la commune en cours
        segments_dict = df_v.dropna(subset=["line"]).groupby("street")["line"].unique().to_dict()

        for _, row in stats_v.iterrows():
            street_name = row["street"]
            score = row["score_100"]
            alerts = int(row["total_alerts"])
            delay = int(row["delay_moyen"])
            speed = round(row["speed_moyenne"], 1)

            if score >= 75:
                color, weight, fg, badge = "#b71c1c", 7, fg_noirs, "Point Noir"
            elif score >= 40:
                color, weight, fg, badge = "#f57c00", 5, fg_reguliers, "Régulier"
            else:
                color, weight, fg, badge = "#4caf50", 3, fg_occasionnels, "Occasionnel"

            tooltip_text = f"<b>{street_name}</b><br>Score : {score}/100"
            popup_html = f"""
            <div style="min-width: 220px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 6px 0; color: {color};">{street_name}</h4>
                <span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold;">
                    {badge}
                </span>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; margin: 0; line-height: 1.5;">
                    <b>Score :</b> {score} / 100<br>
                    <b>Alertes :</b> {alerts}<br>
                    <b>Retard moyen :</b> {delay} s<br>
                    <b>Vitesse moyenne :</b> {speed} km/h
                </p>
            </div>
            """

            for line_raw in segments_dict.get(street_name, []):
                try:
                    line_data = json.loads(line_raw.replace("'", '"')) if isinstance(line_raw, str) else line_raw
                    coords_list = line_data["coordinates"] if "coordinates" in line_data else line_data["geometry"]["coordinates"]
                    coords = [[p[1], p[0]] for p in coords_list]

                    folium.PolyLine(
                        coords,
                        color=color,
                        weight=weight,
                        opacity=0.85,
                        tooltip=tooltip_text,
                        popup=folium.Popup(popup_html, max_width=300),
                    ).add_to(fg)
                except Exception:
                    continue

        fg_noirs.add_to(m)
        fg_reguliers.add_to(m)
        fg_occasionnels.add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)

        safe_name = re.sub(r"[^a-zA-Z0-9\-_]", "", str(ville).replace(" ", "_"))
        m.save(os.path.join(output_dir, f"carte_{safe_name}.html"))
        print(f"Carte générée : {ville}")

    print("Fin de génération des cartes communales.")


if __name__ == "__main__":
    waze_map_report(
        "data/argent/waze_gps_2026_clean.csv",
        "data/gold/waze_gps_2026_scores.csv",
        "maps/rapports_2026_score_unique",
    )