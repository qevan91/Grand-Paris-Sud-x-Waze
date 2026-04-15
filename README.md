# Grand Paris Sud x Waze : Analyse et Scoring du Trafic

Ce projet s'inscrit dans le programme **Connected Citizens** de Waze, un échange de données entre les collectivités et Waze pour améliorer la sécurité et la gestion du réseau routier. 

L'outil ***Grand Paris Sud x Waze*** permet aux élus et techniciens de visualiser la congestion sur les 23 communes de l'agglomération afin d'appuyer la prise de décision en matière de gestion de trafic et d'organisation d'événements.

---

## Architecture Data Lake (Médaillon)

Le projet utilise une architecture de données de type **Médaillon** en local pour garantir la qualité et la traçabilité des indicateurs produits :

1.  **Bronze (Données Brutes) :** Les données sont extraites directement de l'API Open Data Grand Paris Sud via le script `fetch_api.py` et stockées sans transformation dans `data/bronze/`.
2.  **Argent (Données Nettoyées) :** Le script `cleaning_data.py` filtre les données sur le périmètre géographique de Grand Paris Sud, normalise les noms de rues et de villes, et traite les valeurs aberrantes (vitesse ou délais négatifs).
3.  **Gold (Données Métiers) :** Pour obtenir un score de nuisance global, le script `scoring.py` combine les données par rue afin d'analyser en détail le trafic.

---

## Documentation Technique & Pipeline

### 1. Ingestion de données (`src/fetch_api.py`)
Se connecte à l'API Waze de Grand Paris Sud pour récupérer les exports CSV.
- **Authentification** : Utilise une clé API stockée dans un fichier `.env`.
- **Paramétrage** : Filtre les données sur une année spécifique (ex: 2026) via des requêtes SQL-like passées à l'API.

### 2. Nettoyage et Filtrage (`src/cleaning_data.py`)
Nettoie les données avant analyse.
- **Périmètre** : Filtre strictement sur les 23 communes membres (Bondoufle, Évry-Courcouronnes, Lieusaint, etc.).
- **Normalisation** : Suppression des accents et mise en minuscule des noms de villes pour éviter les doublons liés à la saisie.
- **Fiabilisation** : Remplacement des noms de rues manquants par "Inconnue".

### 3. Moteur de Scoring (`src/scoring.py`)
Calcule l'impact du trafic par rue selon la formule suivante :
- **Variables** : Nombre d'alertes, délai moyen (en minutes) et rapport de vitesse (vitesse théorique en km/h / vitesse réelle en km/h).
- **Transformation** : Utilisation de `np.log1p` pour réduire l'impact des valeurs extrêmes.
- **Normalisation** : Le score final est ramené sur une échelle de **0 à 100** pour faciliter la lecture.

### 4. Cartographie Interactive (`src/waze_gps_map.py`)
Génère des cartes HTML interactives par commune.
- **Visualisation** : Utilise la librairie Folium pour tracer les segments routiers.
- **Code couleur catégorie de tension** :
    -  **Points Noirs** (Score > 75)
    -  **Problèmes Réguliers** (Score 40-75)
    -  **Problèmes Occasionnels** (Score < 40)
- **Interactivité** : Infobulles détaillant le score, le nombre d'alertes dans l'année, le retard moyen et la vitesse moyenne (pendant incident).
- **Filtres** :
    -  **Filtrage** par tension.
    -  Filtre à plage à venir : retard moyen, vitesse moyenne (pendant incident), alerte dans l'année
---

## Stack Technique

- **Langage** : Python
- **Manipulations de données** : Pandas, NumPy
- **Visualisation** : Folium, Branca
- **API & Environnement** : Requests, Dotenv
- **Données** : [Open Data Grand Paris Sud](https://data.grandparissud.fr/pages/accueil/)

---

## Installation et Lancement

1.  **Installation des dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration** : Créez un fichier `.env` avec votre `API_KEY`. La syntaxe à suivre est dans le `.env.example` Les scripts créés automatiquement les dossiers de données et de cartes.


3.  **Exécution des scripts** :
    ```bash
    python src/fetch_api.py      # Récupération de données (Bronze)
    python src/cleaning_data.py  # Nettoyage des données (Silver)
    python src/scoring.py        # Calcul (Gold)
    python src/waze_gps_map.py   # Génération des cartes
    ```