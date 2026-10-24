
# France Under Pressure

Application interactive de Data Visualization & Storytelling développée avec Streamlit pour analyser les accidents corporels de la circulation routière en France en 2024.

Ce projet s'appuie sur les données officielles BAAC 2024 et cherche à mieux comprendre les différences de gravité des accidents selon les lieux, les moments, les circonstances et les profils des usagers.

L'objectif n'est pas seulement de montrer où les accidents sont les plus nombreux, mais aussi d'identifier les situations dans lesquelles les conséquences mortelles représentent une proportion plus importante.

## 1. Problématique

**Comment les caractéristiques géographiques, temporelles et les circonstances des accidents corporels sont-elles associées à leur gravité sur les routes françaises en 2024 ?**

Pour répondre à cette question, nous avons développé une application interactive permettant d'explorer les données et de comparer plusieurs indicateurs.

Le jeu de données préparé contient :

- **54 402 accidents corporels**
- **3 226 accidents mortels**
- **3 432 personnes tuées**

Un accident mortel peut entraîner plusieurs décès. Le nombre d'accidents mortels et celui des personnes tuées ne représentent donc pas la même chose.

Nous distinguons également le nombre d'accidents de la proportion d'accidents mortels parmi les accidents corporels enregistrés. Cette proportion ne correspond pas au risque individuel d'avoir un accident pendant un déplacement.

## 2. Source des données

