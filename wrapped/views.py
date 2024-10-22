from urllib.parse import urlencode

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
        "&scope=user-read-private user-read-email"
    )
    return redirect(auth_url)


# Handle Spotify callback after user authorizes
def spotify_callback(request):
    code = request.GET.get('code')

    if not code:
        return JsonResponse({'error': 'No authorization code received'}, status=400)

    response = requests.post(SPOTIFY_TOKEN_URL,
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

    if 'error' in token_data:
        return JsonResponse({'error': token_data['error']}, status=400)

    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token

    return redirect('account')  # Redirect to the account page after successful login

# View user account info with Spotify data
def account(request):
    # access_token = request.session.get('access_token')
    # if not access_token:
    #     return redirect('spotify_login')
    #
    # user_profile_url = "https://api.spotify.com/v1/me"
    # headers = {"Authorization": f"Bearer {access_token}"}
    #
    # response = requests.get(user_profile_url, headers=headers)
    #
    # if response.status_code != 200:
    #     return JsonResponse({'error': 'Failed to fetch user data'}, status=response.status_code)
    #
    # user_data = response.json()
    #
    # return render(request, 'accountInfo.html', {'user': user_data})
    return render(request, 'accountInfo.html')

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
def wrapped(request):
    return render(request, 'wrapped.html', {})

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