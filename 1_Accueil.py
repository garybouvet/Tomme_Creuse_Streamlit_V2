import streamlit as st

st.set_page_config(
    page_title="MGC Cinéma",
    layout="wide"
)

logo_path = "./Logo/MGC_Cinema_Logo.png"

# Center the logo
st.markdown(
    """
    <style>
    .centered-image {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the centered logo at its original size without text
st.markdown(
    f"""
    <div class="centered-image">
        <img src="{logo_path}" alt="Tomme Creuse - Mission possible">
    </div>
    """,
    unsafe_allow_html=True
)
