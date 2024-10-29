from collections import Counter
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
import requests

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
    top_artists_data, top_genres_data, top_tracks_data, average_valence, artist_songs = get_spotify_top_data(access_token, time_range)

    return render(request, 'wrapped.html', {
        'user_data': user_data,
        'top_artists': top_artists_data,
        'artist_songs': artist_songs,
        'top_tracks': top_tracks_data,
        'top_genres': top_genres_data,
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

def get_spotify_top_data(access_token, time_range):
    # Top Artists
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": 50,
        "time_range": time_range
    }

    top_artists = requests.get(url, headers=headers, params=params)
    if top_artists.status_code != 200:
        return None, [], None, 0, {}
    top_artists = top_artists.json()

    # Top Genres
    artists = top_artists.get("items", [])

    if artists is None or not artists:
        return top_artists, [], None, 0, {}

    all_genres = []

    for artist in artists:
        genres = artist.get('genres', [])
        all_genres.extend([genre.title() for genre in genres])

    genre_counts = Counter(all_genres)

    sorted_genres = genre_counts.most_common()[0:5]
    genre_list = []
    for genre, count in sorted_genres:
        genre_list.append(genre)

    # Top Tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": 50,
        "time_range": time_range
    }

    top_tracks_data = requests.get(top_tracks_url, headers=headers, params=params)
    if top_tracks_data.status_code != 200:
        return top_artists, genre_list, None, 0, {}
    top_tracks_data = top_tracks_data.json()

    # Average Valence
    # Get track IDs for fetching audio features
    track_ids = [track['id'] for track in top_tracks_data.get('items', []) if track.get('id')]

    # Fetch audio features for the top tracks
    audio_features_url = "https://api.spotify.com/v1/audio-features"
    params = {
        "ids": ','.join(track_ids)
    }

    audio_response = requests.get(audio_features_url, headers=headers, params=params)
    if audio_response.status_code != 200:
        return top_artists, genre_list, top_tracks_data, -1, {}

    audio_features_data = audio_response.json()

    # Calculate average valence
    if audio_features_data and 'audio_features' in audio_features_data:
        valences = [feature['valence'] for feature in audio_features_data['audio_features'] if
                    feature['valence'] is not None]
        average_valence = sum(valences) / len(valences) if valences else 0
    else:
        average_valence = -1

    # Artist Tracks
    artist_songs = {}
    # Get the top 5 artists
    top_artists_list = top_artists.get('items', [])[:5]

    # Create a set of artist names for quick lookup
    top_artist_names = {artist['name'] for artist in top_artists_list}

    # Loop through top tracks to find songs by top artists
    for track in top_tracks_data.get('items', []):
        track_artists = {artist['name'] for artist in track['artists']}

        # Check if the track's artist is one of the top artists
        for artist in top_artists_list:
            artist_name = artist['name']
            if artist_name in track_artists and artist_name not in artist_songs:
                # If the artist has a track, assign the preview URL
                artist_songs[artist_name] = track.get('preview_url')
                break  # Exit loop after finding the first song for this artist

    # Now, check for any artists without songs and fetch their most popular song
    for artist in top_artists_list:
        artist_name = artist['name']

        # If the artist doesn't have a song yet, get their most popular song
        if artist_name not in artist_songs:
            popular_songs = get_artist_songs(access_token, artist['id'])
            if popular_songs:
                artist_songs[artist_name] = popular_songs[0].get('preview_url')

    # Create a list to preserve the order of top artists
    ordered_artist_songs = {artist['name']: artist_songs.get(artist['name']) for artist in top_artists_list}

    return top_artists, genre_list, top_tracks_data, average_valence, ordered_artist_songs

def get_artist_songs(access_token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "market": "US"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("tracks", [])

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
