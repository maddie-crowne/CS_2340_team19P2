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
        "&show_dialog=true"
        "&state=individual"
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
