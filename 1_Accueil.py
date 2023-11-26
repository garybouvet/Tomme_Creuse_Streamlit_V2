import streamlit as st
import base64
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="MGC Cinéma",
    layout="wide"
)

logo_path = "./Logo/logo_tomme_creuse.png"
logo_image = Image.open(logo_path)
resized_logo = logo_image.resize((300, 300))

# Convertir l'image redimensionnée en base64
buffered = BytesIO()
resized_logo.save(buffered, format="PNG")
resized_logo_base64 = base64.b64encode(buffered.getvalue()).decode()

# Centrer le logo
st.markdown(
    f"""
    <style>
    .centered-image {{
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }}
    .custom-list {{
        text-align: left;
        margin-top: 40px;
        line-height: 1.2;  /* Adjust line spacing as needed */
        font-size: 18px;  /* Adjust font size as needed */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Afficher le logo centré avec la description en dessous
st.markdown(
    f"""
    <div class="centered-image">
        <img src="data:image/png;base64,{resized_logo_base64}" alt="Tomme Creuse - Mission possible">
        <ul class="custom-list">
            <li> Collecte et nettoyage de données depuis IMDB</li>
            <li> Enrichissement automatisé à partir de TMDB via API</li>
            <li> Développement d'un moteur de Machine Learning (Cosine similarity) pour des recommandations de films</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)
