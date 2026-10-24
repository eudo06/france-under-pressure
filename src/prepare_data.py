from pathlib import Path
import pandas as pd

# Chemins du projet
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Chargement des données
accidents = pd.read_csv(
    RAW_DIR / "caract-2024.csv",
    sep=";",
    dtype={"Num_Acc": str, "dep": str, "com": str},
    low_memory=False
)

usagers = pd.read_csv(
    RAW_DIR / "usagers-2024.csv",
    sep=";",
    dtype={"Num_Acc": str},
    low_memory=False
)

# Identification des personnes tuées
usagers["tue"] = (usagers["grav"] == 2).astype(int)

# Agrégation : une ligne par accident
gravite = (
    usagers.groupby("Num_Acc", as_index=False)
    .agg(
        nombre_usagers=("tue", "size"),
        nombre_tues=("tue", "sum")
    )
)

gravite["mortel"] = gravite["nombre_tues"] > 0

# Jointure avec les caractéristiques des accidents
accidents = accidents.merge(
    gravite,
    on="Num_Acc",
    how="left",
    validate="one_to_one"
)

# Contrôle des données
assert accidents["Num_Acc"].is_unique
assert len(accidents) == 54402
assert accidents["nombre_tues"].notna().all()

# Calcul des indicateurs
nombre_accidents = len(accidents)
nombre_mortels = int(accidents["mortel"].sum())
nombre_tues = int(usagers["tue"].sum())

taux_mortels = (
    nombre_mortels / nombre_accidents * 100
)

print("\n===== INDICATEURS BAAC 2024 =====")
print(f"Accidents corporels : {nombre_accidents:,}")
print(f"Accidents mortels : {nombre_mortels:,}")
print(f"Personnes tuées : {nombre_tues:,}")
print(f"Proportion d'accidents mortels : {taux_mortels:.2f}%")

# Sauvegarde des données préparées
accidents.to_csv(
    PROCESSED_DIR / "accidents_2024.csv",
    index=False
)

usagers.to_csv(
    PROCESSED_DIR / "usagers_2024.csv",
    index=False
)

print("\nFichiers préparés et enregistrés.")