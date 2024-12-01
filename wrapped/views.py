from collections import Counter
from statistics import mean

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from wrapped.models import SaveWrap, SaveDuoWrap
import requests

SPOTIFY_API_URL = "https://api.spotify.com/v1/me"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


@login_required
def user_spotify_login(request):
    """
    Renders the Spotify login page, requiring the user to be logged in.

    :param request: The HTTP request object.
    :return: HttpResponse: The rendered login page for Spotify authentication.
    """
    return render(request, 'loginWithSpotify.html', {})


@login_required
def wrapped(request):
    """
    Retrieves and displays the user's Spotify Wrapped data, saves it to the database,
    and renders the wrapped view. The data includes top artists, top tracks, top genres,
    and average valence over a specified time range.

    :param request: The HTTP request object, which should contain the access token and time range parameters.
    :return: HttpResponse: The rendered Wrapped page displaying the user's Spotify stats.
    """
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    time_range = request.GET.get('time_range', 'medium_term')

    user_data = get_spotify_user_info(access_token)
    top_artists_data, top_genres_data, top_tracks_data, average_valence, artist_songs, genre_songs = get_spotify_top_data(
        access_token, time_range)

    # Save the wrap data automatically upon loading
    saved_wrap = SaveWrap(
        user=request.user,
        user_data=user_data,
        top_artists=top_artists_data,
        artist_songs=artist_songs,
        top_tracks=top_tracks_data,
        top_genres=top_genres_data,
        genre_songs=genre_songs,
        average_valence=round(average_valence * 100),
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
        'average_valence': round(average_valence * 100),
        'selected_time_range': time_range
    })


