
import pandas as pd
import plotly.express as px
import streamlit as st

from pages_app.data import ROOT, charger_accidents


LIEUX_PATH = ROOT / "data" / "raw" / "lieux-2024.csv"


def render():
    df = charger_accidents()

    st.divider()
    st.header("04 — Les circonstances des accidents")

    st.markdown("""
Nous avons observé des différences de gravité selon
les territoires et les horaires. Mais ces contrastes peuvent-ils être associés aux
conditions dans lesquelles les accidents surviennent ?
Nous allons examiner la luminosité, la météo, les
limitations de vitesse et les types de collision.
""")

    df_circ = df.copy()

    # Les données BAAC utilisent des codes numériques
    # On les remplace par des noms pour mieux comprendre les graphiques
    lum_labels = {
        1: "Plein jour",
        2: "Crépuscule / aube",
        3: "Nuit sans éclairage",
        4: "Nuit avec éclairage éteint",
        5: "Nuit avec éclairage allumé"
    }

    meteo_labels = {
        1: "Normales",
        2: "Pluie légère",
        3: "Pluie forte",
        4: "Neige / grêle",
        5: "Brouillard / fumée",
        6: "Vent fort / tempête",
        7: "Temps éblouissant",
        8: "Temps couvert",
        9: "Autres"
    }

    collision_labels = {
        1: "Deux véhicules - frontale",
        2: "Deux véhicules - arrière",
        3: "Deux véhicules - côté",
        4: "Trois véhicules ou plus - chaîne",
        5: "Trois véhicules ou plus - multiples",
        6: "Autre collision",
        7: "Sans collision"
    }

    # On crée de nouvelles colonnes avec les noms des catégories
    df_circ["luminosite"] = df_circ["lum"].map(lum_labels)
    df_circ["meteo"] = df_circ["atm"].map(meteo_labels)
    df_circ["collision"] = df_circ["col"].map(collision_labels)

    # On utilise la même fonction pour calculer la gravité
    # selon la luminosité, la météo, la vitesse ou les collisions
    def calculer_gravite(data, colonne):
        # On regroupe les accidents par catégorie
        # puis on compte le total et ceux qui sont mortels
        resultat = (
            data.dropna(subset=[colonne])
            .groupby(colonne, as_index=False)
            .agg(
                accidents=("Num_Acc", "count"),
                mortels=("mortel", "sum")
            )
        )

        # On calcule le pourcentage d'accidents mortels
        # par rapport au total de chaque catégorie
        resultat["part_mortels"] = (
            resultat["mortels"]
            / resultat["accidents"]
            * 100
        )

        return resultat

    st.subheader("4.1 — La luminosité : un premier facteur de contraste")

    st.markdown("""
La circulation nocturne présente des caractéristiques
différentes de la circulation de jour. La visibilité peut être réduite, et les routes ne sont
pas toutes équipées d'un éclairage public.
Voyons comment la proportion d'accidents mortels
varie selon les conditions de luminosité.
""")

    # On applique notre fonction aux différentes conditions de luminosité
    par_lum = calculer_gravite(df_circ, "luminosite")

    # On classe les conditions selon leur proportion d'accidents mortels
    # pour voir plus facilement celles qui ressortent
    fig_lum = px.bar(
        par_lum.sort_values("part_mortels"),
        x="part_mortels",
        y="luminosite",
        orientation="h",
        text="part_mortels",
        color="part_mortels",
        color_continuous_scale="Reds",
        labels={
            "luminosite": "Luminosité",
            "part_mortels": "Accidents mortels (%)"
        }
    )

    fig_lum.update_traces(
        texttemplate="%{text:.2f} %",
        textposition="outside"
    )

    fig_lum.update_layout(
        coloraxis_showscale=False,
        height=420
    )

    st.plotly_chart(fig_lum, use_container_width=True)

    # On récupère les résultats de nuit sans éclairage et de plein jour
    # pour pouvoir les comparer directement dans notre interprétation
    nuit = par_lum.loc[
        par_lum["luminosite"] == "Nuit sans éclairage"
    ].iloc[0]

    jour = par_lum.loc[
        par_lum["luminosite"] == "Plein jour"
    ].iloc[0]

    st.markdown(f"""
### Ce que nous découvrons

Lors des accidents corporels survenus de nuit,
sans éclairage public, **{nuit['part_mortels']:.2f} %**
ont été mortels. En plein jour, cette proportion est de
**{jour['part_mortels']:.2f} %**. La proportion observée de nuit sans éclairage est
donc environ **{nuit['part_mortels'] / jour['part_mortels']:.1f}
fois celle observée en plein jour**.

Ce résultat met en évidence un contraste important,
mais ne démontre pas que l'absence d'éclairage
est à elle seule responsable de cette différence.
Les types de routes et les conditions de circulation
peuvent également intervenir.
""")

    st.subheader("4.2 — Les conditions météorologiques")

    st.markdown("""
La pluie, le brouillard, la neige ou le vent
peuvent modifier les conditions de conduite. Cependant, une météo difficile n'implique pas
automatiquement une proportion plus élevée
d'accidents mortels. Examinons les données pour voir si cela est vrai.
""")

    # On reprend le même calcul pour comparer les conditions météo
    par_meteo = calculer_gravite(df_circ, "meteo")

    fig_meteo = px.bar(
        par_meteo.sort_values("part_mortels"),
        x="part_mortels",
        y="meteo",
        orientation="h",
        color="part_mortels",
        text="part_mortels",
        color_continuous_scale="Reds",
        labels={
            "meteo": "Conditions météorologiques",
            "part_mortels": "Accidents mortels (%)"
        }
    )

    fig_meteo.update_traces(
        texttemplate="%{text:.2f} %",
        textposition="outside"
    )

    fig_meteo.update_layout(
        coloraxis_showscale=False,
        height=450
    )

    st.plotly_chart(fig_meteo, use_container_width=True)

    # On cherche la catégorie météo qui présente
    # la proportion d'accidents mortels la plus élevée
    meteo_max = par_meteo.loc[
        par_meteo["part_mortels"].idxmax()
    ]

    st.markdown(f"""
### Ce que nous observons

La catégorie météorologique présentant la plus forte
proportion d'accidents mortels est
**{meteo_max['meteo']}**, avec
**{meteo_max['part_mortels']:.2f} %**. Cette catégorie représente
**{int(meteo_max['accidents']):,} accidents corporels**. Il faut toutefois examiner les effectifs par exemple
une proportion calculée sur peu d'accidents
est moins stable qu'une proportion calculée
sur plusieurs milliers d'observations.
""")

    # On vérifie que le fichier des lieux est disponible
    # avant de commencer l'analyse des limitations de vitesse
    if LIEUX_PATH.exists():

        st.subheader("4.3 — La limitation de vitesse et la gravité")

        st.markdown("""
Les routes françaises présentent des limitations
de vitesse différentes selon leur configuration. Nous allons comparer la proportion d'accidents mortels
selon la vitesse maximale autorisée sur les lieux. Il ne s'agit pas de mesurer les excès de vitesse,
car la vitesse réelle des véhicules n'est pas
disponible dans cette variable.
""")

        # On charge les limitations de vitesse depuis le fichier des lieux
        # Le cache permet de ne pas relire le fichier à chaque interaction
        @st.cache_data
        def charger_vitesses(version):
            lieux = pd.read_csv(
                LIEUX_PATH,
                sep=";",
                dtype={"Num_Acc": str},
                low_memory=False
            )

            # On convertit les vitesses en nombres
            # et on écarte les valeurs invalides ou hors de la plage retenue
            lieux["vma"] = pd.to_numeric(
                lieux["vma"],
                errors="coerce"
            )

            lieux["vma"] = lieux["vma"].where(
                lieux["vma"].between(10, 130)
            )

            # Un accident peut apparaître plusieurs fois dans ce fichier
            # On vérifie donc combien de vitesses différentes lui sont associées
            vitesses = (
                lieux.dropna(subset=["vma"])
                .groupby("Num_Acc")["vma"]
                .agg(["nunique", "first"])
                .reset_index()
            )

            # On garde seulement les accidents qui ont
            # une seule limitation de vitesse valide
            vitesses = vitesses[
                vitesses["nunique"] == 1
            ].copy()

            return vitesses[["Num_Acc", "first"]].rename(
                columns={"first": "vma"}
            )

        # On utilise les informations du fichier pour actualiser le cache
        # si le fichier des lieux est modifié
        statistiques_lieux = LIEUX_PATH.stat()
        vitesses = charger_vitesses(
            (statistiques_lieux.st_mtime_ns, statistiques_lieux.st_size)
        )

        # On relie les vitesses aux accidents grâce à leur identifiant Num_Acc
        # La jointure garde tous les accidents, même sans vitesse exploitable
        df_vitesse = df_circ.merge(
            vitesses,
            on="Num_Acc",
            how="left",
            validate="one_to_one"
        )

        # On regroupe les limitations de vitesse par tranches
        # pour rendre la comparaison plus simple
        df_vitesse["categorie_vitesse"] = pd.cut(
            df_vitesse["vma"],
            bins=[0, 30, 50, 70, 90, 130],
            labels=[
                "≤ 30 km/h",
                "31–50 km/h",
                "51–70 km/h",
                "71–90 km/h",
                "91–130 km/h"
            ],
            include_lowest=True
        )

        # On calcule la proportion d'accidents mortels
        # dans chaque tranche de limitation de vitesse
        par_vitesse = calculer_gravite(
            df_vitesse,
            "categorie_vitesse"
        )

        fig_vitesse = px.bar(
            par_vitesse,
            x="categorie_vitesse",
            y="part_mortels",
            text="part_mortels",
            color="part_mortels",
            color_continuous_scale="Reds",
            labels={
                "categorie_vitesse": "Vitesse maximale autorisée",
                "part_mortels": "Accidents mortels (%)"
            }
        )

        fig_vitesse.update_traces(
            texttemplate="%{text:.2f} %",
            textposition="outside"
        )

        fig_vitesse.update_layout(
            coloraxis_showscale=False,
            height=430
        )

        st.plotly_chart(fig_vitesse, use_container_width=True)

        # On indique combien d'accidents ont été exclus
        # pour que l'utilisateur sache sur quelles données repose le graphique
        st.caption(
            f"Analyse réalisée sur {len(vitesses):,} accidents "
            "disposant d'une limitation de vitesse valide et unique. "
            f"{len(df_circ) - len(vitesses):,} accidents, dont "
            f"{int(df_circ.loc[~df_circ['Num_Acc'].isin(vitesses['Num_Acc']), 'mortel'].sum()):,} mortels, "
            "sont exclus de ce graphique."
        )

        # On récupère la tranche qui présente la plus forte proportion
        # pour générer automatiquement le texte d'interprétation
        vitesse_max = par_vitesse.loc[
            par_vitesse["part_mortels"].idxmax()
        ]

        st.markdown(f"""
### Ce que nous apprennent les données

La catégorie **{vitesse_max['categorie_vitesse']}** présente la proportion d'accidents mortels
la plus élevée parmi les catégories étudiées, avec **{vitesse_max['part_mortels']:.2f} %**. Cette différence peut être associée à plusieurs
caractéristiques des routes et des déplacements. Nous ne pouvons donc pas conclure qu'une limitation de vitesse donnée provoque directement une gravité plus élevée en effet d'autres facteurs peuvent expliquer
une partie du contraste.
""")

    else:
        st.warning(
            "Fichier data/raw/lieux-2024.csv introuvable : analyse des limitations de vitesse indisponible."
        )

    st.subheader("4.4 — Les types de collision")

    st.markdown("""
Une collision frontale, latérale ou arrière
ne présente pas nécessairement les mêmes conséquences. Nous allons ainsi comparer les différentes configurations
de collision enregistrées dans les données BAAC.
""")

    # On applique notre fonction aux différents types de collision
    par_collision = calculer_gravite(
        df_circ,
        "collision"
    )

    # On classe les collisions selon leur proportion d'accidents mortels
    # pour faciliter la comparaison entre les catégories
    fig_collision = px.bar(
        par_collision.sort_values("part_mortels"),
        x="part_mortels",
        y="collision",
        orientation="h",
        text="part_mortels",
        color="part_mortels",
        color_continuous_scale="Reds",
        labels={
            "collision": "Type de collision",
            "part_mortels": "Accidents mortels (%)"
        }
    )

    fig_collision.update_traces(
        texttemplate="%{text:.2f} %",
        textposition="outside"
    )

    fig_collision.update_layout(
        coloraxis_showscale=False,
        height=450
    )

    st.plotly_chart(fig_collision, use_container_width=True)

    # On identifie le type de collision avec la plus forte proportion
    # pour l'afficher dans notre interprétation
    collision_max = par_collision.loc[
        par_collision["part_mortels"].idxmax()
    ]

    st.markdown(f"""
### Ce que nous observons

La catégorie **{collision_max['collision']}**
présente la proportion d'accidents mortels
la plus élevée, avec
**{collision_max['part_mortels']:.2f} %**. Cette analyse montre que la configuration
de l'accident constitue une dimension importante
pour décrire sa gravité. Cependant, le type de collision peut également
être associé à la vitesse, au type de route
et aux caractéristiques des véhicules impliqués.
""")

    st.divider()

    # On termine le chapitre en résumant les principaux constats
    # avant de passer à l'analyse des personnes impliquées
    st.markdown("""
### Ce que nous retenons

Notre analyse révèle plusieurs contrastes entre les circonstances des accidents corporels. La luminosité, la météo, les limitations de vitesse
et les types de collision sont associés à des
proportions d'accidents mortels différentes.Mais ces caractéristiques peuvent se cumuler. Un accident nocturne hors agglomération peut,
par exemple, se produire sur une route dont
la limitation de vitesse est élevée.

**Pour aller plus loin, nous devons maintenant
nous intéresser aux personnes impliquées.**

Les conséquences des accidents sont-elles
les mêmes selon l'âge, le sexe ou la catégorie
des usagers ?

C'est l'objet de notre prochain chapitre.
""")
