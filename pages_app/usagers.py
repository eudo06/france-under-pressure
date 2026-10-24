
import pandas as pd
import plotly.express as px
import streamlit as st

from pages_app.data import charger_usagers


def render():
    st.divider()
    st.header("05 — Derrière les accidents, des vies humaines")

    st.markdown("""
Jusqu'ici, nous avons étudié les accidents à travers leurs caractéristiques géographiques, temporelles
et environnementales. Mais chaque accident implique une ou plusieurs personnes. Nous allons maintenant changer d'échelle en effet
nous ne comptons plus les accidents, mais les usagers impliqués et les personnes tuées. Cette distinction est essentielle pour comprendre
quels profils présentent les proportions de décès les plus élevées parmi les usagers enregistrés.
""")

    # On charge cette fois les données des usagers
    # car on ne travaille plus sur les accidents mais sur les personnes impliquées
    df_usagers = charger_usagers()

    # Dans les données BAAC, le code 2 de la colonne grav correspond aux personnes tuées
    # On crée une colonne avec 1 pour les personnes tuées et 0 pour les autres
    df_usagers["tue"] = (
        pd.to_numeric(df_usagers["grav"], errors="coerce") == 2
    ).astype(int)

    # On remplace les codes des catégories par des noms
    # pour faciliter la lecture des résultats
    categories_usagers = {
        1: "Conducteurs",
        2: "Passagers",
        3: "Piétons"
    }

    df_usagers["categorie_usager"] = (
        df_usagers["catu"].map(categories_usagers)
    )

    # Même principe pour le sexe des usagers
    # Les valeurs inconnues sont conservées comme non renseignées
    df_usagers["sexe_label"] = df_usagers["sexe"].map({
        1: "Hommes",
        2: "Femmes"
    }).fillna("Non renseigné")

    # On calcule l'âge approximatif à partir de l'année de naissance
    # On convertit d'abord les valeurs pour éviter les erreurs de calcul
    df_usagers["an_nais"] = pd.to_numeric(
        df_usagers["an_nais"],
        errors="coerce"
    )

    df_usagers["age"] = 2024 - df_usagers["an_nais"]

    # On écarte les âges manquants ou incohérents
    df_usagers.loc[
        ~df_usagers["age"].between(0, 110),
        "age"
    ] = float("nan")

    # On regroupe les âges en plusieurs tranches
    # pour pouvoir comparer les profils plus facilement
    df_usagers["tranche_age"] = pd.cut(
        df_usagers["age"],
        bins=[-1, 17, 24, 34, 49, 64, 74, 110],
        labels=[
            "0–17 ans",
            "18–24 ans",
            "25–34 ans",
            "35–49 ans",
            "50–64 ans",
            "65–74 ans",
            "75 ans et plus"
        ]
    )

    # On crée une fonction pour réutiliser le même calcul
    # selon la catégorie d'usager, l'âge ou le sexe
    def analyser_usagers(data, colonne):
        resultat = (
            data.dropna(subset=[colonne])
            .groupby(colonne, observed=True, as_index=False)
            .agg(
                personnes=("tue", "size"),
                personnes_tuees=("tue", "sum")
            )
        )

        # Ici, on divise le nombre de personnes tuées
        # par le nombre total de personnes impliquées dans chaque groupe
        resultat["part_deces"] = (
            resultat["personnes_tuees"]
            / resultat["personnes"]
            * 100
        )

        return resultat

    # On affiche les principaux chiffres concernant les usagers
    nombre_usagers = len(df_usagers)
    nombre_deces = int(df_usagers["tue"].sum())

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Usagers enregistrés",
        f"{nombre_usagers:,}".replace(",", " ")
    )

    col2.metric(
        "Personnes tuées",
        f"{nombre_deces:,}".replace(",", " ")
    )

    col3.metric(
        "Part des usagers tués",
        f"{nombre_deces / nombre_usagers * 100:.2f} %"
    )

    st.caption(
        "Ces proportions concernent les personnes enregistrées "
        "dans les accidents corporels BAAC 2024, et non "
        "l'ensemble des usagers de la route."
    )

    st.subheader("5.1 — Tous les usagers sont-ils exposés aux mêmes conséquences ?")

    # On compare les conducteurs, les passagers et les piétons
    par_categorie = analyser_usagers(
        df_usagers,
        "categorie_usager"
    )

    # On classe les catégories selon leur proportion de décès
    # pour mieux voir les différences entre elles
    fig_categorie = px.bar(
        par_categorie.sort_values("part_deces"),
        x="part_deces",
        y="categorie_usager",
        orientation="h",
        text="part_deces",
        color="part_deces",
        color_continuous_scale="Reds",
        labels={
            "categorie_usager": "Catégorie d'usager",
            "part_deces": "Personnes tuées (%)"
        },
        hover_data=["personnes", "personnes_tuees"]
    )

    fig_categorie.update_traces(
        texttemplate="%{text:.2f} %",
        textposition="outside"
    )

    fig_categorie.update_layout(
        coloraxis_showscale=False,
        height=350
    )

    st.plotly_chart(fig_categorie, use_container_width=True)

    # On récupère la catégorie qui présente la plus forte proportion
    # pour afficher automatiquement son résultat dans le texte
    categorie_max = par_categorie.loc[
        par_categorie["part_deces"].idxmax()
    ]

    st.markdown(f"""
### Ce que nous observons

Les **{categorie_max['categorie_usager'].lower()}** présentent la proportion de décès la plus élevée
parmi les catégories d'usagers enregistrées :
**{categorie_max['part_deces']:.2f} %**. Cela ne signifie pas nécessairement que cette catégorie
a le risque de décès le plus élevé par déplacement. Nous comparons uniquement les personnes déjà impliquées
dans un accident corporel enregistré.
""")

    st.subheader("5.2 — L'âge et la gravité des conséquences")

    st.markdown("""
L'âge est une dimension importante à examiner lorsque nous étudions les conséquences humaines des accidents. Nous allons comparer la proportion de personnes tuées
parmi les usagers impliqués, selon leur tranche d'âge.
""")

    # On reprend la fonction pour comparer les différentes tranches d'âge
    par_age = analyser_usagers(
        df_usagers,
        "tranche_age"
    )

    # Le graphique permet de voir comment la proportion de décès
    # évolue selon l'âge des personnes impliquées
    fig_age = px.bar(
        par_age,
        x="tranche_age",
        y="part_deces",
        text="part_deces",
        color="part_deces",
        color_continuous_scale="Reds",
        labels={
            "tranche_age": "Tranche d'âge",
            "part_deces": "Personnes tuées (%)"
        },
        hover_data=["personnes", "personnes_tuees"]
    )

    fig_age.update_traces(
        texttemplate="%{text:.2f} %",
        textposition="outside"
    )

    fig_age.update_layout(
        coloraxis_showscale=False,
        height=430
    )

    st.plotly_chart(fig_age, use_container_width=True)

    # On identifie la tranche d'âge qui a la proportion de décès la plus élevée
    age_max = par_age.loc[
        par_age["part_deces"].idxmax()
    ]

    st.markdown(f"""
### Une différence marquée selon l'âge

La tranche **{age_max['tranche_age']}** présente
la proportion de décès la plus élevée :
**{age_max['part_deces']:.2f} %** parmi les
personnes de cette tranche d'âge impliquées dans un accident corporel enregistré. Ce contraste peut notamment être lié à la
vulnérabilité physique, mais nos données descriptives ne permettent pas d'isoler les mécanismes responsables. Il faudra également tenir compte du mode de déplacement
et des circonstances des accidents.
""")

    # On indique combien de personnes n'ont pas pu être prises
    # en compte dans l'analyse par âge
    st.caption(
        f"Âge manquant ou non exploitable pour "
        f"{df_usagers['age'].isna().sum():,} usagers."
    )

    st.subheader("5.3 — Observe-t-on une différence selon le sexe ?")

    # Pour cette comparaison, on garde uniquement les usagers
    # dont le sexe est renseigné
    par_sexe = analyser_usagers(
        df_usagers[
            df_usagers["sexe_label"].isin(["Hommes", "Femmes"])
        ],
        "sexe_label"
    )

    fig_sexe = px.bar(
        par_sexe,
        x="sexe_label",
        y="part_deces",
        text="part_deces",
        color="sexe_label",
        labels={
            "sexe_label": "Sexe",
            "part_deces": "Personnes tuées (%)"
        },
        hover_data=["personnes", "personnes_tuees"]
    )

    fig_sexe.update_traces(
        texttemplate="%{text:.2f} %",
        textposition="outside"
    )

    fig_sexe.update_layout(
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig_sexe, use_container_width=True)

    # On précise le nombre de valeurs exclues
    # pour que l'utilisateur sache sur quelles données repose la comparaison
    st.caption(
        f"{int((~df_usagers['sexe_label'].isin(['Hommes', 'Femmes'])).sum()):,} "
        "usagers au sexe non renseigné sont exclus de cette comparaison."
    )

    st.markdown("""
### Comment interpréter cette différence ?

Une différence de proportion de décès entre hommes
et femmes peut être observée dans les données.

Cependant, elle ne permet pas de conclure que le sexe
explique directement cette différence.

Les types de déplacements, les véhicules utilisés,
les horaires et les circonstances des accidents
peuvent varier entre les groupes.
""")

    st.subheader("5.4 — Quels profils cumulent les proportions les plus élevées ?")

    # On croise cette fois les tranches d'âge avec les catégories d'usagers
    # pour aller plus loin qu'une analyse séparée de chaque variable
    croisement = (
        df_usagers.dropna(
            subset=["tranche_age", "categorie_usager"]
        )
        .groupby(
            ["tranche_age", "categorie_usager"],
            observed=True,
            as_index=False
        )
        .agg(
            personnes=("tue", "size"),
            personnes_tuees=("tue", "sum")
        )
    )

    # On calcule la proportion de décès pour chaque combinaison
    # par exemple les piétons de 75 ans et plus
    croisement["part_deces"] = (
        croisement["personnes_tuees"]
        / croisement["personnes"]
        * 100
    )

    # On masque les groupes qui comptent moins de 30 personnes
    # pour éviter de mettre en avant des pourcentages trop fragiles
    croisement.loc[
        croisement["personnes"] < 30,
        "part_deces"
    ] = float("nan")

    # On transforme les résultats en matrice
    # avec les âges en lignes et les catégories en colonnes
    matrice_usagers = croisement.pivot(
        index="tranche_age",
        columns="categorie_usager",
        values="part_deces"
    )

    # On utilise une heatmap pour repérer plus facilement
    # les groupes qui présentent les proportions les plus élevées
    fig_croisement = px.imshow(
        matrice_usagers,
        color_continuous_scale="Reds",
        aspect="auto",
        text_auto=".1f",
        labels={
            "x": "Catégorie d'usager",
            "y": "Tranche d'âge",
            "color": "Personnes tuées (%)"
        }
    )

    fig_croisement.update_layout(height=480)

    st.plotly_chart(
        fig_croisement,
        use_container_width=True
    )

    st.caption(
        "Les groupes de moins de 30 personnes sont masqués. "
        "Les pourcentages sont calculés parmi les personnes "
        "impliquées dans un accident corporel enregistré."
    )

    st.divider()

    # On termine en rappelant que les différences observées
    # concernent les personnes déjà impliquées dans un accident
    st.markdown("""
### Ce que nous retenons

L'analyse des usagers nous permet de compléter
notre compréhension des accidents de la route.

Les différences de gravité ne concernent pas
uniquement les lieux et les circonstances :
elles apparaissent également entre les profils
des personnes impliquées.

L'âge et la catégorie d'usager révèlent notamment
des contrastes importants.

**Une priorité se dessine : mieux comprendre
les situations dans lesquelles les usagers
les plus vulnérables subissent les conséquences
les plus graves.**

Ces résultats pourront nourrir des pistes de prévention,
à condition de tenir compte des limites des données
et de ne pas confondre association et causalité.
""")
