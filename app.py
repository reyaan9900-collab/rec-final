import streamlit as st
import pickle
import pandas as pd
import os
import gdown

# --- Page Setup ---
st.set_page_config(
    page_title="Netflix Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for cards, fonts, hover effects ---
st.markdown("""
<style>
.movie-card {
    background-color: rgba(28,28,28,0.85);
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 15px;
    box-shadow: 2px 2px 15px rgba(0,0,0,0.5);
    transition: transform 0.3s, box-shadow 0.3s;
}
.movie-card:hover {
    transform: scale(1.08);
    box-shadow: 5px 5px 25px rgba(0,0,0,0.7);
}
.movie-title {
    color: #e50914;
    font-weight: bold;
    margin-top: 5px;
    font-size: 16px;
}
.header {
    text-align: center;
    color: #e50914;
    font-size: 40px;
    font-weight: bold;
    text-shadow: 2px 2px 5px black;
    margin-bottom: 20px;
}
[data-testid="stSidebar"] {
    background-color: rgba(28,28,28,0.9);
}
input[type="text"] {
    padding: 5px;
    border-radius: 5px;
    border: 1px solid #e50914;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header">🎬 Netflix Movie Recommendation System</div>', unsafe_allow_html=True)

# --- Download similarity.pkl once and cache it locally ---
def download_similarity(file_id, filename="similarity.pkl"):
    # Use Streamlit's persistent app folder
    cache_dir = st.secrets.get("APP_CACHE_DIR", "/home/appuser/")
    path = os.path.join(cache_dir, filename)
    
    if not os.path.exists(path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, path, quiet=False)
        st.success(f"Downloaded {filename} to cache folder")
    return path

similarity_file_id = "1kj6WEIvPjBrXbwyp9P-j8fZ3Q3KuIWqv"
similarity_path = download_similarity(similarity_file_id)

# --- Load Data ---
@st.cache_data
def load_data():
    movies = pickle.load(open('movie_list.pkl', 'rb'))  # must be in repo
    similarity = pickle.load(open(similarity_path, 'rb'))  # from cached download
    return movies, similarity

movies, similarity = load_data()

# --- Recommendation Function ---
def get_recommendations(title, movies, similarity):
    title = title.strip()
    if title not in movies['Title'].values:
        return ["Movie not found"]
    
    idx = movies[movies['Title'] == title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in sim_scores[1:11]]
    
    return movies['Title'].iloc[top_indices].tolist()

# --- Sidebar: Live Search ---
st.sidebar.header("Search Your Movie")
search_input = st.sidebar.text_input("Type to search:", "")
movie_list = movies['Title'].sort_values().tolist()
filtered_list = [m for m in movie_list if search_input.lower() in m.lower()] if search_input else movie_list
selected_movie = st.sidebar.selectbox("Select a movie:", filtered_list)

# --- Recommendations ---
if st.sidebar.button("Recommend 🎥"):
    with st.spinner("Finding similar movies..."):
        recommendations = get_recommendations(selected_movie, movies, similarity)
        if recommendations[0] == "Movie not found":
            st.error("Movie not found in database.")
        else:
            st.subheader(f"Top 10 movies to watch after **{selected_movie}**:")
            cols = st.columns(5)
            for i, movie in enumerate(recommendations):
                with cols[i % 5]:
                    st.markdown(f"""
                        <div class='movie-card'>
                            <div class='movie-title'>{movie}</div>
                        </div>
                    """, unsafe_allow_html=True)
