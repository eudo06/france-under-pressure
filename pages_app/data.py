
from pathlib import Path

import pandas as pd
import streamlit as st

# On définit les chemins vers les deux fichiers CSV
# à partir du dossier principal du projet
ROOT = Path(__file__).resolve().parents[1]
ACCIDENTS_PATH = ROOT / "data" / "processed" / "accidents_2024.csv"
USAGERS_PATH = ROOT / "data" / "processed" / "usagers_2024.csv"

# On garde les chiffres de référence pour vérifier
# que les données chargées correspondent bien à notre étude
REFERENCES_2024 = (54_402, 3_226, 3_432)


# Le cache évite de relire le fichier à chaque interaction
# ce qui permet de rendre l'application plus rapide
@st.cache_data
def _lire_accidents(path, version):
    return pd.read_csv(path, dtype={"Num_Acc": str, "dep": str, "com": str}, low_memory=False)


@st.cache_data
def _lire_usagers(path, version):
    return pd.read_csv(path, dtype={"Num_Acc": str}, low_memory=False)


def _verifier_fichier(path):
    # Avant de charger un CSV, on vérifie qu'il existe bien
    # sinon on affiche une erreur et on arrête l'exécution
    if not path.is_file():
        st.error(f"Fichier introuvable : {path}. Placez le CSV dans le projet, puis rechargez la page.")
        st.stop()

    # On récupère la date de modification et la taille du fichier
    # pour actualiser le cache si les données changent
    statistiques = path.stat()
    return statistiques.st_mtime_ns, statistiques.st_size


def _verifier_colonnes(donnees, colonnes, nom):
    # On vérifie que toutes les colonnes nécessaires sont présentes
    # pour éviter les erreurs dans les analyses
    manquantes = colonnes.difference(donnees.columns)

    if manquantes:
        raise ValueError(f"{nom} : colonnes manquantes : {', '.join(sorted(manquantes))}")


def _verifier_accidents(accidents):
    # On commence par vérifier les colonnes indispensables
    _verifier_colonnes(
        accidents,
        {"Num_Acc", "dep", "agg", "mortel", "nombre_tues", "nombre_usagers"},
        "accidents_2024.csv",
    )

    # Chaque accident doit avoir un identifiant unique
    # On refuse donc les identifiants manquants ou dupliqués
    if accidents["Num_Acc"].isna().any() or not accidents["Num_Acc"].is_unique:
        raise ValueError("accidents_2024.csv : identifiants d'accident absents ou dupliqués")

    # On vérifie que les nombres de personnes tuées et d'usagers
    # sont bien numériques et qu'il ne manque aucune valeur
    nombre_tues = pd.to_numeric(accidents["nombre_tues"], errors="coerce")
    nombre_usagers = pd.to_numeric(accidents["nombre_usagers"], errors="coerce")

    if nombre_tues.isna().any() or nombre_usagers.isna().any():
        raise ValueError("accidents_2024.csv : effectifs non numériques ou manquants")

    # On écarte les valeurs impossibles comme un nombre négatif de décès
    # ou un accident sans aucun usager enregistré
    if ((nombre_tues < 0).any() or (nombre_usagers < 1).any()
            or (nombre_tues % 1 != 0).any() or (nombre_usagers % 1 != 0).any()):
        raise ValueError("accidents_2024.csv : effectifs invalides")

    # Si un accident compte au moins un décès, il doit être indiqué comme mortel
    # On vérifie donc que les deux colonnes donnent la même information
    if not accidents["mortel"].eq(nombre_tues.gt(0)).all():
        raise ValueError("accidents_2024.csv : indicateur mortel incohérent avec nombre_tues")


