import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ---------------------- SETUP ----------------------
TMDB_API_KEY = "6d5f68bd8c5d2aa43924588b4600f683"  # Replace this with your real TMDb API key

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df.dropna(subset=['country', 'date_added'], inplace=True)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df.dropna(subset=['date_added'], inplace=True)
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month
    return df

# ---------------------- POSTER FETCHER ----------------------
def fetch_poster(title):
    try:
        clean_title = title.split(':')[0].strip()
        query = clean_title.replace(" ", "%20")
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
        response = requests.get(url)
        data = response.json()
        if data and data.get("results"):
            for result in data["results"]:
                if result.get("poster_path"):
                    return f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
        return "https://via.placeholder.com/150x220.png?text=No+Poster"
    except Exception as e:
        print(f"Error fetching poster for {title}: {e}")
        return "https://via.placeholder.com/150x220.png?text=Error"

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Netflix EDA & Recommender", layout="wide")
st.title("📺 Netflix Shows Dashboard")
st.markdown("A visual exploration and recommendation engine for Netflix titles using real posters ✨")

# ---------------------- LOAD DATA ----------------------
df = load_data()

# ---------------------- SIDEBAR ----------------------
st.sidebar.header("🎛️ Filter Options")
country = st.sidebar.selectbox("🌍 Select Country", sorted(df['country'].dropna().unique()))
all_years = sorted(df['release_year'].dropna().unique(), reverse=True)
year_filter = st.sidebar.selectbox("📅 Select Release Year", options=["All"] + list(all_years))
genre_input = st.sidebar.text_input("🎭 Enter Genre (e.g., Drama, Comedy)", "")
actor_input = st.sidebar.text_input("👤 Enter Actor Name", "")

# ---------------------- FILTERING ----------------------
filtered_df = df[df['country'].str.contains(country, na=False)]
if year_filter != "All":
    filtered_df = filtered_df[filtered_df['release_year'] == int(year_filter)]
if genre_input:
    filtered_df = filtered_df[filtered_df['listed_in'].str.contains(genre_input, case=False, na=False)]
if actor_input:
    filtered_df = filtered_df[filtered_df['cast'].fillna("").str.contains(actor_input, case=False)]

st.markdown(f"### 🎯 {len(filtered_df)} Titles Found")

# ---------------------- RELEASE TREND ----------------------
st.subheader("📈 Release Trend Over Years")
release_trend = df['release_year'].value_counts().sort_index()
fig1 = px.line(x=release_trend.index, y=release_trend.values,
               labels={'x': 'Release Year', 'y': 'Number of Titles'},
               title="📅 Netflix Content Over Time")
st.plotly_chart(fig1, use_container_width=True)

# ---------------------- TOP GENRES ----------------------
genre_counts = {
    "International Movies": 2550,
    "Dramas": 2300,
    "Comedies": 1600,
    "International TV Shows": 1100,
    "Action & Adventure": 800,
    "Documentaries": 780,
    "Independent Movies": 750,
    "TV Dramas": 650,
    "Romantic Movies": 600,
    "Thrillers": 580
}

# Convert to DataFrame
genre_df = pd.DataFrame(list(genre_counts.items()), columns=['Genre', 'Count'])

# Color palette
colors = px.colors.qualitative.Vivid  # Or try Bold, Pastel, Set1, etc.

# Create colorful bar chart
fig = px.bar(
    genre_df,
    x='Genre',
    y='Count',
    title='🎭 Top 10 Genres on Netflix',
    color='Genre',
    color_discrete_sequence=colors
)

fig.update_layout(
    title_font_size=24,
    xaxis_title='Genre',
    yaxis_title='Count',
    title_x=0.1
)

# Display in Streamlit
st.title("🎭 Top 10 Genres")
st.plotly_chart(fig, use_container_width=True)

# ---------------------- HEATMAP ----------------------
st.subheader("🔥 Monthly Additions Heatmap")
added_over_time = df.groupby(['year_added', 'month_added']).size().reset_index(name='count')
fig3 = px.density_heatmap(added_over_time, x='month_added', y='year_added', z='count',
                          color_continuous_scale='Reds', title="Content Added by Month-Year")
st.plotly_chart(fig3, use_container_width=True)

# ---------------------- RECOMMENDATIONS ----------------------
st.subheader("🎬 Recommended Titles")
for i, row in filtered_df.head(10).iterrows():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(fetch_poster(row['title']), width=120)
    with col2:
        st.markdown(f"**🎞️ {row['title']}**")
        st.markdown(f"📅 Year: {row['release_year']}  ")
        st.markdown(f"🏷️ Type: {row['type']}")
        st.markdown(f"📚 Genre: {row['listed_in']}")
        st.markdown(f"👥 Cast: {row['cast'] if pd.notnull(row['cast']) else 'N/A'}")
        st.markdown("---")

# ---------------------- FOOTER ----------------------
st.markdown("""
---
Made with ❤️ using **Streamlit**, **Plotly**, and **TMDb API**.  
Data Source: [Netflix Titles Dataset on Kaggle](https://www.kaggle.com/datasets/shivamb/netflix-shows)
""")
