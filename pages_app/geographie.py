
from html import escape

import plotly.express as px
import requests
import streamlit as st

from pages_app.data import charger_accidents


# On garde les codes des territoires d'outre-mer avec leurs noms
# pour pouvoir les identifier dans les résultats
OUTRE_MER = {
    "971": "Guadeloupe",
    "972": "Martinique",
    "973": "Guyane",
    "974": "La Réunion",
    "975": "Saint-Pierre-et-Miquelon",
    "976": "Mayotte",
    "977": "Saint-Barthélemy",
    "978": "Saint-Martin",
    "986": "Wallis-et-Futuna",
    "987": "Polynésie française",
    "988": "Nouvelle-Calédonie",
}


def graphique_classement(donnees, colonne):
    # On trie les départements selon l'indicateur choisi
    # et on utilise le nombre d'accidents pour départager les égalités
    donnees = donnees.sort_values(
        [colonne, "accidents"], ascending=False
    ).copy()

    # On adapte les valeurs affichées selon qu'on regarde
    # les pourcentages ou le nombre d'accidents mortels
    if colonne == "part_mortels":
        donnees["valeur_affichee"] = donnees.apply(
            lambda ligne: (
                f"{ligne['part_mortels']:.2f} % · "
                f"{int(ligne['accidents_mortels']):,}/{int(ligne['accidents']):,}"
            ),
            axis=1,
        )
        titre_axe = "Proportion d'accidents mortels (%)"

    else:
        donnees["valeur_affichee"] = donnees.apply(
            lambda ligne: (
                f"{int(ligne['accidents_mortels']):,} mortels · "
                f"{int(ligne['accidents']):,} corporels"
            ),
            axis=1,
        )
        titre_axe = "Nombre d'accidents mortels"

    # On crée un graphique horizontal pour mieux lire les noms
    # des départements et comparer leurs résultats
    figure = px.bar(
        donnees,
        x=colonne,
        y="departement",
        orientation="h",
        text="valeur_affichee",
        custom_data=[
            "departement",
            "accidents",
            "accidents_mortels",
            "part_mortels"
        ],
    )

    # Au survol, on affiche les différentes valeurs
    # pour ne pas se limiter au chiffre visible sur la barre
    figure.update_traces(
        marker_color="#B84B52",
        textposition="outside",
        textfont_size=12,
        cliponaxis=False,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Accidents corporels : %{customdata[1]:,}<br>"
            "Accidents mortels : %{customdata[2]:,}<br>"
            "Proportion : %{customdata[3]:.2f} %<extra></extra>"
        ),
    )

    # On garde le classement dans l'ordre décroissant
    figure.update_yaxes(
        type="category",
        categoryorder="array",
        categoryarray=list(reversed(donnees["departement"].tolist())),
        automargin=True,
        title=None,
    )

    # On laisse de la place à droite pour afficher les valeurs
    # sans qu'elles soient coupées
    figure.update_xaxes(
        title=titre_axe,
        range=[0, donnees[colonne].max() * 1.48]
    )

    figure.update_layout(
        height=max(340, len(donnees) * 47 + 100),
        bargap=0.26,
        margin=dict(l=12, r=180, t=20, b=50),
        showlegend=False,
    )

    return figure


def afficher_classement(donnees, colonne, cle):
    # On affiche d'abord le classement sous forme de graphique
    with st.container(key=f"{cle}-graphique"):
        st.plotly_chart(
            graphique_classement(donnees, colonne),
            width="stretch"
        )

    # On prépare aussi une version en liste pour les petits écrans
    # avec les mêmes informations que dans le graphique
    lignes = []

    for ligne in donnees.sort_values(
        [colonne, "accidents"], ascending=False
    ).itertuples():

        # On sécurise le nom avant de l'insérer dans le HTML
        nom = escape(ligne.departement)

        valeur = (
            f"{ligne.part_mortels:.2f} %"
            if colonne == "part_mortels"
            else f"{int(ligne.accidents_mortels):,} mortels"
        )

        lignes.append(
            '<div class="fup-geo-row">'
            f'<strong>{nom}</strong><span>{valeur}</span>'
            f'<small>{int(ligne.accidents):,} accidents corporels · '
            f'{int(ligne.accidents_mortels):,} mortels · '
            f'{ligne.part_mortels:.2f} %</small></div>'
        )

    with st.container(key=f"{cle}-mobile"):
        st.markdown(
            '<div class="fup-geo-list">' + "".join(lignes) + "</div>",
            unsafe_allow_html=True,
        )


