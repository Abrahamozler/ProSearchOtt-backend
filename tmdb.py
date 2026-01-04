import os, requests

TMDB_KEY = os.getenv("TMDB_API_KEY")

def tmdb_data(title):
    if not TMDB_KEY:
        return {}
    url = "https://api.themoviedb.org/3/search/movie"
    r = requests.get(url, params={
        "api_key": TMDB_KEY,
        "query": title
    }, timeout=5).json()

    if not r.get("results"):
        return {}

    m = r["results"][0]
    return {
        "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get("poster_path") else None,
        "year": m.get("release_date","")[:4],
        "rating": m.get("vote_average")
    }
