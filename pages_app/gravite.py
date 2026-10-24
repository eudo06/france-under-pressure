
import plotly.express as px
import streamlit as st

from pages_app.data import charger_accidents


def render():
    # On récupère les données des accidents pour travailler dessus
    df = charger_accidents().copy()

    st.divider()

    st.header("01 — Comprendre la gravité")

    st.markdown("""
En 2024, la France a enregistré des dizaines de milliers
d'accidents corporels. Cependant, tous ces accidents n'ont pas les mêmes conséquences.
Certains entraînent des blessures, tandis que d'autres provoquent
la mort d'une ou plusieurs personnes. Avant d'explorer les territoires, commençons par mesurer
l'ampleur de cette différence.
""")

    # On laisse l'utilisateur choisir la zone qu'il souhaite analyser
    with st.container(border=True):
        st.subheader("Explorer les accidents par zone")
        zone_selectionnee = st.selectbox(
            "Sélectionnez une zone géographique",
            [
                "Toutes les zones",
                "En agglomération",
                "Hors agglomération"
            ],
            key="zone_gravite"
        )

    # Selon son choix, on garde uniquement les accidents de la zone concernée
    # Dans les données, 1 correspond à hors agglomération et 2 à en agglomération
    df_filtre = df.copy()

    if zone_selectionnee == "En agglomération":
        df_filtre = df_filtre[df_filtre["agg"] == 2]

    elif zone_selectionnee == "Hors agglomération":
        df_filtre = df_filtre[df_filtre["agg"] == 1]

    # On calcule les indicateurs à partir des données filtrées
    # La somme de la colonne mortel donne le nombre d'accidents mortels
    nombre_accidents = len(df_filtre)
    nombre_mortels = int(df_filtre["mortel"].sum())
    nombre_tues = int(df_filtre["nombre_tues"].sum())

    # On rapporte les accidents mortels au total des accidents corporels
    # On vérifie aussi que le total n'est pas nul pour éviter une division par zéro
    taux_mortels = (
        nombre_mortels / nombre_accidents * 100
        if nombre_accidents > 0 else 0
    )

    # Les quatre indicateurs se mettent à jour quand on change de zone
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Accidents corporels", f"{nombre_accidents:,}")
    col2.metric("Accidents mortels", f"{nombre_mortels:,}")
    col3.metric("Personnes tuées", f"{nombre_tues:,}")
    col4.metric("Part d'accidents mortels", f"{taux_mortels:.2f} %")

    st.caption(
        f"Zone sélectionnée : {zone_selectionnee} | "
        f"{nombre_accidents:,} accidents corporels analysés."
    )

    if zone_selectionnee == "Toutes les zones":
        st.markdown(
            "Vous explorez actuellement **l'ensemble des accidents "
            "corporels enregistrés en France en 2024**."
        )
    else:
        st.markdown(
            f"Vous explorez actuellement les accidents corporels "
            f"enregistrés **{zone_selectionnee.lower()} en 2024**."
        )

    st.caption(
        "La part d'accidents mortels correspond au nombre "
        "d'accidents mortels rapporté au nombre d'accidents "
        "corporels enregistrés."
    )

    st.subheader("Les accidents sont-ils plus graves hors agglomération ?")

    # Pour comparer les deux zones, on repart des données complètes
    # Le graphique reste donc identique même si un filtre est sélectionné plus haut
    df["zone"] = df["agg"].map({
        1: "Hors agglomération",
        2: "En agglomération"
    })

    # On regroupe les accidents par zone pour compter les accidents
    # et calculer combien d'entre eux sont mortels
    comparaison = (
        df.dropna(subset=["zone"])
        .groupby("zone", as_index=False)
        .agg(
            accidents=("Num_Acc", "count"),
            accidents_mortels=("mortel", "sum")
        )
    )

    # On calcule la part des accidents mortels pour chaque zone
    comparaison["part_mortels"] = (
        comparaison["accidents_mortels"]
        / comparaison["accidents"]
        * 100
    )

    # On utilise un diagramme en barres pour visualiser la différence
    # entre les deux zones
    fig = px.bar(
        comparaison,
        x="zone",
        y="part_mortels",
        color="zone",
        text="part_mortels",
        labels={
            "zone": "Zone",
            "part_mortels": "Accidents mortels (%)"
        },
        title="Part d'accidents mortels selon la zone"
    )

    fig.update_traces(
        texttemplate="%{text:.2f} %",
        textposition="outside"
    )

    fig.update_layout(
        showlegend=False,
        yaxis_range=[
            0,
            comparaison["part_mortels"].max() * 1.25
        ]
    )

    st.caption(
        "Le graphique ci-dessous conserve les deux zones "
        "pour permettre leur comparaison, indépendamment du filtre."
    )

    st.plotly_chart(fig, use_container_width=True)

    # On récupère les résultats de chaque zone pour rédiger
    # une interprétation directement à partir des données
    zone_urbaine = comparaison.loc[
        comparaison["zone"] == "En agglomération"
    ].iloc[0]

    zone_rurale = comparaison.loc[
        comparaison["zone"] == "Hors agglomération"
    ].iloc[0]

    # Ce rapport permet de voir combien de fois la proportion
    # d'accidents mortels est plus élevée hors agglomération
    rapport = (
        zone_rurale["part_mortels"]
        / zone_urbaine["part_mortels"]
    )

    st.markdown(f"""
### Ce que nous apprend cette comparaison

En agglomération, **{zone_urbaine['part_mortels']:.2f} %**
des accidents corporels enregistrés sont mortels. Hors agglomération, cette proportion atteint
**{zone_rurale['part_mortels']:.2f} %**. Autrement dit, parmi les accidents corporels enregistrés,
la proportion d'accidents mortels est environ
**{rapport:.1f} fois plus élevée hors agglomération**.

Ce contraste ne signifie pas qu'un trajet hors agglomération
présente nécessairement ce même niveau de risque.
Il nous invite plutôt à examiner les circonstances
des accidents : vitesse autorisée, luminosité,
conditions météorologiques et types de collision.
""")
