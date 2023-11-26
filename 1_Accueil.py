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
    </style>
    """,
    unsafe_allow_html=True
)

# Afficher le logo centré avec les textes en dessous
st.markdown(
    f"""
    <div class="centered-image">
        <img src="data:image/png;base64,{resized_logo_base64}" alt="Tomme Creuse - Mission possible">
        <h1 style="margin-top: 20px;">MGC - Cinéma</h1>
    </div>
    """,
    unsafe_allow_html=True
)
