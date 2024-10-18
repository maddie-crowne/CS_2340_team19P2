from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def wrapped(request):
    """
    Renders the wrapped page that includes the slides.

    This view requires the user to be logged in. It renders the
    'wrapped.html' template.

    :param request: The HTTP request object associated with the user's session.
    :return: Renders the 'wrapped.html' template.
    """
    return render(request, 'wrapped.html', {

    })

@login_required
def select(request):
    """
    Renders the selection of wrapped timeframe page.

    This view requires the user to be logged in. It renders the
    'wrappedSelect.html' template.

    :param request: The HTTP request object associated with the user's session.
    :return: Renders the 'wrappedSelect.html' template.
    """
    return render(request, 'wrappedSelect.html', {

    })

@login_required
def invite(request):
    """
    Renders the invite page.

    This view requires the user to be logged in. It renders the
    'wrappedInvite.html' template.

    :param request: The HTTP request object associated with the user's session.
    :return: Renders the 'wrappedInvite.html' template.
    """
    return render(request, 'wrappedInvite.html', {

    })

@login_required
def duo(request):
    """
    Renders the duo wrapped page.

    This view requires the user to be logged in. It renders the
    'wrappedDuo.html' template.

    :param request: The HTTP request object associated with the user's session.
    :return: Renders the 'wrappedDuo.html' template.
    """
    return render(request, 'wrappedDuo.html', {

    })

@login_required
def account(request):
    """
    Renders the account information page.

    This view requires the user to be logged in. It renders the
    'accountInfo.html' template.

    :param request: The HTTP request object associated with the user's session.
    :return: Renders the 'accountInfo.html' template.
    """
    return render(request, 'accountInfo.html', {

    })