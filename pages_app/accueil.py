import base64

import streamlit as st

from pages_app.data import ROOT

def render():
    st.markdown(
        '<div class="fup-cover-heading">Projet  Data Analysis & Visualization </div>',
        unsafe_allow_html=True,
    )

    logo_path = ROOT / "assets" / "logo_efrei.png"
    if logo_path.exists():
        logo_base64 = base64.b64encode(logo_path.read_bytes()).decode("ascii")
        st.markdown(
            f'<div class="fup-logo"><img src="data:image/png;base64,{logo_base64}" '
            'alt="Logo EFREI Paris"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("Logo EFREI à ajouter")

    st.markdown("""
<div class="fup-academic">
    <div class="fup-academic-panel">
        <h3>Informations académiques</h3>
        <p><strong>Nom :</strong> KOUADIO</p>
        <p><strong>Prénom :</strong> Bli Jean Eudes</p>
        <p><strong>Classe :</strong> DE_02</p>
        <p><strong>Mail :</strong> bli-jean-eudes.kouadio@efrei.net</p>
    </div>
    <div class="fup-academic-panel">
        <h3>Encadrement</h3>
        <p><strong>Enseignant :</strong> Mathew Mano Joseph</p>
    </div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    st.markdown("""
<h1 class="fup-cover-title">FRANCE UNDER PRESSURE</h1>
<p class="fup-cover-subtitle">Comprendre la gravité des accidents corporels en France en 2024</p>
""", unsafe_allow_html=True)

    st.divider()


    # ==========================================
    # INTRODUCTION
    # ==========================================

    st.header("Introduction")

    st.markdown("""
Chaque année, des milliers d'accidents corporels sont
enregistrés sur les routes françaises. Mais une question mérite notre attention  **Les endroits où les accidents sont les plus nombreux
sont-ils aussi ceux où leurs conséquences sont les plus graves ?**
À travers les données officielles BAAC 2024, nous allons
explorer les différences de gravité selon les territoires,
les moments de la journée, les circonstances des accidents
et les profils des usagers impliqués. Notre objectif est de mieux comprendre ces contrastes
pour éclairer les décisions en matière de sécurité routière.
""")


    # ==========================================
    # PROBLÉMATIQUE
    # ==========================================

    st.subheader("Notre problématique")

    st.markdown("""
**Comment les caractéristiques géographiques, temporelles
et les circonstances des accidents corporels sont-elles
associées à leur gravité sur les routes françaises en 2024 ?**
""")


    # ==========================================
    # SOURCE DES DONNÉES
    # ==========================================

    st.divider()

    st.caption(
        "Source : ONISR — Bases de données annuelles des accidents "
        "corporels de la circulation routière (BAAC 2024)."
    )

