import streamlit as st
import pandas as pd
import json
from spotify_utils import get_access_token, search_track_id
from reccobeats_utils import get_full_music_data_from_reccobeats

st.set_page_config(page_title="ReccoBeats Music Analyzer 🎧", layout="wide")
st.title("🎵 Music Metadata Pipeline: Spotify ID ➡️ ReccoBeats")

st.header("Step 1: Find Spotify ID by artist + title + album")

json_1 = st.file_uploader("Send JSON with the fields 'artist', 'title' and 'album'.", type="json", key="step1")

if json_1:
    raw = json.load(json_1)
    df = pd.DataFrame(raw)

    if "artist" not in df.columns or "title" not in df.columns:
        st.error("The JSON must contain 'artist', 'title' and album.")
        st.stop()

    if st.button("🔍 Start Step 1: Get Spotify IDs"):
        token = get_access_token()
        st.info("Looking for Spotify IDs...")
        df["spotify_id"] = df.apply(lambda row: search_track_id(row["title"], row["artist"], row["album"], token), axis=1)

        st.success(f"✅ IDs found: {df['spotify_id'].notnull().sum()} for {len(df)} songs")
        st.dataframe(df)

        json_out = df.to_dict(orient="records")
        json_str = json.dumps(json_out, indent=2)
        st.download_button("Download JSON with Spotify IDs", json_str, file_name="spotify_ids.json", mime="application/json")

st.divider()

st.header("Step 2: Fetch ReccoBeats data (Track + Audio Features)")

json_2 = st.file_uploader("Send JSON with field 'spotify_id'", type="json", key="step2")

if json_2:
    raw = json.load(json_2)
    df_original = pd.DataFrame(raw)

    if "spotify_id" not in df_original.columns:
        st.error("The JSON must contain spotify_id.")
        st.stop()

    if st.button("🔄 Start Step 2: Fetch ReccoBeats Data"):
        ids = df_original["spotify_id"].dropna().unique().tolist()
        st.info("⏳ Fetching full track data from ReccoBeats...")
        full_result = get_full_music_data_from_reccobeats(ids)

        if not full_result:
            st.warning("⚠️ No track data returned.")
        else:
            # df_new = pd.DataFrame(full_result)
            df_new = pd.json_normalize(full_result)

            # 🔁 Mesclar os dados originais com os da API, com base no spotify_id
            df_merged = df_original.merge(df_new, on="spotify_id", how="left")

            st.success("✅ All data retrieved and merged successfully.")
            st.dataframe(df_merged)

            json_str = json.dumps(df_merged.to_dict(orient="records"), indent=2)
            st.download_button("⬇️ Download merged JSON", json_str,
                               file_name="reccobeats_merged_output.json", mime="application/json")

            # Novo botão: exportar CSV
            csv_bytes = df_merged.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download merged CSV",
                data=csv_bytes,
                file_name="reccobeats_merged_output.csv",
                mime="text/csv"
            )

