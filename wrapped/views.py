from collections import Counter
from statistics import mean

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from wrapped.models import SaveWrap
import requests

SPOTIFY_API_URL = "https://api.spotify.com/v1/me"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

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
    top_artists_data, top_genres_data, top_tracks_data, average_valence, artist_songs, genre_songs = get_spotify_top_data(access_token, time_range)

    # Save the wrap data automatically upon loading
    saved_wrap = SaveWrap(
        user=request.user,
        user_data=user_data,
        top_artists=top_artists_data,
        artist_songs=artist_songs,
        top_tracks=top_tracks_data,
        top_genres=top_genres_data,
        genre_songs=genre_songs,
        average_valence=average_valence,
        time_range=time_range
    )
    saved_wrap.save()

    return render(request, 'wrapped.html', {
        'user_data': user_data,
        'top_artists': top_artists_data,
        'artist_songs': artist_songs,
        'top_tracks': top_tracks_data,
        'top_genres': top_genres_data,
        'genre_songs': genre_songs,
        'average_valence': average_valence,
        'selected_time_range': time_range
    })

@login_required
def view_saved_wrap(request, wrap_id):
    # Get the specific saved wrap by ID
    wrap = get_object_or_404(SaveWrap, id=wrap_id, user=request.user)  # Ensure it's the current user's wrap

    # Get the user data (this will be the current user from the request)
    user_data = request.user  # User data from the authenticated user

    # Get the time range from the request, default to the wrap's time range if not provided
    time_range = request.GET.get('time_range', wrap.time_range)

    # Prepare context to pass to the template
    context = {
        'user_data': user_data,
        'top_artists': wrap.top_artists,
        'artist_songs': wrap.artist_songs,
        'top_tracks': wrap.top_tracks,
        'top_genres': wrap.top_genres,
        'genre_songs': wrap.genre_songs,
        'average_valence': wrap.average_valence,
        'selected_time_range': time_range,
    }

    # Render the wrapped.html template with the context data
    return render(request, 'wrapped.html', context)

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
        return None, [], None, 0, {}, {}
    top_artists = top_artists.json()

    # Top Genres
    artists = top_artists.get("items", [])

    if artists is None or not artists:
        return top_artists, [], None, 0, {}, {}

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
        return top_artists, genre_list, None, 0, {}, {}
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
        return top_artists, genre_list, top_tracks_data, -1, {}, {}

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

    # Check for any artists without songs and fetch their most popular song
    for artist in top_artists_list:
        artist_name = artist['name']

        # If the artist doesn't have a song yet, get their most popular song
        if artist_name not in artist_songs:
            popular_songs = get_artist_songs(access_token, artist['id'])
            if popular_songs:
                artist_songs[artist_name] = popular_songs[0].get('preview_url')

    # Create a list to preserve the order of top artists
    ordered_artist_songs = {artist['name']: artist_songs.get(artist['name']) for artist in top_artists_list}

    # Top Genre Songs
    genre_songs = {}
    added_songs = set()  # Set to keep track of added song URLs
    artist_genre_cache = {}  # Dictionary to cache artist genres

    # Function to get artist genres with caching
    def get_artist_genres_cached(artist_id):
        if artist_id in artist_genre_cache:
            return artist_genre_cache[artist_id]

        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        response = requests.get(artist_url, headers=headers)

        if response.status_code == 200:
            genres = response.json().get('genres', [])
            artist_genre_cache[artist_id] = genres  # Cache the result
            return genres
        return []

    # Loop through the list of genres
    for genre in genre_list:
        # Check each track in top_tracks
        for track in top_tracks_data.get('items', []):
            track_artists = track['artists']
            track_preview_url = track.get('preview_url')

            # Check if any of the artists in the track match the genre
            for artist in track_artists:
                artist_genres = get_artist_genres_cached(artist['id'])

                if genre.lower() in (g.lower() for g in artist_genres):
                    # If a matching artist is found and the song is not already added
                    if track_preview_url not in added_songs:
                        genre_songs[genre] = track_preview_url
                        added_songs.add(track_preview_url)  # Add the song URL to the set
                    break  # Exit the loop after checking the first matching artist

            if genre in genre_songs:
                break  # Exit the genre loop if a song was found

    return top_artists, genre_list, top_tracks_data, average_valence, ordered_artist_songs, genre_songs

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
    user = request.user
    saved = SaveWrap.objects.filter(user=user)

    context = {
        'user': user,
        'saved': saved,
    }

    return render(request, 'accountInfo.html', context)

