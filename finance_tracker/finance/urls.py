from django.urls import path
from . import views
from .views import delete_income

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('income/', views.income, name='income'),
    path('income/delete/<int:income_id>/', delete_income, name='delete_income'),

    path('savings/', views.savings, name='savings'),
    path('savings/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),

    path('expenditure/', views.expenditure, name='expenditure'),
    path('expense/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),

    path('transactions/', views.transactions, name='transactions'),
    # ... other URL patterns ...
]
