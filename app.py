
from importlib import import_module

import streamlit as st

# On configure l'apparence générale de l'application
# avec son titre, son icône et un affichage sur toute la largeur
st.set_page_config(
    page_title="France Under Pressure | EFREI Paris",
    
    layout="wide",
    initial_sidebar_state="expanded",
)

# On regroupe les différentes pages dans un dictionnaire
# pour pouvoir les retrouver facilement dans le menu
PAGES = {
    "Accueil": "accueil",
    "01 — Comprendre la gravité": "gravite",
    "02 — Géographie des accidents": "geographie",
    "03 — Analyse temporelle": "temporalite",
    "04 — Circonstances des accidents": "circonstances",
    "05 — Profils des usagers": "usagers",
    "06 — Conclusions et recommandations": "conclusions",
}

# On crée le menu sur le côté pour naviguer entre les chapitres
with st.sidebar:
    st.title("France Under Pressure")
    st.caption("EFREI Paris | BAAC 2024")
    st.divider()

    # Le choix de l'utilisateur permet de déterminer
    # quelle page sera affichée
    page = st.radio("Navigation", list(PAGES), label_visibility="collapsed")

    st.divider()
    st.caption("Projet de Data Visualization & Storytelling")
    st.caption("Bli Jean Eudes KOUADIO")

# On utilise du CSS pour personnaliser l'affichage de Streamlit
# et garder une présentation cohérente entre les différentes pages
st.markdown("""
<style>
    /* On limite la largeur du contenu pour faciliter la lecture */
    .block-container {
        max-width: 1100px;
        padding-top: 2.5rem;
        padding-left: clamp(1rem, 3vw, 2rem);
        padding-right: clamp(1rem, 3vw, 2rem);
    }

    /* On ajuste les paragraphes pour éviter les textes trop étalés */
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] p {
        max-width: min(100%, 850px);
        text-align: justify;
        text-align-last: left;
        line-height: 1.4;
        margin-top: 0;
        margin-bottom: 0.5rem;
        hyphens: none;
        overflow-wrap: break-word;
    }

    [data-testid="stMain"] [data-testid="stMarkdownContainer"] p:last-child {
        margin-bottom: 0;
    }

    [data-testid="stMain"] [data-testid="stAlert"] p {
        text-align: left;
    }

    /* On rend les titres plus visibles */
    h1 {
        font-size: 2.6rem !important;
        font-weight: 800 !important;
    }

    h2, h3 {
        font-weight: 650 !important;
    }

    [data-testid="stImage"] img {
        object-fit: contain;
    }

    /* Mise en forme de la page d'accueil */
    .fup-cover-heading {
        text-align: center;
        margin: 0 auto 1.1rem;
        color: inherit;
        font-size: clamp(1.1rem, 2.4vw, 1.5rem);
        font-weight: 600;
        letter-spacing: 0.025em;
    }

    .fup-logo {
        display: flex;
        justify-content: center;
        margin: 0 auto 1.2rem;
    }

    .fup-logo img {
        display: block;
        width: 170px;
        max-width: 100%;
        height: auto;
    }

    .fup-academic {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 2rem;
        margin: 1.35rem 0 1.6rem;
    }

    .fup-academic-panel {
        padding: 1.1rem 1.35rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 0.55rem;
    }

    .fup-academic-panel h3 {
        margin: 0 0 0.8rem;
        font-size: 1.05rem;
    }

    [data-testid="stMain"] .fup-academic-panel p {
        text-align: left;
        line-height: 1.4;
        margin: 0.3rem 0;
    }

    .fup-cover-title {
        text-align: center;
        margin: 1.4rem 0 0.35rem;
        font-size: clamp(2rem, 5vw, 3.1rem);
        font-weight: 800;
        letter-spacing: 0.03em;
    }

    [data-testid="stMain"] .fup-cover-subtitle {
        text-align: center;
        line-height: 1.4;
        margin: 0 auto 1.35rem;
        max-width: 46rem;
        font-size: clamp(1rem, 2.2vw, 1.25rem);
    }

    /* Sur ordinateur, on affiche les graphiques des départements */
    .st-key-geo-outre-mer-mobile,
    .st-key-geo-classement-mobile {
        display: none;
    }

    .fup-geo-row {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 0.2rem 0.7rem;
        padding: 0.65rem 0;
        border-bottom: 1px solid rgba(128, 128, 128, 0.22);
        font-size: 0.9rem;
    }

    .fup-geo-row small {
        grid-column: 1 / -1;
        opacity: 0.78;
    }

    /* Sur téléphone, on adapte les textes et les graphiques
       pour que l'application reste facile à consulter */
    @media (max-width: 640px) {
        .block-container { padding-top: 4rem; }

        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p {
            text-align: left;
        }

        .fup-academic {
            grid-template-columns: 1fr;
            gap: 0.75rem;
        }

        .fup-academic-panel {
            padding: 0.9rem 1rem;
        }

        [data-testid="stMain"] [data-testid="stMarkdownContainer"] .fup-cover-subtitle {
            text-align: center;
        }

        .st-key-geo-outre-mer-graphique,
        .st-key-geo-classement-graphique {
            display: none;
        }

        .st-key-geo-outre-mer-mobile,
        .st-key-geo-classement-mobile {
            display: block;
        }
    }
</style>
""", unsafe_allow_html=True)

# On récupère le fichier correspondant à la page choisie
# puis on appelle sa fonction render pour afficher son contenu
import_module(f"pages_app.{PAGES[page]}").render()
