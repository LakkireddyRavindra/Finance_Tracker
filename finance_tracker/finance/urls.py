from django.urls import path
from . import views

app_name = 'finance'
urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    
    # Income

    path('income/<int:id>/', views.income, name='edit_income'),
    path('income/delete/<int:id>/', views.delete_income, name='delete_income'),
    path('income/', views.income, name='income'),


    path('expense/', views.expense, name='expense'),
    path('expense/<int:id>/', views.expense, name='edit_expense'),  # For editing
    path('expense/delete/<int:id>/', views.delete_expense, name='delete_expense'),
    
    # Savings
    path('savings/', views.savings, name='savings'),
    path('savings/<int:id>/', views.savings, name='edit_savings'),  # Edit URL
    path('savings/delete/<int:id>/', views.delete_savings, name='delete_savings'),
    # Transactions
    path('transactions/', views.transactions, name='transactions'),
]