import os
import base64
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


def get_access_token():
    client_id = st.secrets["SPOTIFY_CLIENT_ID"]
    client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]

    if not client_id or not client_secret:
        raise Exception("there is no CLIENT_ID ou CLIENT_SECRET on secrets.toml")

    auth = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}"
    }
    data = {
        "grant_type": "client_credentials"
    }

    r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    r.raise_for_status()

    return r.json().get("access_token")


def search_track_id(track_name, artist_name, album, token):
    query = f"track:{track_name} artist:{artist_name} album:{album}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)

    try:
        results = r.json()
        items = results.get("tracks", {}).get("items", [])
        if items:
            return items[0]["id"]
        return None
    except Exception as e:
        st.write("Error retrieving ID:", r.status_code, r.text)
        return None