Les données utilisées proviennent des bases annuelles BAAC (Bulletins d'Analyse des Accidents Corporels) diffusées sur data.gouv.fr.

Source officielle :

[Base de données des accidents corporels de la circulation routière — BAAC 2024](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024)

Quatre fichiers bruts sont disponibles pour l'année 2024 :

- `caract-2024.csv` : caractéristiques générales des accidents.
- `lieux-2024.csv` : informations sur les lieux et les infrastructures.
- `vehicules-2024.csv` : informations sur les véhicules impliqués.
- `usagers-2024.csv` : informations sur les personnes impliquées.

### Préparation des données

Le script `src/prepare_data.py` permet de préparer les données nécessaires à l'application.

Il utilise notamment l'identifiant `Num_Acc` pour relier les informations des accidents à celles des usagers, calculer les effectifs de personnes tuées et produire deux fichiers préparés :

- `data/processed/accidents_2024.csv`
- `data/processed/usagers_2024.csv`

Ces deux fichiers sont indispensables au fonctionnement des analyses.

Le fichier `data/raw/lieux-2024.csv` est également utilisé pour l'analyse des limitations de vitesse dans le chapitre 4.

Le fichier `vehicules-2024.csv` est conservé dans le projet pour documenter la provenance des données, mais n'est pas directement utilisé dans les visualisations actuelles.

### Vérification des données

Le fichier `pages_app/data.py` centralise le chargement des CSV.

Il effectue plusieurs vérifications :

- Présence des fichiers et des colonnes nécessaires.
- Absence d'identifiants d'accident manquants ou dupliqués.
- Cohérence des effectifs de personnes impliquées et tuées.
- Correspondance des informations entre les fichiers accidents et usagers.
- Comparaison des totaux avec les chiffres de référence de notre étude.

Ces contrôles permettent de détecter certaines incohérences avant l'affichage des résultats.

### Régénération des données

Les fichiers nécessaires sont déjà présents dans le projet.

Pour télécharger à nouveau les données brutes et recréer les fichiers préparés, exécuter depuis la racine du projet :

```bash
python src/download_data.py
python src/prepare_data.py
```

Le premier script télécharge les fichiers BAAC 2024 depuis la source publique. Le second prépare les deux CSV utilisés par l'application.

Ces scripts peuvent remplacer les fichiers existants. Il est donc préférable de conserver une copie lorsqu'une version précise des données doit être archivée.

Si les données officielles évoluent et que les totaux diffèrent des chiffres de référence, il faut vérifier la version utilisée avant d'interpréter les résultats.

## 3. Technologies utilisées

Le projet a été développé en Python avec plusieurs bibliothèques :

- **Python** : préparation, traitement et analyse des données.
- **Pandas** : manipulation des DataFrames, regroupements, jointures et calcul des indicateurs.
- **Plotly** : création de graphiques interactifs.
- **Streamlit** : développement de l'interface web et des filtres interactifs.
- **Requests** : téléchargement des données depuis leur source publique.

Nous utilisons également du CSS dans `app.py` pour personnaliser la présentation et adapter certains éléments aux différentes tailles d'écran.

## 4. Parcours de l'application

L'application est organisée autour d'une page d'accueil et de six chapitres accessibles depuis le menu latéral.

### Chapitre 1 — Comprendre la gravité

Ce chapitre présente les principaux indicateurs de l'année 2024 :

- Nombre d'accidents corporels.
- Nombre d'accidents mortels.
- Nombre de personnes tuées.
- Proportion d'accidents mortels.

Un filtre interactif permet de comparer les accidents en agglomération et hors agglomération.

### Chapitre 2 — Géographie des accidents

Ce chapitre analyse la répartition des accidents selon les départements français.

Il comprend notamment :

- Une carte interactive de la France métropolitaine.
- Une représentation séparée des territoires d'outre-mer.
- Une comparaison des nombres d'accidents.
- Un classement selon la proportion d'accidents mortels.

Un seuil minimal de 100 accidents, configurable, est appliqué par défaut au classement des proportions afin de limiter les comparaisons fondées sur de très petits effectifs.

### Chapitre 3 — Analyse temporelle

Ce chapitre étudie les accidents selon :

- Les heures de la journée.
- Les périodes du matin, de l'après-midi, de la soirée et de la nuit.
- Les jours de la semaine.

Une heatmap permet également de croiser les jours et les heures pour visualiser les différences de gravité.

### Chapitre 4 — Circonstances des accidents

Nous examinons quatre dimensions :

- La luminosité.
- Les conditions météorologiques.
- Les limitations de vitesse.
- Les types de collision.

L'objectif est de comparer les proportions d'accidents mortels selon les circonstances enregistrées.

La limitation de vitesse correspond à la vitesse maximale autorisée sur les lieux, et non à la vitesse réelle des véhicules.

### Chapitre 5 — Profils des usagers

Dans ce chapitre, nous passons de l'analyse des accidents à celle des personnes impliquées.

Nous étudions :

- Les catégories d'usagers : conducteurs, passagers et piétons.
- Les tranches d'âge.
- Le sexe.
- Le croisement entre âge et catégorie d'usager.

Les proportions calculées correspondent ici au nombre de personnes tuées parmi les usagers impliqués dans un accident corporel enregistré.

### Chapitre 6 — Conclusions et recommandations

Ce dernier chapitre reprend trois enseignements majeurs :

- La gravité des accidents hors agglomération.
- Les accidents survenus de nuit sans éclairage.
- Les conséquences observées chez les usagers âgés de 75 ans et plus.

Il propose également des pistes de prévention et présente les limites de notre analyse.

## 5. Organisation du projet

```text
france-under-pressure/
├── app.py
├── README.md
├── requirements.txt
│
├── pages_app/
│   ├── __init__.py
│   ├── data.py
│   ├── accueil.py
│   ├── gravite.py
│   ├── geographie.py
│   ├── temporalite.py
│   ├── circonstances.py
│   ├── usagers.py
│   └── conclusions.py
│
├── assets/
│   └── logo_efrei.png
│
├── data/
│   ├── processed/
│   │   ├── accidents_2024.csv
│   │   └── usagers_2024.csv
│   │
│   └── raw/
│       ├── caract-2024.csv
│       ├── lieux-2024.csv
│       ├── vehicules-2024.csv
│       └── usagers-2024.csv
│
└── src/
    ├── download_data.py
    ├── prepare_data.py
    └── exploration.py
```

Le fichier `app.py` constitue le point d'entrée de l'application.

Chaque chapitre possède son propre fichier Python dans `pages_app/`. Cette organisation permet de séparer les analyses et de faciliter la maintenance du code.

Le fichier `data.py` est utilisé pour charger et vérifier les données de manière centralisée.

## 6. Installation et lancement

### Prérequis

- Python 3.12 recommandé.
- Une connexion Internet pour télécharger les dépendances.
- Les fichiers CSV préparés présents dans le dossier `data/processed/`.

### Installation

Depuis le dossier principal du projet, créer un environnement virtuel :

```bash
python3.12 -m venv .venv
```

Sur macOS ou Linux, activer l'environnement :

```bash
source .venv/bin/activate
```

Sur Windows PowerShell :

```powershell
.venv\Scripts\Activate.ps1
```

Installer ensuite les dépendances :

```bash
python -m pip install -r requirements.txt
```

### Lancement de l'application

Exécuter la commande :

```bash
python -m streamlit run app.py
```

Streamlit affiche une adresse locale, généralement :

```text
http://localhost:8501
```

Ouvrir cette adresse dans un navigateur pour accéder à l'application.

## 7. Déploiement sur Streamlit Community Cloud

L'application est structurée pour pouvoir être déployée sur Streamlit Community Cloud.

Documentation officielle :

[Déployer une application Streamlit](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

Pour effectuer le déploiement :

1. Publier le projet dans un dépôt GitHub.
2. Se connecter à Streamlit Community Cloud.
3. Sélectionner le dépôt contenant le projet.
4. Choisir `app.py` comme fichier principal.
5. Sélectionner Python 3.12 dans les paramètres avancés.
6. Lancer le déploiement.

Le fichier `requirements.txt` doit rester à la racine du projet.

Il faut également inclure les fichiers nécessaires au fonctionnement de l'application :

- `app.py`
- `pages_app/`
- `requirements.txt`
- `data/processed/accidents_2024.csv`
- `data/processed/usagers_2024.csv`
- `data/raw/lieux-2024.csv`
- `assets/logo_efrei.png`

Les autres fichiers bruts et les scripts de `src/` sont à conserver si l'on souhaite permettre la reproduction complète de la préparation des données.

La carte métropolitaine utilise des contours géographiques récupérés depuis GitHub lors de l'exécution. Une connexion sortante est donc nécessaire pour afficher cette carte.

**État du déploiement :** l'application a été testée localement dans un environnement Python 3.12 propre. Le déploiement distant sur Streamlit Community Cloud n'a pas encore été testé.

## 8. Limites de l'analyse

Même si les données BAAC 2024 permettent de réaliser plusieurs analyses, certaines limites doivent être prises en compte.

### Périmètre des données

Les données concernent les accidents corporels enregistrés. Les accidents sans dommage corporel ne sont pas inclus.

### Absence de mesure d'exposition

Nous ne disposons pas du nombre total de trajets, des kilomètres parcourus ou du trafic pour chaque catégorie étudiée.

Les proportions calculées ne permettent donc pas de mesurer directement le risque d'accident par déplacement ou par habitant.

### Analyse descriptive

Les résultats montrent des associations entre certaines caractéristiques et la gravité des accidents.

Ils ne permettent pas de démontrer qu'une caractéristique provoque directement une conséquence mortelle.

### Valeurs manquantes

Certaines informations peuvent être absentes ou non exploitables.

Les exclusions nécessaires sont précisées dans les chapitres concernés, notamment pour les limitations de vitesse et les caractéristiques des usagers.

### Effectifs réduits

Les proportions calculées sur de petits nombres d'accidents peuvent varier fortement.

Un seuil minimal est utilisé dans certaines visualisations pour éviter de surinterpréter ces résultats. Il ne garantit toutefois pas leur significativité statistique.

### Période étudiée

Notre étude porte uniquement sur l'année 2024.

Elle ne permet donc pas de conclure à une évolution de la sécurité routière sur plusieurs années.

Pour aller plus loin, il serait intéressant de comparer plusieurs années et d'intégrer des données sur le trafic et les déplacements.

## 9. Conclusion

Avec France Under Pressure, nous avons cherché à montrer que le nombre d'accidents ne suffit pas à comprendre leur gravité.

L'analyse des données BAAC 2024 met en évidence des différences importantes selon les territoires, les conditions de circulation et les profils des usagers.

Grâce à Streamlit et Plotly, ces résultats sont présentés dans une application interactive qui permet d'explorer les données et de mieux comprendre les principaux contrastes.

Ce projet montre comment la Data Visualization et le Storytelling peuvent transformer des données publiques en informations accessibles et utiles pour réfléchir à la prévention routière.

---

**Projet de Data Visualization & Storytelling — EFREI Paris**

**Auteur :** Bli Jean Eudes KOUADIO

**Année universitaire :** 2026–2027

**Source des données :** BAAC 2024 — data.gouv.fr
