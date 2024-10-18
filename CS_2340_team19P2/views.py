from django.contrib.auth.decorators import login_required
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1/me"

@login_required
# Redirect to Spotify login
def spotify_login(request):
    auth_url = (
        "https://accounts.spotify.com/authorize"
        "?response_type=code"
        f"&client_id={settings.SPOTIFY_CLIENT_ID}"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
        "&scope=user-read-private user-read-email user-top-read"
        "&show_dialog=true"  # Add this to force reauthorization
    )
    return redirect(auth_url)
# Handle Spotify callback after user authorizes
def spotify_callback(request):
    code = request.GET.get('code')
    token_url = "https://accounts.spotify.com/api/token"

    response = requests.post(token_url,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )

    token_data = response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    # Check if access token is successfully obtained
    print("Access Token:", access_token)

    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token

    return JsonResponse({'access_token': access_token, 'refresh_token': refresh_token})
# View user account info with Spotify data
def account(request):
    access_token = request.session.get('access_token')

    if not access_token:
        return redirect('spotify_login')

    user_profile_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(user_profile_url, headers=headers)

    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch user data'}, status=response.status_code)

    user_data = response.json()

    return render(request, 'accountInfo.html', {'user': user_data})

def get_spotify_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{SPOTIFY_API_URL}", headers=headers)
    return response.json()

def get_spotify_top_artists(access_token):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": 10  # You can specify how many top artists you want to retrieve
    }

    response = requests.get(url, headers=headers, params=params)

    # Print the status code and response for debugging
    print("Spotify API Status Code:", response.status_code)
    print("Spotify API Response:", response.json())

    if response.status_code != 200:
        return None

    return response.json()

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

@login_required
def select(request):
    return render(request, 'wrappedSelect.html', {

    })
@login_required
def invite(request):
    return render(request, 'wrappedInvite.html', {

    })

@login_required
def duo(request):
    return render(request, 'wrappedDuo.html', {

    })

@login_required
def wrapped(request):
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    user_data = get_spotify_user_info(access_token)
    top_artists_data = get_spotify_top_artists(access_token)

    if top_artists_data is None:
        print("Top artists data is not available.")
    else:
        print("Top artists retrieved successfully.")

    return render(request, 'wrapped.html', {
        'user_data': user_data,
        'top_artists': top_artists_data  # Pass top artists to the template
    })
def spotify_callback(request):
    code = request.GET.get('code')

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

        # Redirect to a view (like 'wrapped') after login
        return redirect('wrapped')

    else:
        # Handle the case where the code is missing
        return render(request, 'error.html', {"message": "Failed to authenticate with Spotify"})
@login_required
def contactDevelopers(request):
    """
    Renders the contact developers page.

    This view requires the user to be logged in. It renders a template
    where users can contact the developers. The request context is passed
    to the template, allowing for further customization if needed in the future.

    :param request: The HTTP request object associated with the user's session.
    :return: Renders the 'contactDevelopers.html' template.
    """
    return render(request, 'contactDevelopers.html', {

    })
