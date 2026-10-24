
import pandas as pd
import plotly.express as px
import streamlit as st

from pages_app.data import charger_accidents


def render():
    df = charger_accidents()

    st.divider()
    st.header("03 — Quand les accidents sont-ils les plus graves ?")

    st.markdown("""
Un accident peut survenir à n'importe quel moment de la journée. Cependant, les conditions de circulation évoluent selon les heures par exemple
trafic dense, déplacements professionnels, retours de soirée
ou circulation nocturne. Nous allons examiner si les moments où les accidents sont
les plus nombreux correspondent également à ceux où leur
proportion de conséquences mortelles est la plus élevée.
""")

    # On fait une copie pour préparer les données temporelles
    # sans modifier celles utilisées dans les autres chapitres
    df_temps = df.copy()

    # On rassemble l'année, le mois et le jour dans une seule date
    # Les dates incorrectes seront ignorées dans les analyses concernées
    df_temps["date"] = pd.to_datetime(
        dict(
            year=df_temps["an"],
            month=df_temps["mois"],
            day=df_temps["jour"]
        ),
        errors="coerce"
    )

    # On récupère uniquement l'heure à partir de la colonne hrmn
    # Par exemple, 14:35 devient 14
    df_temps["heure"] = pd.to_numeric(
        df_temps["hrmn"].astype(str).str.split(":").str[0],
        errors="coerce"
    )

    # On écarte les heures qui ne sont pas comprises entre 0 et 23
    df_temps.loc[
        ~df_temps["heure"].between(0, 23), "heure"
    ] = float("nan")

    # On associe les numéros des jours à leurs noms en français
    jours = {
        0: "Lundi",
        1: "Mardi",
        2: "Mercredi",
        3: "Jeudi",
        4: "Vendredi",
        5: "Samedi",
        6: "Dimanche"
    }

    df_temps["jour_semaine"] = (
        df_temps["date"].dt.dayofweek.map(jours)
    )

    # On découpe la journée en quatre périodes
    # pour comparer plus facilement la gravité des accidents
    def definir_periode(heure):
        if pd.isna(heure):
            return "Non renseignée"
        if 6 <= heure < 12:
            return "Matin"
        elif 12 <= heure < 18:
            return "Après-midi"
        elif 18 <= heure < 22:
            return "Soirée"
        else:
            return "Nuit"

    df_temps["periode"] = df_temps["heure"].apply(definir_periode)

    st.subheader("À quelles heures la gravité est-elle la plus élevée ?")

    # On regroupe les accidents par heure pour calculer
    # le nombre d'accidents et ceux qui sont mortels
    par_heure = (
        df_temps.dropna(subset=["heure"])
        .groupby("heure", as_index=False)
        .agg(
            accidents=("Num_Acc", "count"),
            mortels=("mortel", "sum")
        )
    )

    # On calcule la proportion d'accidents mortels pour chaque heure
    par_heure["part_mortels"] = (
        par_heure["mortels"] / par_heure["accidents"] * 100
    )

    # On peut choisir entre observer le nombre d'accidents
    # ou leur proportion de conséquences mortelles
    indicateur_heure = st.radio(
        "Indicateur temporel :",
        ["Nombre d'accidents", "Part d'accidents mortels"],
        horizontal=True,
        key="indicateur_heure"
    )

    col_heure = (
        "accidents"
        if indicateur_heure == "Nombre d'accidents"
        else "part_mortels"
    )

    # On utilise une courbe pour suivre l'évolution
    # de l'indicateur choisi au cours de la journée
    fig_heure = px.line(
        par_heure,
        x="heure",
        y=col_heure,
        markers=True,
        labels={
            "heure": "Heure de la journée",
            "accidents": "Nombre d'accidents",
            "part_mortels": "Accidents mortels (%)"
        }
    )

    fig_heure.update_xaxes(
        dtick=1,
        range=[0, 23]
    )

    fig_heure.update_layout(height=420)

    st.plotly_chart(fig_heure, use_container_width=True)

    st.subheader("La nuit est-elle associée à une gravité plus élevée ?")

    # On définit l'ordre des périodes pour qu'elles apparaissent
    # dans le bon ordre sur le graphique
    ordre_periodes = ["Matin", "Après-midi", "Soirée", "Nuit"]

    # On regroupe les accidents selon les quatre périodes
    # en laissant de côté les heures non renseignées
    par_periode = (
        df_temps[df_temps["periode"].isin(ordre_periodes)]
        .groupby("periode", as_index=False)
        .agg(
            accidents=("Num_Acc", "count"),
            mortels=("mortel", "sum")
        )
    )

    # On calcule la part des accidents mortels pour chaque période
    par_periode["part_mortels"] = (
        par_periode["mortels"] / par_periode["accidents"] * 100
    )

    # Le diagramme en barres permet de comparer directement
    # le matin, l'après-midi, la soirée et la nuit
    fig_periode = px.bar(
        par_periode,
        x="periode",
        y="part_mortels",
        color="part_mortels",
        text="part_mortels",
        category_orders={"periode": ordre_periodes},
        color_continuous_scale="Reds",
        labels={
            "periode": "Période",
            "part_mortels": "Accidents mortels (%)"
        }
    )

    fig_periode.update_traces(
        texttemplate="%{text:.2f} %",
        textposition="outside"
    )

    fig_periode.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=420,
        yaxis_range=[0, par_periode["part_mortels"].max() * 1.25]
    )

    st.plotly_chart(fig_periode, use_container_width=True)

    # On recherche automatiquement la période avec la plus grande
    # proportion d'accidents mortels pour l'expliquer dans le texte
    periode_max = par_periode.loc[
        par_periode["part_mortels"].idxmax()
    ]

    st.markdown(f"""
### Ce que nous observons

La période présentant la proportion d'accidents mortels
la plus élevée est **{periode_max['periode']}**,
avec **{periode_max['part_mortels']:.2f} %**
d'accidents mortels parmi les accidents corporels enregistrés. Cette observation mérite d'être approfondie :
la luminosité, la fatigue, les déplacements et les
caractéristiques des routes peuvent varier selon les horaires. Ces données descriptives ne permettent toutefois pas
d'attribuer directement cette différence à un facteur précis.
""")

    st.subheader("Quels créneaux combinent jour et heure ?")

    ordre_jours = [
        "Lundi", "Mardi", "Mercredi", "Jeudi",
        "Vendredi", "Samedi", "Dimanche"
    ]

    # On croise les jours de la semaine avec les heures
    # pour connaître les résultats de chaque créneau
    heatmap_df = (
        df_temps.dropna(subset=["jour_semaine", "heure"])
        .groupby(["jour_semaine", "heure"], as_index=False)
        .agg(
            accidents=("Num_Acc", "count"),
            mortels=("mortel", "sum")
        )
    )

    # On calcule la proportion d'accidents mortels
    # pour chaque combinaison de jour et d'heure
    heatmap_df["part_mortels"] = (
        heatmap_df["mortels"] / heatmap_df["accidents"] * 100
    )

    # On masque les créneaux qui comptent moins de 30 accidents
    # car un pourcentage basé sur trop peu de cas peut être trompeur
    seuil_min = 30

    heatmap_df.loc[
        heatmap_df["accidents"] < seuil_min,
        "part_mortels"
    ] = float("nan")

    # On transforme les résultats en tableau :
    # les jours en lignes et les heures en colonnes
    matrice = heatmap_df.pivot(
        index="jour_semaine",
        columns="heure",
        values="part_mortels"
    )

    # On remet les jours et les heures dans leur ordre habituel
    matrice = matrice.reindex(
        index=ordre_jours,
        columns=range(24)
    )

    # On utilise une heatmap pour repérer visuellement
    # les créneaux où la proportion d'accidents mortels est plus élevée
    fig_heatmap = px.imshow(
        matrice,
        color_continuous_scale="Reds",
        aspect="auto",
        labels={
            "x": "Heure",
            "y": "Jour de la semaine",
            "color": "Accidents mortels (%)"
        }
    )

    fig_heatmap.update_layout(height=450)

    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.caption(
        "Les créneaux comptant moins de 30 accidents corporels "
        "sont masqués afin d'éviter de surinterpréter des proportions "
        "calculées sur de très petits effectifs."
    )

    # On termine ce chapitre en rappelant que l'heure seule
    # ne suffit pas à expliquer la gravité d'un accident
    st.markdown("""
### Ce que cette analyse nous apprend

Le moment d'un accident est une dimension importante
pour comprendre sa gravité. Cependant, l'heure ne suffit pas à expliquer les différences
observées. Deux accidents survenus au même moment peuvent
se produire dans des conditions très différentes.

**Une nouvelle question apparaît alors :**

La luminosité, les conditions météorologiques et les
caractéristiques de la route sont-elles associées à des
différences de gravité ?
C'est ce que nous allons explorer dans le chapitre suivant.
""")
