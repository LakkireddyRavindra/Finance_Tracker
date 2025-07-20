from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Home page served by TemplateView
    path('', views.home_view, name='home'),
    # Auth views
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Optional dashboard view
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
