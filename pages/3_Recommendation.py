

import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------- CONFIGURATION -----------------------
st.set_page_config(page_title="Recommandation de Films", layout="wide")

# ----------------------- HIDE 'MADE WITH STREAMLIT' -----------------------
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ----------------------- LOAD DATA -----------------------
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("./Data_base/df_ML_modif.csv").drop_duplicates(subset="title", keep='first')
    df['production_companies_name_y'] = df['production_companies_name_y'].str.replace('"', '').str.replace("'", '')
    return df

df = load_data()

@st.cache_data(show_spinner=False)
def calculate_cosine_similarity(df):
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df['combined_features'])
    return cosine_similarity(count_matrix)

cosine_sim = calculate_cosine_similarity(df)

# ----------------------- UTILITY FUNCTIONS -----------------------
def title_from_index(index, df):
    return df[df.index == index]["title"].values[0]

def index_from_title(title, df):
    return df[df.title.str.lower() == title.lower()]["index"].values[0]

def find_similar_movies(movie_title, num_movies, df, cosine_sim, genres_filter, selected_studios, rating_range):
    movie_index = index_from_title(movie_title, df)
    similar_movies = list(enumerate(cosine_sim[movie_index]))
    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:num_movies + 1]
    filtered_movies = []
    for idx, sim_score in sorted_similar_movies:
        movie = df.iloc[idx]
        genres = set(movie['genres'].split(','))
        studio = movie['production_companies_name_y']
        rating = movie['averageRating']
        if (not genres_filter or genres.intersection(genres_filter)) and \
           (not selected_studios or studio in selected_studios) and \
           rating_range[0] <= rating <= rating_range[1]:
            filtered_movies.append(idx)
    return [title_from_index(idx, df) for idx in filtered_movies]

# Ajoutez une fonction pour mettre à jour les films recommandés en fonction des filtres
def update_filtered_movies(selected_movie, genres_filter, selected_studios, rating_range):
    all_similar_movies = find_similar_movies(selected_movie, 100, df, cosine_sim, genres_filter, selected_studios, rating_range)
    return all_similar_movies

def poster_url(title, df):
    try:
        poster_path = df[df['title'] == title]['poster_path_y'].values[0]
        return 'https://image.tmdb.org/t/p/w500' + poster_path
    except Exception as e:
        st.error(f"Error for {title}: {str(e)}")
        return None

