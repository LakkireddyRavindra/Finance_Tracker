from django.contrib import admin
from .models import Income, Expense, SavingsGoal  # Relative importpython manage.py makemigrations finance

admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(SavingsGoal)