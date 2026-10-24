
import pandas as pd
import streamlit as st

from pages_app.data import ACCIDENTS_PATH, USAGERS_PATH, charger_accidents, charger_usagers


def render():
    # On vérifie d'abord que les deux fichiers sont présents
    # avant de calculer les chiffres de la conclusion
    indicateurs = None

    if ACCIDENTS_PATH.is_file() and USAGERS_PATH.is_file():
        accidents = charger_accidents()
        usagers = charger_usagers()

        # On récupère les accidents hors agglomération
        # et ceux qui ont eu lieu de nuit sans éclairage
        hors_agglomeration = accidents[accidents["agg"] == 1]
        nuit_sans_eclairage = accidents[accidents["lum"] == 3]

        # On calcule l'âge des usagers pour garder
        # uniquement les personnes âgées de 75 ans et plus
        age = 2024 - pd.to_numeric(usagers["an_nais"], errors="coerce")
        usagers_ages = usagers[age.between(75, 110)]

        # On calcule les trois pourcentages que l'on souhaite retenir
        # Les deux premiers concernent les accidents et le dernier les usagers
        indicateurs = (
            100 * hors_agglomeration["mortel"].sum() / len(hors_agglomeration),
            100 * nuit_sans_eclairage["mortel"].sum() / len(nuit_sans_eclairage),
            100 * usagers_ages["tue"].sum() / len(usagers_ages),
        )

    st.divider()
    st.header("06 — Ce que révèlent les données")

    st.markdown("""
Nous avons commencé cette étude avec une question :

**Comment les caractéristiques géographiques, temporelles
et les circonstances des accidents corporels sont-elles
associées à leur gravité sur les routes françaises en 2024 ?**

Les analyses précédentes montrent que la gravité
des accidents n'est pas répartie uniformément.

Certains territoires, certaines conditions de circulation
et certains profils d'usagers présentent des proportions
de conséquences mortelles plus élevées.

Trois enseignements ressortent particulièrement.
""")

    st.subheader("Trois enseignements à retenir")

    # Si les données sont absentes, on affiche un message
    # plutôt que de laisser l'application planter
    if indicateurs is None:
        st.warning("Indicateurs indisponibles : les fichiers CSV préparés sont absents.")
        valeurs = ("—", "—", "—")
    else:
        # On met les pourcentages au format français
        # avec deux chiffres après la virgule
        valeurs = tuple(f"{valeur:.2f}".replace(".", ",") + " %" for valeur in indicateurs)

    # On affiche les trois résultats côte à côte
    # pour résumer les principaux constats de notre étude
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Hors agglomération",
            valeurs[0]
        )
        st.markdown("""
    **Un contraste territorial**

    Parmi les accidents corporels survenus
    hors agglomération, environ un sur dix
    est mortel.

    Cette proportion est nettement supérieure
    à celle observée en agglomération.
    """)

    with col2:
        st.metric(
            "Nuit sans éclairage",
            valeurs[1]
        )
        st.markdown("""
    **Un contraste lié à la luminosité**

    Les accidents corporels enregistrés
    de nuit sans éclairage présentent
    une proportion de conséquences mortelles
    particulièrement élevée.

    Cette observation mérite une analyse
    approfondie des routes concernées.
    """)

    with col3:
        st.metric(
            "Usagers de 75 ans et plus",
            valeurs[2]
        )
        st.markdown("""
    **Une vulnérabilité humaine**

    Parmi les usagers âgés de 75 ans et plus
    impliqués dans un accident corporel,
    la proportion de personnes tuées
    est particulièrement élevée.

    Cela invite à porter une attention
    spécifique aux usagers âgés.
    """)

    st.divider()
    st.header("Quelles pistes pour améliorer la sécurité routière ?")

    st.markdown("""
Les résultats de notre analyse peuvent aider
les collectivités à identifier des situations
nécessitant une attention particulière.

Ils ne suffisent toutefois pas à déterminer
quelles interventions seront les plus efficaces.

Nous proposons trois pistes à approfondir.
""")

    # On utilise des menus déroulants pour présenter les recommandations
    # sans afficher trop de texte d'un seul coup
    with st.expander(
        "01 — Examiner les routes hors agglomération",
        expanded=True
    ):
        st.markdown("""
    Les accidents corporels hors agglomération
    présentent une proportion de conséquences
    mortelles plus élevée.

    **Pistes d'action :**
    - Identifier les axes cumulant un nombre important
      d'accidents mortels.
    - Examiner les caractéristiques des infrastructures.
    - Étudier les possibilités d'aménagement et de
      réduction des conflits entre usagers.

    Ces actions nécessitent des diagnostics locaux
    complémentaires.
    """)

    with st.expander(
        "02 — Étudier les conditions de circulation nocturne"
    ):
        st.markdown("""
    Les accidents survenus de nuit sans éclairage
    présentent une proportion élevée d'accidents mortels.

    **Pistes d'action :**
    - Identifier les secteurs concernés.
    - Examiner la visibilité et la signalisation.
    - Évaluer les besoins d'aménagement ou
      d'amélioration de la lisibilité des routes.

    Une proportion élevée ne prouve pas que
    l'absence d'éclairage soit la cause des décès.
    """)

    with st.expander(
        "03 — Mieux protéger les usagers vulnérables"
    ):
        st.markdown("""
    Les résultats montrent des différences importantes
    selon l'âge et la catégorie d'usager.

    **Pistes d'action :**
    - Examiner la sécurité des traversées piétonnes.
    - Étudier les aménagements autour des lieux
      fréquentés par les personnes âgées.
    - Adapter les actions de prévention aux situations
      identifiées localement.

    Les mesures envisagées doivent être confrontées
    aux caractéristiques réelles des déplacements.
    """)

    st.divider()
    st.header("Les limites de notre analyse")

    # On précise les limites pour éviter de tirer
    # des conclusions que les données ne permettent pas de prouver
    st.markdown("""
Les données BAAC 2024 constituent une source importante
pour étudier les accidents corporels de la circulation
routière en France.

Cependant, notre étude comporte plusieurs limites :

- **Périmètre des données :** les accidents sans dommage
  corporel ne sont pas inclus.
- **Absence de mesure d'exposition :** nous ne connaissons
  pas le nombre de trajets ou les kilomètres parcourus
  par chaque catégorie d'usager ou sur chaque route.
- **Analyse descriptive :** les associations observées
  ne permettent pas d'établir des relations de causalité.
- **Qualité des données :** certaines informations
  peuvent être manquantes, inconnues ou non renseignées.
- **Période étudiée :** nos conclusions portent sur
  l'année 2024 et ne démontrent pas une évolution
  à long terme.

Pour approfondir cette étude, il serait pertinent
de comparer plusieurs années et d'intégrer des
indicateurs d'exposition au trafic routier.
""")

    st.divider()

    st.header("Conclusion — Comprendre pour mieux prévenir")

    # On termine en répondant à la question de départ
    # et en rappelant l'intérêt de comparer plusieurs indicateurs
    st.markdown("""
Au début de cette étude, nous nous sommes demandé
si les endroits où les accidents étaient les plus
nombreux étaient également ceux où leurs conséquences
étaient les plus graves.

L'analyse des données BAAC 2024 nous a permis de
mettre en évidence une distinction essentielle :
**le nombre d'accidents ne suffit pas à décrire
leur gravité.**

Les contrastes observés entre agglomération et
hors agglomération, selon la luminosité ou selon
les profils d'usagers montrent l'intérêt d'une
analyse qui combine plusieurs dimensions.

Pour les collectivités, ces résultats peuvent
constituer un point de départ pour identifier
des territoires et des situations à examiner
plus précisément.

**La sécurité routière ne consiste pas seulement
à réduire le nombre d'accidents, mais aussi
à limiter la gravité de leurs conséquences.**

C'est tout l'enjeu de notre projet :
transformer des données en informations utiles
pour mieux comprendre et orienter la prévention.
""")
