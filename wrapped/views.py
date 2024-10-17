from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def wrapped(request):
    return render(request, 'wrapped.html', {

    })

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
def account(request):
    return render(request, 'accountInfo.html', {

    })