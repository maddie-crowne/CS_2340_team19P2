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
    """
    Redirects the user to the Spotify login page with the necessary
    authentication parameters. This is the first step in the OAuth flow.

    The user is redirected to Spotify's authorization URL to log in and
    grant the application the necessary permissions.

    :param request: The HTTP request object
    :return: HttpResponseRedirect: Redirects to the Spotify login page for authentication.
    """
    auth_url = (
        "https://accounts.spotify.com/authorize"
        "?response_type=code"
        f"&client_id={settings.SPOTIFY_CLIENT_ID}"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
        "&scope=user-read-private user-read-email user-top-read"
        "&show_dialog=true"
        "&state=individual"
    )
    return redirect(auth_url)

# View user account info with Spotify data
def get_spotify_token(auth_code):
    """
    Exchange the provided authorization code for an access token and refresh token
    from Spotify's API.

    This function is used to complete the OAuth flow by exchanging the authorization
    code received from the Spotify API for access and refresh tokens, which are required
    to make further authenticated requests to the Spotify API on behalf of the user.

    :param auth_code: The authorization code returned by Spotify after the user logs in.
    :return: dict: The response from Spotify, typically containing access and refresh tokens.
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
    Refresh the Spotify access token using the refresh token stored in the session.

    If the access token has expired, this function retrieves a new access token using
    the refresh token. The new access token is then stored in the session for subsequent
    requests.

    :param request: The HTTP request object containing the session with the refresh token.
    :return: JsonResponse: A JSON response containing the new access token, or an error message if the refresh token is unavailable.
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
    Handles the callback from Spotify's OAuth flow, exchanging the authorization code
    for an access token and fetching the user's Spotify profile data.

    Once the authorization code is received from Spotify, this function exchanges it
    for an access token, retrieves the user's profile data, and stores both in the session.
    It then redirects to either a "duo" or "select" page based on the state parameter.

    :param request: The HTTP request object, which contains the authorization code and state.
    :return: HttpResponseRedirect: Redirects to the next page after authentication (either "duo" or "select").
                Rendered response: If the authorization code is missing, renders an error page.
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

        if state == "duo":
            # This is the second user, save their token and profile as "user2"
            request.session['spotify_access_token_user2'] = access_token
            request.session['spotify_profile_user2'] = profile_data
            return redirect('wrapped:duo')  # Redirect to the duo page
        else:
            # This is the first user, save their token and profile
            request.session['spotify_access_token'] = access_token
            request.session['spotify_profile'] = profile_data
            return redirect('wrapped:select')  # Redirect to the select page (or wherever)

    else:
        # Handle the case where the code is missing
        return render(request, 'error.html', {"message": "Failed to authenticate with Spotify"})
