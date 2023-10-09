import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Découverte de Films",
    layout="wide"
)

# Page title
st.markdown(
    """
    <div class="centered-text">
        <h1>🔍 Découverte aléatoire</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Styling: CSS personnalisé
st.markdown(
    """
    <style>
    .filter-title {
        font-size: 24px;
        border: 2px solid #F0B900;
        border-radius: 10px;
        padding: 5px;
        text-align: center;
    }
    .centered-text {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    div[data-baseweb="select"] > div {
        border: 2px solid #F0B900 !important;
    }
    button {
        border: 2px solid #F0B900 !important;
        background-color: transparent !important;
        color: #F0B900 !important;
    }
    button:hover {
        background-color: #F0B900 !important;
        color: #ffffff !important;
    }
    button:active {
        background-color: #F0B900 !important;
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: transparent;
        color: white; 
        border: 1px solid #F0B900; 
    }
    .stButton>button:hover {
        color: #F0B900; 
        border-color: #F0B900; 
    }
    .stButton>button:active {
        background-color: #F0B900; 
        color: white; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Titre du filtre avec marge en dessous
st.sidebar.markdown(
    """
    <style>
    .filter-title {
        font-size: 24px;
        border: 2px solid #F0B900;
        border-radius: 10px;
        padding: 5px;
        text-align: center;
        margin-bottom: 20px;  /* Ajoutez cette ligne pour la marge en dessous */
    }
    </style>
    <div class="filter-title">
        FILTRE
    </div>
    """,
    unsafe_allow_html=True
)

# Chargement des données
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("./Data_base/df_ML_modif.csv").drop_duplicates(subset="title", keep='first')

# Prétraitement des studios
@st.cache_data(show_spinner=False)
def preprocess_studios(df):
    return (
        df['production_companies_name_y']
        .str.replace('"', '')
        .str.split(',')
        .explode()
        .str.strip()
    )

# Calcul de la similarité cosinus
@st.cache_data(show_spinner=False)
def calculate_cosine_similarity(df):
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df['combined_features'])
    return cosine_similarity(count_matrix)

# Chargement et prétraitement des données
df = load_data()
cosine_sim = calculate_cosine_similarity(df)
studios = preprocess_studios(df)


# Interface utilisateur: Filtres
genres = df['genres'].str.get_dummies(sep=',').columns.tolist()
genres_filter = st.sidebar.multiselect("Filtrer par genre", options=genres)

studio_options = ['⭐️ POPULAIRE ⭐️'] + studios.value_counts().nlargest(10).index.tolist() + ['-' * 54] + studios.unique().tolist()
selected_studios = st.sidebar.multiselect("Studio", options=studio_options)

rating_range = st.sidebar.slider("Notes :", min_value=0.0, max_value=9.5, step=0.5, value=(0.0, 9.5), key="rating_slider")

# Fonction pour obtenir l'URL du poster
@st.cache_data(show_spinner=False)
def poster_url(title):
    poster_path = df[df['title'] == title]['poster_path_y'].values[0]
    return f'https://image.tmdb.org/t/p/w500{poster_path}'

# Génération de films aléatoires
if st.button("👉 Générer des films aléatoires", key="random_button"):
    random_df_filtered = df.copy()

    # Appliquer les filtres
    if genres_filter:
        random_df_filtered = random_df_filtered[random_df_filtered['genres'].str.contains('|'.join(genres_filter))]
    
    if selected_studios:
        # Note: il peut être nécessaire de répéter le prétraitement ici si votre implémentation du filtre le nécessite
        random_df_filtered = random_df_filtered[random_df_filtered['production_companies_name_y'].isin(selected_studios)]
    
    random_df_filtered = random_df_filtered[
        (random_df_filtered['averageRating'] >= rating_range[0]) & 
        (random_df_filtered['averageRating'] <= rating_range[1])
    ]

    # Sélectionner aléatoirement des films
    num_random_movies = min(8, len(random_df_filtered))
    random_movies = random_df_filtered.sample(n=num_random_movies)

    # Afficher les films
    cols = st.columns(4)
    for i, movie in enumerate(random_movies.itertuples()):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div style='margin: 0 0 20px 0; border: 1px solid #9E9E9E; border-radius: 16px; overflow: hidden;'>
                    <div style='height: 300px; overflow: hidden;'>
                        <img src='{poster_url(movie.title)}' style='width: 100%; height: 100%; object-fit: cover;'>
                    </div>
                    <div style='background-color: black; padding: 10px; min-height: 185px;'>
                        <div style='text-align: left; color: white;'>
                            <span style='color: gold; font-size: 22px;'>★</span> <span style='font-size: 16px;'>{movie.averageRating}</span>
                        </div>
                        <div style='text-align: left; color: white; font-weight: bold;'>
                            {movie.title}
                        </div>
                        <div style='text-align: left; color: white;'>
                            ({int(movie.startYear)})
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

