from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('wrapped:select')  # Redirect to the Google Maps page
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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('wrapped:select')  # Redirect to the wrappedSelect page
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

# Logout view
def user_logout(request):
    logout(request)
    return redirect('auth:user_login')  # Redirect to login page after logout

def delete_account(request):
    if request.method == 'POST':
        # Delete the user account
        request.user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('auth:user_login')  # Redirect to a home or login page

    return render(request, 'accountInfo.html')  # Or redirect to the account info page