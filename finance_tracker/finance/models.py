from django.db import models
from django.conf import settings
from django.utils import timezone

class Income(models.Model):
    INCOME_TYPE_CHOICES = [
        ('salary', 'Salary'),
        ('business', 'Business'),
        ('freelance', 'Freelance'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    income_type = models.CharField(max_length=20, choices=INCOME_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_received = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.income_type} - {self.amount}"



from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import math

class SavingsGoal(models.Model):
    goal_name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.goal_name} - ₹{self.target_amount}"

    @property
    def days_remaining(self):
        return (self.target_date - timezone.now().date()).days
    
    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        percentage = (self.current_amount / self.target_amount) * 100
        return min(100, math.floor(percentage))
    
    class Meta:
        ordering = ['target_date', '-created_at']  # This ensures goals are always ordered by target date


class Expense(models.Model):
    EXPENSE_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('utilities', 'Utilities'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_incurred = models.DateField(default=timezone.now)  # was 'date_spent'
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.expense_type} - {self.amount}"
