from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

fichiers = {
    "Accidents": "caract-2024.csv",
    "Lieux": "lieux-2024.csv",
    "Véhicules": "vehicules-2024.csv",
    "Usagers": "usagers-2024.csv",
}

for nom, fichier in fichiers.items():
    chemin = DATA_DIR / fichier

    print(f"\n{'=' * 55}")
    print(f"TABLE : {nom}")
    print(f"{'=' * 55}")

    if not chemin.exists():
        print(f"Fichier introuvable : {chemin}")
        continue

    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        low_memory=False,
        dtype={"Num_Acc": str}
    )

    print(f"Nombre de lignes : {df.shape[0]:,}")
    print(f"Nombre de colonnes : {df.shape[1]}")

    print("\nColonnes :")
    print(df.columns.tolist())

    print("\nPremières lignes :")
    print(df.head(3).to_string(index=False))

    print("\nValeurs manquantes (top 10) :")
    print(
        df.isna()
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    print("\nNombre d'accidents distincts :")
    print(df["Num_Acc"].nunique())