@login_required
def delete_wrap(request, wrap_id):
    if request.method == 'POST':
        wrap = SaveWrap.objects.get(id=wrap_id, user=request.user)
        wrap.delete()
        return redirect('wrapped:account')

@login_required
def select(request):
    return render(request, 'wrappedSelect.html', {})

@login_required
def invite(request):
    return render(request, 'wrappedInvite.html', {})

@login_required
# Redirect to Spotify login
def duo_spotify_login(request):
    auth_url = (
        "https://accounts.spotify.com/authorize"
        "?response_type=code"
        f"&client_id={settings.SPOTIFY_CLIENT_ID}"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
        "&scope=user-read-private user-read-email user-top-read"
        "&show_dialog=true"
        "&state=duo"
    )
    return redirect(auth_url)

# View user account info with Spotify data
def get_spotify_token(auth_code):
    token_url = "https://accounts.spotify.com/api/token"

    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET
    })

    return response.json()

def refresh_access_token(request):
    refresh_token = request.session.get('refresh_token')

    if not refresh_token:
        return JsonResponse({'error': 'No refresh token available'}, status=401)

    token_url = "https://accounts.spotify.com/api/token"
    response = requests.post(
        token_url,
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': settings.SPOTIFY_CLIENT_ID,
            'client_secret': settings.SPOTIFY_CLIENT_SECRET,
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )

    token_data = response.json()
    access_token = token_data.get('access_token')

    # Update the session with the new access token
    request.session['access_token'] = access_token

    return JsonResponse({'access_token': access_token})

def spotify_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if code:
        # Exchange the authorization code for an access token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }
        token_response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        # Get user's Spotify profile data
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        profile_response = requests.get(SPOTIFY_API_URL, headers=headers)
        profile_data = profile_response.json()

        # Optionally save the access_token and profile data in the session or database
        request.session['spotify_access_token'] = access_token
        request.session['spotify_profile'] = profile_data

        # Redirect to a duo wrapped page
        if state == "duo":
            # This is the second user, save their token and profile as "user2"
            request.session['spotify_access_token_user2'] = access_token
            request.session['spotify_profile_user2'] = profile_data
            return redirect('wrapped:duo')  # Redirect to the duo page
        else:
            # This is the first user, save their token and profile
            request.session['spotify_access_token'] = access_token
            request.session['spotify_profile'] = profile_data
            return redirect('wrapped:select')  # Redirect to the select page

    else:
        # Handle the case where the code is missing
        return render(request, 'error.html', {"message": "Failed to authenticate with Spotify"})

