# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignupForm

# User Signup
def signup_view(request):
    if request.method == "POST":  # When form is submitted
        form = SignupForm(request.POST)  # Pass POST data to form
        if form.is_valid():      # Validate all fields
            user = form.save()    # Save data to database
            login(request, user)  # Log user in
            return redirect("dashboard")  # Redirect to dashboard
    else:
        form = SignupForm()  # Display empty form
    return render(request, "users/signup.html", {"form": form})

# User Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            return render(request, 'users/login.html', {
                'error': 'Invalid credentials',
                'next': request.GET.get('next', '')
            })
    return render(request, 'users/login.html', {
        'next': request.GET.get('next', '')
    })

# User Logout
def logout_view(request):
    logout(request)
    return redirect("login")

# User Dashboard (Protected Route)
@login_required
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'users/dashboard.html', {
        'user': request.user,
        'page_title': 'Dashboard'
    })
