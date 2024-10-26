from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    """
    Handles user registration.

    This view processes both GET and POST requests. If the request method is
    POST, it means the user has submitted the registration form. The function
    validates the form and creates a new user if the data is valid. After
    successful registration, the user is logged in and redirected to a
    specified page. If the form is invalid, error messages are added to the
    request's messages to inform the user.

    If the request method is GET, it initializes an empty registration form
    for the user to fill out.

    :param request: The HTTP request object containing data submitted by the user.
    :return: HttpResponse: Renders the registration template with the form or
                redirects the user upon successful registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('wr')  # Redirect to the Google Maps page
        else:
            # Iterate over form errors and add to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



# Login view
def user_login(request):
    """
    Handles user login functionality.

    This view processes both GET and POST requests. When the user submits
the login form via a POST request, the function attempts to authenticate
    the user using the provided username and password. If authentication is
    successful, the user is logged in and redirected to a specified page.
    If the authentication fails, an error message is added to the request's
    messages to inform the user of the invalid credentials.

    If the request method is GET, the login page is rendered for the user
    to enter their credentials.

    :param request: The HTTP request object containing data submitted by the user.
    :return: HttpResponse: Renders the login template or redirects the user
                upon successful authentication.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('wrapped:user_spotify_login')  # Redirect to the login with Spotify page
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

# Logout view
def user_logout(request):
    """
    Handles user logout functionality.

    This view logs the user out of the application and redirects them to
    the login page. The logout process clears the user's session and
    any authentication information.

    :param request: The HTTP request object associated with the user's session.
    :return: HTTPResponse: Redirects the user to the login page after successful logout.
    """
    logout(request)
    return redirect('auth:user_login')  # Redirect to login page after logout

def delete_account(request):
    """
    Handles user account deletion.

    This view processes both GET and POST requests. If the request method is
    POST, the function deletes the user's account and adds a success message
    to inform the user. After deletion, the user is redirected to the login
    page. If the request method is GET, the account information page is rendered
    to confirm the deletion action.

    :param request: The HTTP request object associated with the user's session.
    :return: HttpResponse: Redirects the user to the login page after account deletion
                or renders the account information page for confirmation.
    """
    if request.method == 'POST':
        # Delete the user account
        request.user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('auth:user_login')  # Redirect to a home or login page

    return render(request, 'accountInfo.html')  # Or redirect to the account info page