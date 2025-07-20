from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Income
    path('income/', views.income, name='income'),
    path('income/<int:id>/', views.income, name='edit_income'),
    path('income/delete/<int:id>/', views.delete_income, name='delete_income'),

    # Expense
    path('expense/', views.expense, name='expense'),
    path('expense/<int:edit_id>/', views.expense, name='edit_expense'),
    path('expense/delete/<int:id>/', views.delete_expense, name='delete_expense'),

    # Savings
    path('savings/', views.savings, name='savings'),
    path('savings/edit/<int:edit_id>/', views.savings, name='edit_savings'),


    path('savings/delete/<int:goal_id>/', views.delete_savings, name='delete_savings'),
    # There was a problem that I am unable to edit only in savings

    # Transactions
    path('transactions/', views.transactions, name='transactions'),

    # Downloads
    path('expenses/download/', views.download_expenses, name='download_expenses'),
    path('income/download/', views.download_income, name='download_income'),
    path('savings/download/', views.download_savings, name='download_savings'),
    path('transactions/download/', views.download_transactions, name='download_transactions'),
]