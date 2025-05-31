from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignupForm

from django.shortcuts import render

def home_view(request):
    return render(request, 'users/home.html')

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('finance:dashboard')  # Redirect to finance dashboard
    else:
        form = SignupForm()
    return render(request, "users/signup.html", {"form": form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or 'finance:dashboard'  # Default to finance dashboard
            return redirect(next_url)
        else:
            return render(request, 'users/login.html', {
                'error': 'Invalid credentials',
                'next': request.GET.get('next', 'finance:dashboard')  # Default to finance dashboard
            })
    return render(request, 'users/login.html', {
        'next': request.GET.get('next', 'finance:dashboard')  # Default to finance dashboard
    })

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect("home")  # Redirect to home after logout

@login_required
def dashboard_view(request):
    """Dashboard view - decide if you want to keep this or use finance dashboard"""
    return render(request, 'users/dashboard.html', {
        'user': request.user,
        'page_title': 'Dashboard'
    })