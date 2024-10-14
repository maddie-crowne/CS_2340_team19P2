from django.shortcuts import render

def wrapped(request):
    return render(request, 'wrapped.html', {

    })

def select(request):
    return render(request, 'wrappedSelect.html', {

    })

def invite(request):
    return render(request, 'wrappedInvite.html', {

    })

def duo(request):
    return render(request, 'wrappedDuo.html', {

    })

def account(request):
    return render(request, 'accountInfo.html', {

    })