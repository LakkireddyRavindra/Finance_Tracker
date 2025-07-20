from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Default home page
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Optional - can remove if using finance dashboard
]