def _verifier_usagers(usagers):
    # On fait les mêmes vérifications de base pour le fichier des usagers
    _verifier_colonnes(
        usagers,
        {"Num_Acc", "id_usager", "grav", "tue", "catu", "sexe", "an_nais"},
        "usagers_2024.csv",
    )

    # Chaque usager doit avoir un identifiant unique
    # et être rattaché à un accident
    if (usagers["Num_Acc"].isna().any() or usagers["id_usager"].isna().any()
            or not usagers["id_usager"].is_unique):
        raise ValueError("usagers_2024.csv : identifiants absents ou dupliqués")

    # On vérifie que les codes de gravité correspondent
    # aux quatre valeurs prévues dans les données BAAC
    gravite = pd.to_numeric(usagers["grav"], errors="coerce")

    if not gravite.isin([1, 2, 3, 4]).all():
        raise ValueError("usagers_2024.csv : codes de gravité inconnus")

    # Dans les données BAAC, le code 2 correspond à une personne tuée
    # On vérifie que la colonne tue respecte bien cette règle
    if not usagers["tue"].eq(gravite.eq(2).astype(int)).all():
        raise ValueError("usagers_2024.csv : indicateur tue incohérent avec grav")


def _verifier_jointure(accidents, usagers):
    # On regroupe les usagers par accident pour retrouver
    # combien de personnes sont impliquées et combien sont décédées
    regroupement = usagers.groupby("Num_Acc").agg(
        nombre_usagers=("tue", "size"),
        nombre_tues=("tue", "sum"),
    )

    # On récupère les mêmes informations dans le fichier des accidents
    # afin de pouvoir comparer les deux résultats
    controles = accidents.set_index("Num_Acc")[["nombre_usagers", "nombre_tues"]]

    # On vérifie que les deux fichiers contiennent les mêmes accidents
    if set(controles.index) != set(regroupement.index):
        raise ValueError("Les fichiers accidents et usagers ne couvrent pas les mêmes accidents")

    regroupement = regroupement.reindex(controles.index)

    # Les nombres d'usagers et de décès doivent être identiques
    # dans les deux fichiers pour chaque accident
    if (not controles["nombre_usagers"].eq(regroupement["nombre_usagers"]).all()
            or not controles["nombre_tues"].eq(regroupement["nombre_tues"]).all()):
        raise ValueError("Les effectifs d'usagers ou de personnes tuées ne concordent pas")


def _avertir_ecart_references(accidents):
    # On recalcule les trois chiffres principaux à partir du CSV
    # pour les comparer aux chiffres de référence
    totaux = (
        len(accidents),
        int(accidents["mortel"].sum()),
        int(accidents["nombre_tues"].sum()),
    )

    # Si les résultats ne correspondent pas, on affiche un avertissement
    # sans empêcher l'utilisateur de consulter l'application
    if totaux != REFERENCES_2024:
        st.warning(
            "Les totaux des CSV diffèrent des chiffres de référence BAAC 2024 "
            "(54 402 accidents corporels, 3 226 accidents mortels, "
            "3 432 personnes tuées). Vérifiez la version des données."
        )


def charger_accidents():
    # Cette fonction est utilisée par les chapitres qui analysent les accidents
    # Elle vérifie le fichier avant de retourner les données
    version = _verifier_fichier(ACCIDENTS_PATH)
    accidents = _lire_accidents(ACCIDENTS_PATH, version)

    _verifier_accidents(accidents)
    _avertir_ecart_references(accidents)

    # Si le fichier des usagers est disponible, on vérifie aussi
    # que ses données correspondent à celles des accidents
    if USAGERS_PATH.is_file():
        usagers = _lire_usagers(USAGERS_PATH, _verifier_fichier(USAGERS_PATH))
        _verifier_usagers(usagers)
        _verifier_jointure(accidents, usagers)

    return accidents


def charger_usagers():
    # Même principe ici, mais cette fois on charge les données des usagers
    version = _verifier_fichier(USAGERS_PATH)
    usagers = _lire_usagers(USAGERS_PATH, version)

    _verifier_usagers(usagers)

    # On contrôle également la cohérence avec le fichier des accidents
    # lorsqu'il est présent dans le projet
    if ACCIDENTS_PATH.is_file():
        accidents = _lire_accidents(ACCIDENTS_PATH, _verifier_fichier(ACCIDENTS_PATH))
        _verifier_accidents(accidents)
        _avertir_ecart_references(accidents)
        _verifier_jointure(accidents, usagers)

    return usagers
