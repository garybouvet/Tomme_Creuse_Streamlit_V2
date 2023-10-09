import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data(show_spinner=False)
def calculate_similarity(df):
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df['combined_features'])
    cosine_sim = cosine_similarity(count_matrix)
    return cosine_sim

st.set_page_config(
    page_title="Titre de votre application",
    layout="wide"
)

# Début de la mise en forme
st.markdown(
    """
    <style>
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

st.markdown(
    """
    <div class="centered-text">
        <h1>FILMS</h1>
    </div>
    """,
    unsafe_allow_html=True
)

df = pd.read_csv("./Data_base/merged_data.csv")

df['production_companies_name_y'] = df['production_companies_name_y'].str.split(',')
df = df.explode('production_companies_name_y')
df['production_companies_name_y'] = df['production_companies_name_y'].str.strip()
df['production_companies_name_y'] = df['production_companies_name_y'].str.replace('"', '')
df['production_companies_name_y'] = df['production_companies_name_y'].str.replace("'", '')
df.drop_duplicates(subset="tconst", keep="first", inplace=True)

if 'clicked_movie_tconst' not in st.session_state:
    st.session_state['clicked_movie_tconst'] = ""

def show_movie_details(tconst):
    movie = df[df['tconst'] == tconst].iloc[0]
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(f"https://image.tmdb.org/t/p/w900{movie['poster_path_y']}", use_column_width=True)
    with col2:
        st.write(f"**Titre :** {movie['title']}")
        st.write(f"**Année :** {int(movie['startYear'])}")
        st.write(f"**Durée :** {movie['runtimeMinutes']} minutes")
        st.write(f"**Genres :** {movie['genres']}")
        st.write(f"**Note :** {movie['averageRating']}")

def title_from_index(index):
    return df[df.index == index]["title"].values[0]

def index_from_title(title):
    return df[df.title == title]["index"].values[0]

def find_similar_movies(movie_title, num_movies=5):
    movie_index = index_from_title(movie_title)
    similar_movies = list(enumerate(cosine_sim[movie_index]))
    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:num_movies + 1]
    return [title_from_index(element[0]) for element in sorted_similar_movies]

def poster_url(title, df):
    try:
        poster_path = df[df['title'] == title]['poster_path_y'].values[0]
        return 'https://image.tmdb.org/t/p/w500' + poster_path
    except Exception as e:
        st.error(f"Error for {title}: {str(e)}")
        return None


cosine_sim = calculate_similarity(df)

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
        margin-bottom: 20px;  # Ajout de la marge en dessous
    }
    </style>
    <div class="filter-title">
        FILTRE
    </div>
    """,
    unsafe_allow_html=True
)

genres = df['genres'].str.get_dummies(sep=',').columns.tolist()
genres_filter = st.sidebar.multiselect("Genre :", options=genres)

df_filtered = df.copy()
if genres_filter:
    genre_mask = df_filtered['genres'].str.contains('|'.join(genres_filter))
    df_filtered = df_filtered[genre_mask]

studio_counts = df['production_companies_name_y'].value_counts()
top_studios = studio_counts.nlargest(10).index.tolist()
other_studios = studio_counts.index[~studio_counts.index.isin(top_studios)].sort_values().tolist()
studio_options = ['★ POPULAIRE ★'] + top_studios + ['-' * 54] + other_studios
selected_studios = st.sidebar.multiselect("Studio :", options=studio_options)

rating_range = st.sidebar.slider("Notes :", min_value=0.0, max_value=9.5, step=0.5, value=(0.0, 9.5), key="rating_slider")

min_rating = rating_range[0]
max_rating = rating_range[1]

df_filtered = df[(df['averageRating'] >= min_rating) & (df['averageRating'] <= max_rating)]

search_query = st.text_input("", placeholder="Rechercher :", key="search_input")



if search_query:
    starts_with_mask = df_filtered['title'].str.lower().str.startswith(search_query.lower())
    df_filtered = df_filtered[starts_with_mask]
    df_filtered['starts_with'] = df_filtered['title'].str.lower().str.startswith(search_query.lower())
    df_filtered['exact_match'] = df_filtered['title'].str.lower() == search_query.lower()
    df_filtered = df_filtered.sort_values(by=['exact_match', 'starts_with', 'title'], ascending=[False, False, True])

# Ajoutez cette section pour gérer les différents cas d'affichage
if len(df_filtered) == 0:
    st.markdown("### Film inconnu ou invalide ...")
elif not genres_filter and not selected_studios and not (min_rating > 0.0 or max_rating < 9.5) and not search_query:
    st.markdown("### Derniers films populaires :")
else:
    st.markdown("### Selon votre sélection :")



st.markdown(
    """
    <style>
    .stTextInput input {
        border: 1px solid #F0B900 !important;
        border-radius: 10px !important;
        padding: 5px !important;
        outline: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



if search_query:
    starts_with_mask = df_filtered['title'].str.lower().str.startswith(search_query.lower())
    df_filtered = df_filtered[starts_with_mask]
    df_filtered['starts_with'] = df_filtered['title'].str.lower().str.startswith(search_query.lower())
    df_filtered['exact_match'] = df_filtered['title'].str.lower() == search_query.lower()
    df_filtered = df_filtered.sort_values(by=['exact_match', 'starts_with', 'title'], ascending=[False, False, True])

if genres_filter:
    genre_mask = df_filtered['genres'].str.contains('|'.join(genres_filter))
    df_filtered = df_filtered[genre_mask]

if rating_range:
    df_filtered = df_filtered[(df_filtered['averageRating'] >= min_rating) & (df_filtered['averageRating'] <= max_rating)]

if selected_studios:
    studio_mask = df_filtered['production_companies_name_y'].isin(selected_studios)
    df_filtered = df_filtered[studio_mask]

df_filtered = df_filtered.sort_values(by='startYear', ascending=False)

num_movies_per_page = 52

cols = st.sidebar.columns([4, 2, 3])

if 'page_state' not in st.session_state:
    st.session_state['page_state'] = "gallery"
    st.session_state['movies_shown'] = 52  # 52 films affichés initialement

if st.session_state['page_state'] == "gallery":

    cols = st.columns(4)
    for i, movie_row in enumerate(df_filtered.iloc[:st.session_state['movies_shown']].itertuples()):
        movie_data = movie_row  # Utilisez directement la ligne du DataFrame pour accéder aux données
        movie_title = movie_row.title  # Accédez au titre du film
        poster_url = f"https://image.tmdb.org/t/p/w500{movie_row.poster_path_y}"
        with cols[i % 4]:
            st.markdown(
                f"""
                <div style='margin: 0 0 20px 0; border: 1px solid white; border-radius: 16px; overflow: hidden;'>
                    <!-- Display image -->
                    <img src='{poster_url}' style='width: 100%;'>
                    <!-- Display rating, title, and year under the image -->
                    <div style='background-color: black; padding: 10px; min-height: 165px;'>
                        <div style='text-align: left; color: white;'>
                            <span style='color: gold; font-size: 22px;'>★</span> <span style='font-size: 16px;'>{movie_data.averageRating}</span>
                        </div>
                        <div style='text-align: left; color: white; font-weight: bold;'>
                            {movie_title}
                        </div>
                        <div style='text-align: left; color: white;'>
                            ({int(movie_data.startYear)})
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        if (i + 1) % 4 == 0:
            cols = st.columns(4)
    
    if len(df_filtered) > st.session_state['movies_shown']:
        if st.button("Afficher plus", key='unique_key_afficher_plus'):
            st.session_state['movies_shown'] += 52  # Ajoute 52 films supplémentaires
            st.experimental_rerun()


