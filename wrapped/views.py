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

def get_spotify_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{SPOTIFY_API_URL}", headers=headers)
    return response.json()

def get_spotify_top_artists(access_token, limit):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    return response.json()

def get_spotify_top_tracks(access_token):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": 5
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    return response.json()


def get_spotify_top_genres(access_token):
    artists = get_spotify_top_artists(access_token, 50).get("items", [])

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
def wrapped(request):
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    user_data = get_spotify_user_info(access_token)
    top_artists_data = get_spotify_top_artists(access_token, 5)
    top_tracks_data = get_spotify_top_tracks(access_token)
    top_genres_data = get_spotify_top_genres(access_token)

    return render(request, 'wrapped.html', {
        'user_data': user_data,
        'top_artists': top_artists_data,
        'top_tracks': top_tracks_data,
        'top_genres': top_genres_data # Pass top artists to the template
    })

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