def render():
    # On charge les données qui vont servir à l'analyse géographique
    df = charger_accidents()

    st.divider()
    st.header("02 — La géographie des accidents")

    st.markdown("""
Notre première analyse a révélé un contraste important entre
les accidents survenus en agglomération et hors agglomération. Mais cette différence se retrouve-t-elle de la même manière
dans tous les territoires étudiés ? Pour répondre à cette question, nous allons comparer deux indicateurs :
le nombre d'accidents mortels et leur proportion parmi
les accidents corporels enregistrés.
""")

    # On regroupe les accidents par département pour connaître
    # le nombre total d'accidents et ceux qui sont mortels
    geo_df = (
        df.groupby("dep", as_index=False)
        .agg(
            accidents=("Num_Acc", "count"),
            accidents_mortels=("mortel", "sum")
        )
    )

    # On calcule le pourcentage d'accidents mortels dans chaque département
    # pour pouvoir comparer les territoires au-delà du nombre d'accidents
    geo_df["part_mortels"] = (
        geo_df["accidents_mortels"]
        / geo_df["accidents"]
        * 100
    )

    # On récupère les contours géographiques des départements
    # Le cache évite de refaire le téléchargement à chaque interaction
    @st.cache_data
    def charger_geojson():
        url = (
            "https://raw.githubusercontent.com/"
            "gregoiredavid/france-geojson/master/departements.geojson"
        )
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    st.subheader("Une France, des réalités différentes")

    # On laisse l'utilisateur choisir ce qu'il veut observer sur la carte
    indicateur = st.radio(
        "Choisir l'indicateur à afficher :",
        [
            "Nombre d'accidents mortels",
            "Proportion d'accidents mortels"
        ],
        horizontal=True
    )

    # On récupère la colonne correspondant à son choix
    # Elle sera utilisée pour la carte et les classements
    colonne = (
        "accidents_mortels"
        if indicateur == "Nombre d'accidents mortels"
        else "part_mortels"
    )

    # On sépare la métropole et l'outre-mer pour garder
    # une carte lisible sans oublier les territoires ultramarins
    noms_departements = OUTRE_MER.copy()
    geo_metro = geo_df[~geo_df["dep"].isin(OUTRE_MER)]

    try:
        geojson = charger_geojson()

        # On associe les codes des départements à leurs noms
        # pour les afficher plus clairement dans les classements
        noms_departements.update({
            feature["properties"]["code"]: feature["properties"]["nom"]
            for feature in geojson["features"]
        })

        # On crée la carte à partir des contours géographiques
        # La couleur dépend de l'indicateur sélectionné
        fig_carte = px.choropleth(
            geo_metro,
            geojson=geojson,
            locations="dep",
            featureidkey="properties.code",
            color=colonne,
            hover_name="dep",
            hover_data={
                "accidents": True,
                "accidents_mortels": True,
                "part_mortels": ":.2f",
                "dep": False
            },
            color_continuous_scale="Reds",
            labels={
                "accidents": "Accidents corporels",
                "accidents_mortels": "Accidents mortels",
                "part_mortels": "Part mortelle (%)"
            }
        )

        # On centre la carte sur les départements affichés
        fig_carte.update_geos(
            fitbounds="locations",
            visible=False
        )

        fig_carte.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=10, b=0)
        )

        st.plotly_chart(
            fig_carte,
            use_container_width=True
        )

        st.caption(
            "Carte : France métropolitaine uniquement. Les territoires ultramarins "
            "sont présentés séparément ci-dessous pour conserver une échelle lisible."
        )

    # Si le téléchargement des contours échoue,
    # on affiche un message plutôt que de bloquer toute la page
    except requests.RequestException:
        st.error(
            "Impossible de charger les contours des départements. "
            "Vérifie ta connexion Internet."
        )

    # On ajoute le nom de chaque département à son code
    # pour rendre les résultats plus faciles à identifier
    geo_df["departement"] = geo_df.apply(
        lambda ligne: (
            f"{noms_departements.get(ligne['dep'], ligne['dep'])} "
            f"({ligne['dep']})"
        ),
        axis=1,
    )

    geo_outre_mer = geo_df[geo_df["dep"].isin(OUTRE_MER)]

    # Les territoires ultramarins sont affichés séparément
    # mais restent pris en compte dans notre analyse
    st.subheader("Territoires ultramarins")
    afficher_classement(geo_outre_mer, colonne, "geo-outre-mer")

    st.caption(
        f"Outre-mer : {int(geo_outre_mer['accidents'].sum()):,} accidents corporels, "
        f"dont {int(geo_outre_mer['accidents_mortels'].sum()):,} mortels. "
        "Les proportions des territoires à faible effectif sont descriptives et instables."
    )

    st.subheader("Quels territoires ressortent le plus ?")

    # Quand on compare des pourcentages, un territoire avec très peu
    # d'accidents peut ressortir en tête alors que le résultat est fragile
    # On ajoute donc un seuil minimum que l'utilisateur peut modifier
    if colonne == "part_mortels":
        seuil_min = st.number_input(
            "Nombre minimal d'accidents corporels par territoire",
            min_value=1,
            value=100,
            step=25,
        )

        st.caption(
            "Le seuil limite les comparaisons fondées sur de petits effectifs ; "
            "il ne garantit pas leur significativité statistique."
        )

        candidats = geo_df[geo_df["accidents"] >= seuil_min]

    else:
        # Pour le nombre d'accidents mortels, on garde tous les territoires
        candidats = geo_df

    # On classe les territoires et on garde les dix premiers
    # pour éviter d'avoir un graphique trop chargé
    classement = candidats.sort_values(
        [colonne, "accidents"], ascending=False
    ).head(10)

    # On prévoit aussi le cas où aucun territoire ne respecte le seuil
    if classement.empty:
        st.warning("Aucun territoire ne satisfait le seuil sélectionné.")
    else:
        afficher_classement(classement, colonne, "geo-classement")

        st.caption(
            "Chaque entrée indique la valeur de l'indicateur, le nombre d'accidents "
            "mortels et l'effectif d'accidents corporels."
        )

    # On termine en expliquant la différence entre le nombre
    # d'accidents mortels et leur proportion
    st.markdown("""
### Comment interpréter cette carte ?

Le nombre d'accidents mortels permet d'identifier les territoires
où le bilan est le plus important en valeur absolue. La proportion d'accidents mortels quant à elle  indique, parmi les accidents corporels enregistrés
dans chaque territoire, la part ayant entraîné au moins un décès.

Ces deux indicateurs ne répondent donc pas à la même question.

Un territoire très peuplé ou fortement fréquenté peut enregistrer
beaucoup d'accidents, tandis qu'un territoire comptant moins
d'accidents peut présenter une proportion d'accidents mortels
plus élevée.

**Limite importante :** ces résultats ne tiennent pas compte
du nombre de trajets, des kilomètres parcourus ou de la population
exposée. Ils ne constituent donc pas un classement du risque
routier individuel.
""")

    st.info(
        "À retenir : pour identifier les territoires prioritaires, "
        "il est utile d'examiner à la fois le volume d'accidents mortels "
        "et leur proportion parmi les accidents corporels."
    )