@login_required
def view_saved_wrap(request, wrap_id):
    """
    Retrieves and displays a specific saved Spotify Wrapped data for the current user by ID.

    :param request: The HTTP request object.
    :param wrap_id: The ID of the saved Spotify Wrapped data to retrieve.
    :return: HttpResponse: The rendered Wrapped page displaying the saved Wrapped data.
    """
    # Get the specific saved wrap by ID
    wrap = get_object_or_404(SaveWrap, id=wrap_id, user=request.user)  # Ensure it's the current user's wrap

    # Get the time range from the request, default to the wrap's time range if not provided
    time_range = request.GET.get('time_range', wrap.time_range)

    # Prepare context to pass to the template
    context = {
        'user_data': wrap.user_data,
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
    """
    Fetches the current user's profile information from the Spotify API.

    :param access_token: The user's Spotify access token for authentication.
    :return: dict: The JSON response containing the user's profile information.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{SPOTIFY_API_URL}", headers=headers)
    return response.json()


def get_spotify_top_data(access_token, time_range):
    """
    Retrieves the user's top artists, top genres, top tracks, average valence,
    and associated songs for a given time range using the Spotify API.

    :param access_token: The user's Spotify access token for authentication.
    :param time_range: The time range to query for top artists, tracks, and genres (e.g., 'short_term', 'medium_term', 'long_term').
    :return: tuple: A tuple containing:
            - top_artists (list): The user's top artists.
            - genre_list (list): A list of the user's top genres.
            - top_tracks_data (dict): The user's top tracks.
            - average_valence (float): The average valence of the user's top tracks.
            - ordered_artist_songs (dict): A dictionary of top artists and their songs.
            - genre_songs (dict): A dictionary of genres and associated tracks.
    """
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
        """
        Fetches the genres of a specific artist, caching the result for efficiency.

        :param artist_id: The Spotify ID of the artist.
        :return: A list of genres associated with the artist.
        """
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
                print(genre_songs[genre])
                break  # Exit the genre loop if a song was found

    return top_artists, genre_list, top_tracks_data, average_valence, ordered_artist_songs, genre_songs


def get_artist_songs(access_token, artist_id):
    """
    Fetches the top tracks of a specific artist from Spotify based on their artist ID.

    :param access_token: The Spotify access token for authentication.
    :param artist_id: The Spotify ID of the artist whose top tracks are to be retrieved.
    :return: list: A list of top tracks for the given artist, where each track is represented as a dictionary.
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "market": "US"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("tracks", [])


@login_required
def account(request):
    """
    Renders the user's account page with their saved wraps, Spotify profile data, and duo wraps.

    :param request: The HTTP request object associated with the user's session.
    :return: Renders the 'accountInfo.html' template with user, Spotify, and wrap data.
    """
    user = request.user
    saved = SaveWrap.objects.filter(user=user)
    duo_saved = SaveDuoWrap.objects.filter(user=user)

    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    user_data = get_spotify_user_info(access_token)

    # Extract profile picture (if available)
    profile_image = None
    if user_data.get('images'):
        profile_image = user_data['images'][0].get('url')

    context = {
        'user': user,
        'saved': saved,
        'duo_saved': duo_saved,
        'user_data': user_data,
        'profile_image': profile_image,
    }

    return render(request, 'accountInfo.html', context)


@login_required
def delete_wrap(request, wrap_id):
    """
    Deletes a saved wrap based on the provided wrap ID, and redirects to the user's account page.

    :param request: The HTTP request object.
    :param wrap_id: The ID of the wrap to be deleted.
    :return: HttpResponseRedirect: Redirects to the 'account' page after deleting the wrap.
    """
    if request.method == 'POST':
        wrap = SaveWrap.objects.get(id=wrap_id, user=request.user)
        wrap.delete()
        return redirect('wrapped:account')


@login_required
def delete_duo_wrap(request, wrap_id):
    """
    Deletes a saved duo wrap based on the provided wrap ID, and redirects to the user's account page.

    :param request: The HTTP request object.
    :param wrap_id: The ID of the duo wrap to be deleted.
    :return: HttpResponseRedirect: Redirects to the 'account' page after deleting the duo wrap.
    """
    if request.method == 'POST':
        wrap = SaveDuoWrap.objects.get(id=wrap_id, user=request.user)
        wrap.delete()
        return redirect('wrapped:account')


@login_required
def select(request):
    """
    Renders the select page with the user's Spotify profile data for choosing a wrap option.

    :param request: The HTTP request object associated with the user's session.
    :return: HttpResponse: The rendered 'wrappedSelect.html' template displaying the user's Spotify data.
    """
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    # Retrieve Spotify user data
    user_data = get_spotify_user_info(access_token)

    # Pass user_data to the template
    return render(request, 'wrappedSelect.html', {
        'user_data': user_data
    })


@login_required
def invite(request):
    """
    Renders the invite page, allowing users to invite others to join.

    :param request: The HTTP request object associated with the user's session.
    :return: HttpResponse: The rendered 'wrappedInvite.html' template for inviting others.
    """
    return render(request, 'wrappedInvite.html', {})


@login_required
# Redirect to Spotify login
def duo_spotify_login(request):
    """
    Redirects the user to Spotify's authorization page for Duo login. This allows users to log in
    and authenticate via Spotify for the purpose of sharing wrap data between two users.

    :param request: The HTTP request object associated with the user's session.
    :return: HttpResponseRedirect: A redirect to Spotify's authorization page for Duo login.
    """
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
    """
    Retrieves an access token from Spotify using the provided authorization code.

    :param auth_code: The authorization code received after the user logs in via Spotify.
    :return: dict: A JSON response containing the access token and refresh token (if applicable).
    """
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
    """
    Refreshes the Spotify access token using the stored refresh token from the session.

    :param request: The HTTP request object associated with the user's session.
    :return: JsonResponse: A JSON response containing the new access token or an error message if the refresh token is missing.
    """
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
    """
    Handles the Spotify OAuth callback by exchanging the authorization code for an access token,
    fetching the user's Spotify profile, and saving the necessary data in the session.

    :param request: The HTTP request object containing the authorization code and state parameter.
    :return: HttpResponseRedirect: Redirects to the appropriate page after successful authentication (either 'duo' or 'select').
                HttpResponse: Renders an error page if authentication fails due to missing code.
    """
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
    """
    Renders the duo wrapped page, calculates the compatibility between two users based on their top Spotify artists,
    tracks, and audio features. Saves the wrap data and displays the results.

    :param request: The HTTP request object associated with the user's session.
    :return: HttpResponseRedirect: Redirects to the login page if the user is not authenticated or if Spotify data is missing.
                HttpResponse: Renders the 'wrappedDuo.html' template with the calculated compatibility and Spotify data for both users.
    """
    access_token_user1 = request.session.get('spotify_access_token')
    profile_user1 = request.session.get('spotify_profile')

    if not access_token_user1 or not profile_user1:
        return redirect('spotify_login')

    user1_display_name = profile_user1.get('display_name', 'User1')
    user1_first_name = user1_display_name.split(' ')[0] if user1_display_name else 'User1'

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

    # Get top 5 tracks preview URLs for user 1
    top_5_tracks_user1 = top_tracks_data_user1['items'][:5]  # Get the top 5 tracks
    preview_urls_user1 = [track['preview_url'] for track in top_5_tracks_user1]

    # Get audio features for the top tracks
    audio_features_data_user1 = get_audio_features(access_token_user1, track_ids_user1)

    # Calculate the average values for the requested audio features
    valence_user1, averages_user1 = calculate_averages(audio_features_data_user1)

    access_token_user2 = request.session.get('spotify_access_token_user2')
    profile_user2 = request.session.get('spotify_profile_user2')

    if not access_token_user2 or not profile_user2:
        return redirect('spotify_login')

    user2_display_name = profile_user2.get('display_name', 'User2')
    user2_first_name = user2_display_name.split(' ')[0] if user2_display_name else 'User2'

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

    # Get top 5 tracks preview URLs for user 1
    top_5_tracks_user2 = top_tracks_data_user2['items'][:5]  # Get the top 5 tracks
    preview_urls_user2 = [track['preview_url'] for track in top_5_tracks_user2]

    # Get audio features for the top tracks
    audio_features_data_user2 = get_audio_features(access_token_user2, track_ids_user2)

    # Calculate the average values for the requested audio features
    valence_user2, averages_user2 = calculate_averages(audio_features_data_user2)

    # Calculate compatibility
    compatibility = calculate_compatibility(top_artists_data_user1, top_tracks_data_user1, averages_user1,
                                            top_artists_data_user2, top_tracks_data_user2, averages_user2)

    # Interleave the preview URLs of the top 5 tracks of each user
    interleaved_preview_urls = []
    for i in range(3):
        if i < len(preview_urls_user1):
            interleaved_preview_urls.append(preview_urls_user1[i])
        if i < len(preview_urls_user2) and i < 2:
            interleaved_preview_urls.append(preview_urls_user2[i])

    user1_profile_pic = profile_user1.get('images', [{}])[0].get('url',
                                                                 '')  # Get the first image URL or an empty string
    user2_profile_pic = profile_user2.get('images', [{}])[0].get('url', '')

    # Save the wrap data automatically upon loading
    saved_wrap = SaveDuoWrap(
        user=request.user,
        user1_data=profile_user1,
        user2_data=profile_user2,
        compatibility=round(compatibility),
        valence_user1=round(valence_user1 * 100),
        valence_user2=round(valence_user2 * 100),
        top_tracks_user1=top_tracks_data_user1,
        top_tracks_user2=top_tracks_data_user2,
        interleaved_preview_urls=interleaved_preview_urls
    )
    saved_wrap.save()

    # Pass the first names to the template
    return render(request, 'wrappedDuo.html', {
        'user1_data': profile_user1,
        'user2_data': profile_user2,
        'compatibility': round(compatibility),
        'valence_user1': round(valence_user1 * 100),
        'valence_user2': round(valence_user2 * 100),
        'top_tracks_user1': top_tracks_data_user1,
        'top_tracks_user2': top_tracks_data_user2,
        'interleaved_preview_urls': interleaved_preview_urls
    })


# Function to calculate compatibility
def calculate_compatibility(top_artists_user1, top_tracks_user1, averages_user1, top_artists_user2, top_tracks_user2,
                            averages_user2):
    """
    Calculates the compatibility score between two users based on their top Spotify artists, tracks, and audio features.

    :param top_artists_user1: The top artists data for user 1 from Spotify.
    :param top_tracks_user1: The top tracks data for user 1 from Spotify.
    :param averages_user1: The average audio features for user 1's top tracks.
    :param top_artists_user2: The top artists data for user 2 from Spotify.
    :param top_tracks_user2: The top tracks data for user 2 from Spotify.
    :param averages_user2: The average audio features for user 2's top tracks.
    :return: The compatibility score between 0 and 100, based on matching artists, tracks, and audio features.
    """
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

    return total_compatibility


# Function to get the audio features of multiple tracks
def get_audio_features(access_token, track_ids):
    """
    Fetches the audio features of multiple tracks from the Spotify API.

    :param access_token: The OAuth access token for the authenticated user.
    :param track_ids: A list of track IDs to fetch the audio features for.
    :return: A list of audio feature dictionaries for each track, or an empty list if the request fails.
    """
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
    """
    Calculates the average values for specific audio features: valence, danceability, energy, instrumentalness, and tempo.

    :param audio_features_data: A list of audio feature dictionaries for multiple tracks.
    :return: A tuple containing the average valence value and a dictionary with the average values for each feature.
    """
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


@login_required
def view_saved_duo_wrap(request, wrap_id):
    """
    Retrieves and displays the details of a saved duo wrap based on the provided wrap ID.

    The saved wrap includes user data, compatibility score, valence values, top tracks, and interleaved preview URLs.

    :param request: The HTTP request object associated with the current user.
    :param wrap_id: The ID of the saved wrap to retrieve and display.
    :return: HttpResponse: Renders the 'wrappedDuo.html' template with the saved wrap data.
    """
    # Get the specific saved wrap by ID
    wrap = get_object_or_404(SaveDuoWrap, id=wrap_id, user=request.user)  # Ensure it's the current user's wrap

    # Prepare context to pass to the template
    context = {
        'user1_data': wrap.user1_data,
        'user2_data': wrap.user2_data,
        'compatibility': wrap.compatibility,
        'valence_user1': wrap.valence_user1,
        'valence_user2': wrap.valence_user2,
        'top_tracks_user1': wrap.top_tracks_user1,
        'top_tracks_user2': wrap.top_tracks_user2,
        'interleaved_preview_urls': wrap.interleaved_preview_urls
    }

    # Render the wrapped.html template with the context data
    return render(request, 'wrappedDuo.html', context)


@login_required
def contact_developers(request):
    """
    Renders the contact developers page.

    This view requires the user to be logged in. It renders a template
    where users can contact the developers. The request context is passed
    to the template, allowing for further customization if needed in the future.

    :param request: The HTTP request object associated with the user's session.
    :return: Renders the 'contactDevelopers.html' template.
    """
    return render(request, 'contactDevelopers.html', {})
