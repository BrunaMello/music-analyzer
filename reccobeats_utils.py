import requests
import time
import streamlit as st

def get_full_music_data_from_reccobeats(spotify_ids, delay=0.2):
    """
    Para cada spotify_id:
    - Busca metadados da música via ReccoBeats
    - Usa o ID interno para buscar audio features
    - Retorna lista com todas informações combinadas
    """
    full_data = []
    status = st.empty()
    status2 = st.empty()

    for i, spotify_id in enumerate(spotify_ids):
        base_url = f"https://api.reccobeats.com/v1/track?ids={spotify_id}"
        status.write(f"[{i+1}/{len(spotify_ids)}] 🎯 Fetching track for Spotify ID: {spotify_id}")

        try:
            # Buscar metadados da música
            r = requests.get(base_url)
            if r.status_code != 200:
                status2.warning(f"[{i+1}] ❌ Failed to get track: {r.status_code}")
                continue

            track_data = r.json().get("content", [])
            if not track_data:
                status2.warning(f"[{i+1}] ⚠️ No data for {spotify_id}")
                continue

            track = track_data[0]
            track_id = track.get("id")

            # Buscar audio features se houver ID interno
            audio_features = {}
            if track_id:
                audio_url = f"https://api.reccobeats.com/v1/track/{track_id}/audio-features"
                r_audio = requests.get(audio_url)
                if r_audio.status_code == 200:
                    audio_features = r_audio.json()
                    status2.info(f"[{i+1}] ✅ Audio features for ID {track_id}")
                else:
                    status2.warning(f"[{i+1}] ⚠️ No features for ID {track_id}")
            else:
                status2.warning(f"[{i+1}] ⚠️ Missing internal ID for Spotify ID {spotify_id}")

            # Combinar os dados em um único dicionário
            combined = {**track, **{"spotify_id": spotify_id}, **audio_features}
            full_data.append(combined)

        except Exception as e:
            status.error(f"[{i+1}] ❗ Error with ID {spotify_id}: {e}")

        time.sleep(delay)

    return full_data
