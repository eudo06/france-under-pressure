from pathlib import Path
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "https://www.data.gouv.fr/api/1/datasets/"
DATASET_ID = "53698f4ca3a729239d2036df"

response = requests.get(
    f"{API_URL}{DATASET_ID}/",
    timeout=30
)
response.raise_for_status()

dataset = response.json()

fichiers = [
    "caract-2024.csv",
    "lieux-2024.csv",
    "vehicules-2024.csv",
    "usagers-2024.csv"
]

for fichier in fichiers:
    ressources = [
        r for r in dataset["resources"]
        if fichier.lower() in (
            r.get("title", "") + " " +
            r.get("url", "")
        ).lower()
    ]

    if not ressources:
        print(f"Fichier introuvable : {fichier}")
        continue

    url = ressources[0]["url"]
    destination = DATA_DIR / fichier

    print(f"Téléchargement : {fichier}")

    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()

        with open(destination, "wb") as f:
            for bloc in r.iter_content(chunk_size=1024 * 1024):
                if bloc:
                    f.write(bloc)

    print(f"Terminé : {destination}")

print("\nTéléchargement terminé.")