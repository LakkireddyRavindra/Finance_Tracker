# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


# User Signup
def signup_view(request):
    print("🔹 Signup View Called!")
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
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to the dashboard in the finance app
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# User Logout
def logout_view(request):
    logout(request)
    return redirect("login")

# User Dashboard (Protected Route)
@login_required
def dashboard_view(request):
    print("Dashboard view called")
    print(f"User: {request.user}")
    return render(request, 'finance/dashboard1.html', {
        'user': request.user,
        'page_title': 'Dashboard'
    })


from django.shortcuts import render
def home(request):
    return render(request, 'home.html')

