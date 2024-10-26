from collections import Counter

from django.contrib.auth.decorators import login_required
import requests
from django.shortcuts import render
from django.shortcuts import redirect

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1/me"

@login_required
def user_spotify_login(request):
    return render(request, 'loginWithSpotify.html', {})

@login_required
def wrapped(request):
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    time_range = request.GET.get('time_range', 'medium_term')

    user_data = get_spotify_user_info(access_token)
    top_artists_data = get_spotify_top_artists(access_token, 5, time_range)
    top_tracks_data, average_valence = get_spotify_top_tracks_and_valence(access_token, time_range)
    top_genres_data = get_spotify_top_genres(access_token , time_range)

    return render(request, 'wrapped.html', {
        'user_data': user_data,
        'top_artists': top_artists_data,
        'top_tracks': top_tracks_data,
        'top_genres': top_genres_data, # Pass top artists to the template
        'average_valence': average_valence,
        'selected_time_range': time_range
    })

def get_spotify_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{SPOTIFY_API_URL}", headers=headers)
    return response.json()

def get_spotify_top_artists(access_token, limit, time_range):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": limit,
        "time_range": time_range
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    return response.json()


def get_spotify_top_tracks_and_valence(access_token, time_range):
    # Fetch the top tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": 50,
        "time_range": time_range
    }

    response = requests.get(top_tracks_url, headers=headers, params=params)
    if response.status_code != 200:
        return None, 0  # Return None and 0 if failed to fetch tracks

    top_tracks_data = response.json()

    # Get track IDs for fetching audio features
    track_ids = [track['id'] for track in top_tracks_data.get('items', []) if track.get('id')]

    # Fetch audio features for the top tracks
    audio_features_url = "https://api.spotify.com/v1/audio-features"
    params = {
        "ids": ','.join(track_ids)
    }

    audio_response = requests.get(audio_features_url, headers=headers, params=params)
    if audio_response.status_code != 200:
        return top_tracks_data, 0  # Return top tracks and 0 if failed to fetch audio features

    audio_features_data = audio_response.json()

    # Calculate average valence
    if audio_features_data and 'audio_features' in audio_features_data:
        valences = [feature['valence'] for feature in audio_features_data['audio_features'] if
                    feature['valence'] is not None]
        average_valence = sum(valences) / len(valences) if valences else 0
    else:
        average_valence = 0

    return top_tracks_data, average_valence


def get_spotify_top_genres(access_token, time_range):
    artists = get_spotify_top_artists(access_token, 50, time_range).get("items", [])

    if artists is None:
        print("Failed to fetch top tracks. The returned value is None.")
        return []

    if not artists:
        print("No top tracks found.")
        return []

    all_genres = []

    for artist in artists:
        genres = artist.get('genres', [])
        all_genres.extend([genre.title() for genre in genres])

    genre_counts = Counter(all_genres)

    sorted_genres = genre_counts.most_common()[0:5]
    genre_list = []
    for genre, count in sorted_genres:
        genre_list.append(genre)
    return genre_list

@login_required
def account(request):
    return render(request, 'accountInfo.html')

@login_required
def select(request):
    return render(request, 'wrappedSelect.html', {})
@login_required
def invite(request):
    return render(request, 'wrappedInvite.html', {})

@login_required
def duo(request):
    return render(request, 'wrappedDuo.html', {})