@login_required
def duo(request):
    access_token_user1 = request.session.get('spotify_access_token')
    profile_user1 = request.session.get('spotify_profile')

    # Get user's top artists
    top_artists_url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token_user1}"}
    params = {"limit": 50}
    top_artists_response = requests.get(top_artists_url, headers=headers, params=params)

    if top_artists_response.status_code != 200:
        return redirect('spotify_login')  # Redirect if we can't fetch the top artists

    top_artists_data_user1 = top_artists_response.json()

    # Get user's top tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
    top_tracks_response = requests.get(top_tracks_url, headers=headers, params=params)

    if top_tracks_response.status_code != 200:
        return redirect('spotify_login')  # Redirect if we can't fetch the top tracks

    top_tracks_data_user1 = top_tracks_response.json()
    track_ids_user1 = [track['id'] for track in top_tracks_data_user1.get('items', []) if track.get('id')]

    # Get audio features for the top tracks
    audio_features_data_user1 = get_audio_features(access_token_user1, track_ids_user1)

    # Calculate the average values for the requested audio features
    valence_user1, averages_user1 = calculate_averages(audio_features_data_user1)

    access_token_user2 = request.session.get('spotify_access_token_user2')
    profile_user2 = request.session.get('spotify_profile_user2')

    # Get user's top artists
    headers = {"Authorization": f"Bearer {access_token_user2}"}
    top_artists_response = requests.get(top_artists_url, headers=headers, params=params)

    if top_artists_response.status_code != 200:
        return redirect('spotify_login')  # Redirect if we can't fetch the top artists

    top_artists_data_user2 = top_artists_response.json()

    # Get user's top tracks
    top_tracks_response = requests.get(top_tracks_url, headers=headers, params=params)

    if top_tracks_response.status_code != 200:
        return redirect('spotify_login')  # Redirect if we can't fetch the top tracks

    top_tracks_data_user2 = top_tracks_response.json()
    track_ids_user2 = [track['id'] for track in top_tracks_data_user2.get('items', []) if track.get('id')]

    # Get audio features for the top tracks
    audio_features_data_user2 = get_audio_features(access_token_user2, track_ids_user2)

    # Calculate the average values for the requested audio features
    valence_user2, averages_user2 = calculate_averages(audio_features_data_user2)

    # Calculate compatibility
    compatibility = calculate_compatibility(top_artists_data_user1, top_tracks_data_user1, averages_user1, top_artists_data_user2, top_tracks_data_user2, averages_user2)

    return render(request, 'wrappedDuo.html', {
        'user1': profile_user1,
        'user2': profile_user2,
        'compatibility': compatibility,
        'valence_user1': valence_user1,
        'valence_user2': valence_user2,
        'top_tracks_user1': top_tracks_data_user1,
        'top_tracks_user2': top_tracks_data_user2
    })

# Function to calculate compatibility
def calculate_compatibility(top_artists_user1, top_tracks_user1, averages_user1, top_artists_user2, top_tracks_user2, averages_user2):
    # Calculate the percentage of matching artists
    artists_user1 = set([artist['id'] for artist in top_artists_user1['items']])
    artists_user2 = set([artist['id'] for artist in top_artists_user2['items']])
    matching_artists = len(artists_user1.intersection(artists_user2))
    artist_compatibility = (matching_artists / 50) * 100  # 50 is the limit

    # Calculate the percentage of matching tracks
    tracks_user1 = set([track['id'] for track in top_tracks_user1['items']])
    tracks_user2 = set([track['id'] for track in top_tracks_user2['items']])
    matching_tracks = len(tracks_user1.intersection(tracks_user2))
    track_compatibility = (matching_tracks / 50) * 100  # 50 is the limit

    # Calculate the percentage of matching audio features
    feature_compatibility = 0
    total_features = len(averages_user1)
    for feature in averages_user1:
        if abs(averages_user1[feature] - averages_user2[feature]) <= 0.20:
            feature_compatibility += 1

    feature_compatibility = (feature_compatibility / total_features) * 100

    # Final compatibility score: 30% artists, 30% tracks, 40% audio features
    total_compatibility = (artist_compatibility * 0.3) + (track_compatibility * 0.3) + (feature_compatibility * 0.4)

    return round(total_compatibility, 2)

# Function to get the audio features of multiple tracks
def get_audio_features(access_token, track_ids):
    url = "https://api.spotify.com/v1/audio-features"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "ids": ','.join(track_ids)
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("audio_features", [])
    return []

# Calculate averages for valence, danceability, energy, instrumentalness, and tempo
def calculate_averages(audio_features_data):
    features = {
        'valence': [],
        'danceability': [],
        'energy': [],
        'instrumentalness': [],
        'tempo': []
    }

    for feature in audio_features_data:
        if feature:
            for key in features.keys():
                value = feature.get(key)
                if value is not None:
                    features[key].append(value)

    averages = {}
    for key, values in features.items():
        if values:
            averages[key] = mean(values)
        else:
            averages[key] = 0  # Default to 0 if no values are available

    return averages['valence'], averages