# ----------------------- STYLES -----------------------
st.markdown(
    """
    <style>
    .centered-text {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    .stButton>button {
        background-color: transparent;
        color: white; 
        border: 1px solid #F0B900; 
    }
    .stButton>button:hover {
        color: #F0B900; 
        border-color: 1px solid #F0B900; 
    }
    .stButton>button:active {
        background-color: #F0B900; 
        color: white;
    }
    .filter-title {
        font-size: 24px;
        border: 1px solid #F0B900;
        border-radius: 10px;
        padding: 5px;
        text-align: center;
    }
    div[data-baseweb="select"] > div {
        border: 1px solid #F0B900 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------- UI ELEMENTS -----------------------

# UI: Title
st.markdown(
    """
    <div class="centered-text">
        <h1>∞ Recommandation ∞</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar: Filter Title
st.sidebar.markdown(
    """
    <style>
    .filter-title {
        font-size: 24px;
        border: 2px solid #F0B900;
        border-radius: 10px;
        padding: 5px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    <div class="filter-title">
        FILTRE
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar: Genre Filter
genres = df['genres'].str.get_dummies(sep=',').columns.tolist()
genres_filter = st.sidebar.multiselect("Genre :", options=genres)

# Obtenez la liste des noms de studios
studio_names = df['production_companies_name_y'].unique().tolist()

# Supprimez les guillemets de chaque nom de studio
studio_names_no_quotes = [name.replace('"', '') for name in studio_names]

# Triez les studios par compte
studio_counts = df['production_companies_name_y'].value_counts()

# Obtenez les 10 studios les plus populaires
top_studios = studio_counts.nlargest(10).index.tolist()
top_studios_no_quotes = [name.replace('"', '') for name in top_studios]

# Obtenez les autres studios
other_studios = studio_counts.index[~studio_counts.index.isin(top_studios)].tolist()
other_studios_no_quotes = [name.replace('"', '') for name in other_studios]

# Triez les autres studios
other_studios_no_quotes.sort()

# Créez la liste des options de studio pour le filtre
studio_options = ['★ POPULAIRE ★'] + top_studios_no_quotes + ['-' * 54] + other_studios_no_quotes

# Affichez le filtre
selected_studios = st.sidebar.multiselect("Studio", options=studio_options)

# Vérifier si "★ POPULAIRE ★" est sélectionné, et ajouter les top studios si c'est le cas
if '★ POPULAIRE ★' in selected_studios:
    selected_studios = list(set(selected_studios + top_studios))

# Sidebar: Rating Filter
rating_range = st.sidebar.slider("Notes :", min_value=0.0, max_value=9.5, step=0.5, value=(0.0, 9.5), key="rating_slider")


# CSS styles
st.markdown(
    """
    <style>
    .centered-text {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    .stButton>button {
        background-color: transparent;
        color: white; 
        border: 1px solid #F0B900; 
    }
    .stButton>button:hover {
        color: #F0B900; 
        border-color: 1px solid #F0B900; 
    }
    .stButton>button:active {
        background-color: #F0B900; 
        color: white; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

# UI: Widgets
sorted_movies = df.sort_values(by="startYear", ascending=False)["title"].tolist()

# Create columns to align the Start button, search, and Clear button on the same row.
cols = st.columns([1, 9, 0.5])

# Initialisez clear_click_count au début du script
if 'clear_click_count' not in st.session_state:
    st.session_state.clear_click_count = 0
    
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = ''


# Place the "Start" button in the first column.
with cols[0]:
    st.markdown("""
        <style>
            .start-button {
                padding: 24.5px;
            }
        </style>
        <div class="start-button">
    """, unsafe_allow_html=True)
    if st.button("👉Start", key='start_button'):
        st.session_state.recommendation_started = True
    st.markdown("</div>", unsafe_allow_html=True)

# Modification: Only show movies from 2020 and later
sorted_movies = df.sort_values(by="startYear", ascending=False)["title"].tolist()

# Place the movie selection in the second column.
with cols[1]:
    st.markdown("""
        <style>
            .search-bar {
                padding: 10px;
            }
        </style>
        <div class="search-bar">
    """, unsafe_allow_html=True)
    
    # Initialize selected_movie to an empty list outside of the if block
    selected_movie = []
    
    suggestions = sorted_movies  
    
    # Update selected_movie inside the if block
    selected_movie = st.selectbox(
        "Commencez par choisir votre film préféré: (Example: Avatar)", 
        [''] + suggestions, 
        index=0,
        key=f'search_bar_{st.session_state.clear_click_count}'
    )
    
    # Add the following code to reset relevant states when a new movie is selected
    if st.session_state.get('genres_filter') != genres_filter or \
       st.session_state.get('selected_studios') != selected_studios or \
       st.session_state.get('rating_range') != rating_range:
        st.session_state.recommendation_started = False  # Reset the recommendation
        st.session_state.start_index = 0  # Reset the start index for displayed movies
        st.session_state.displayed_movies = []  # Clear the displayed movies
        st.session_state.current_page = 1  # Reset the current page
        # Update st.session_state with the new filter values
        st.session_state['genres_filter'] = genres_filter
        st.session_state['selected_studios'] = selected_studios
        st.session_state['rating_range'] = rating_range

        
        
    st.markdown("</div>", unsafe_allow_html=True)

# Place the "Clear" button in the third column with a thicker border.
with cols[2]:
    st.markdown("""
        <style>
            .clear-button {
                padding: 24.5px;
            }
        </style>
        <div class="clear-button">
    """, unsafe_allow_html=True)

    if st.button("X", key='clear_button'):
        # Réinitialisation des variables d'état
        st.session_state.selected_movie = ''
        st.session_state.recommendation_started = False
        st.session_state.start_index = 0
        st.session_state.displayed_movies = []
        st.session_state.search_bar_input = ''
        st.session_state.current_page = 1
        st.session_state.last_displayed_index = 0
        
        # Redémarrage de l'exécution du script
        st.session_state.clear_click_count += 1
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# Initialize or reset states
if 'last_displayed_index' not in st.session_state:
    st.session_state.last_displayed_index = 0
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = ''
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'recommendation_started' not in st.session_state:
    st.session_state.recommendation_started = False
if 'start_index' not in st.session_state:
    st.session_state.start_index = 0
if 'search_bar_input' not in st.session_state:
    st.session_state.search_bar_input = ''
if 'displayed_movies' not in st.session_state:
    st.session_state.displayed_movies = []

    
# UI: Displaying Movies
if st.session_state.recommendation_started and selected_movie and len(selected_movie) >= 1:
    all_similar_movies = update_filtered_movies(selected_movie, genres_filter, selected_studios, rating_range)

    # Determine the number of films per page
    movies_per_page = 16
    
    # Update the start and end indices based on the length of displayed_movies
    start_index = len(st.session_state.displayed_movies)
    end_index = start_index + movies_per_page

    # Add the next set of movies to displayed_movies
    st.session_state.displayed_movies.extend(all_similar_movies[start_index:end_index])

    cols = st.columns(4)
    for i, movie_title in enumerate(st.session_state.displayed_movies):  # Change here to use displayed_movies
        movie_data = df[df["title"] == movie_title].iloc[0]
        with cols[i % 4]:
            st.markdown(
                f"""
                <div style='margin: 0 0 20px 0; border: 1px solid #9E9E9E; border-radius: 16px; overflow: hidden;'>
                    <div style='height: 300px; overflow: hidden;'>
                        <img src='{poster_url(movie_title, df)}' style='width: 100%; height: 100%; object-fit: cover;'>
                    </div>
                    <div style='background-color: black; padding: 10px; min-height: 185px;'>
                        <div style='text-align: left; color: white;'>
                            <span style='color: gold; font-size: 22px;'>★</span> <span style='font-size: 16px;'>{movie_data['averageRating']}</span>
                        </div>
                        <div style='text-align: left; color: white; font-weight: bold;'>
                            {movie_title}
                        </div>
                        <div style='text-align: left; color: white;'>
                            ({int(movie_data['startYear'])})
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    if len(st.session_state.displayed_movies) < len(all_similar_movies):  # Change the condition here
        if st.button("Afficher plus"):
            st.experimental_rerun()



