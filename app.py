import streamlit as st
import pandas as pd
import pickle
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter, Retry

# -----------------------------------
# Streamlit Page Setup
# -----------------------------------
st.set_page_config(
    page_title="CineSense – Smart Movie Recommendations",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------
# CSS Theme
# -----------------------------------
st.markdown("""
<style>
body { background: linear-gradient(135deg,#0f0f18 0%,#1a1a2e 100%); color:white; }
.cine-title { font-size:40px; font-weight:900; text-align:center; margin-top:-10px; }
.cine-subtitle { text-align:center; margin-top:-8px; font-size:16px; color:#b5b5c8; }
.movie-card { border-radius:14px; overflow:hidden; box-shadow:0 8px 24px rgba(0,0,0,0.25); transition:0.22s; position:relative; background:rgba(255,255,255,0.04); }
.movie-card:hover { transform:translateY(-6px) scale(1.03); box-shadow:0 16px 40px rgba(0,0,0,0.35); }
.movie-poster { width:100%; height:auto; }
.overlay { position:absolute; bottom:0; width:100%; padding:10px; background:linear-gradient(180deg,transparent 0%,rgba(0,0,0,0.75) 60%); color:white; }
.title { font-size:15px; font-weight:700; margin:0; }
.year { font-size:13px; opacity:0.85; }
.rating-badge { position:absolute; left:10px; top:10px; background:rgba(0,0,0,0.75); padding:5px 10px; border-radius:999px; font-size:13px; font-weight:700; }
.card-link { text-decoration:none; color:inherit; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# Title
# -----------------------------------
st.markdown("<h1 class='cine-title'>CineSense</h1>", unsafe_allow_html=True)
st.markdown("<p class='cine-subtitle'>AI-powered movie intelligence • Discover films you'll actually enjoy</p>", unsafe_allow_html=True)

# -----------------------------------
# TMDB Setup
# -----------------------------------
API_KEY = "b5f432a8a004ec54bff5b9bac32079ea"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Image"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cine")

# Session with retries
SESSION = requests.Session()
retries = Retry(total=3, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
SESSION.mount("https://", HTTPAdapter(max_retries=retries))


# Clean integer ID
def safe_int(val):
    try:
        if pd.isna(val): return None
        v = int(float(val))
        return v if v > 0 else None
    except:
        return None


# -----------------------------------
# Fetch Movie Metadata
# -----------------------------------
@st.cache_data(show_spinner=False)
def fetch_movie_data(movie_id):
    mid = safe_int(movie_id)
    if not mid:
        return {
            "poster_url": PLACEHOLDER, "tmdb_url": "",
            "title": "", "year": "", "rating": None
        }

    url = f"https://api.themoviedb.org/3/movie/{mid}?api_key={API_KEY}&language=en-US"

    try:
        r = SESSION.get(url, timeout=6)

        if r.status_code != 200:
            logger.warning(f"Movie ID {mid} -> HTTP {r.status_code}")
            return {
                "poster_url": PLACEHOLDER,
                "tmdb_url": f"https://www.themoviedb.org/movie/{mid}",
                "title": "", "year": "", "rating": None
            }

        data = r.json()

        poster = data.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else PLACEHOLDER

        return {
            "poster_url": poster_url,
            "tmdb_url": f"https://www.themoviedb.org/movie/{mid}",
            "title": data.get("title", ""),
            "year": (data.get("release_date") or "").split("-")[0] if data.get("release_date") else "",
            "rating": data.get("vote_average")
        }

    except Exception as e:
        logger.error(f"Error fetching {mid}: {e}")
        return {
            "poster_url": PLACEHOLDER,
            "tmdb_url": f"https://www.themoviedb.org/movie/{mid}",
            "title": "", "year": "", "rating": None
        }


# -----------------------------------
# Recommendation logic
# -----------------------------------
def recommend(movie):
    idx = movies[movies["title"] == movie].index[0]
    distances = similarity[idx]

    sorted_scores = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    ids = [safe_int(movies.iloc[i[0]].movie_id) for i in sorted_scores]

    # Concurrent metadata fetching
    with ThreadPoolExecutor(max_workers=5) as ex:
        meta_list = list(ex.map(fetch_movie_data, ids))

    names = [m["title"] for m in meta_list]
    return names, meta_list, ids


# -----------------------------------
# Load Data
# -----------------------------------
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))


# -----------------------------------
# UI Controls
# -----------------------------------
selected = st.selectbox("Choose a movie you like:", movies["title"].values)

if st.button("Recommend Movies"):
    names, metas, ids = recommend(selected)
    cols = st.columns(5)

    for i, col in enumerate(cols):
        m = metas[i]
        card = f"""
        <a class='card-link' href='{m["tmdb_url"]}' target='_blank'>
            <div class='movie-card'>
                <img class='movie-poster' src='{m["poster_url"]}'>
                <div class='rating-badge'>{round(m["rating"],1) if m["rating"] else "—"}</div>
                <div class='overlay'>
                    <p class='title'>{m["title"]}</p>
                    <p class='year'>{m["year"]}</p>
                </div>
            </div>
        </a>
        """
        with col:
            st.markdown(card, unsafe_allow_html=True)

