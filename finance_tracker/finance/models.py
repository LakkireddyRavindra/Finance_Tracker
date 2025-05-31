from django.db import models
from django.conf import settings  # Add this import
from django.utils import timezone
import logging
from datetime import date
# Remove: from django.contrib.auth.models import User

from django.db import models
from django.conf import settings

class Income(models.Model):
    INCOME_TYPE_CHOICES = [
        ('SALARY', 'Salary'),
        ('BUSINESS', 'Business'),
        ('INVESTMENT', 'Investment'),
        ('FREELANCE', 'Freelance'),
        ('RENTAL', 'Rental'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    income_type = models.CharField(max_length=20, choices=INCOME_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_received = models.DateField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'finance_income'
        ordering = ['-date_received']

    def __str__(self):
        return f"{self.get_income_type_display()} - ₹{self.amount}"

class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('FOOD', 'Food'),
        ('TRANSPORT', 'Transport'),
        ('HOUSING', 'Housing'),
        ('UTILITIES', 'Utilities'),
        ('HEALTHCARE', 'Healthcare'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('EDUCATION', 'Education'),
        ('SHOPPING', 'Shopping'),
        ('OTHER', 'Other'),
    ]
    
    SOURCE_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Account'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DIGITAL_WALLET', 'Digital Wallet'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Changed from User
        on_delete=models.CASCADE
    )
    expense_type = models.CharField(
    max_length=20,
    choices=EXPENSE_TYPE_CHOICES,
    default='OTHER'  # Add this line
)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_incurred = models.DateField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    description = models.TextField(blank=True, null=True)


    class Meta:
        db_table = 'finance_expense'  # Maps to existing table
        ordering = ['-date_incurred']

    def __str__(self):
        return f"{self.get_expense_type_display()} - ₹{self.amount}"

class SavingsGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Changed from User
        on_delete=models.CASCADE
    )
    goal_name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
   

    class Meta:
        db_table = 'finance_savingsgoal'  # Maps to existing table
        ordering = ['target_date']

    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100

    @property
    def days_remaining(self):
        return (self.target_date - date.today()).days

    def __str__(self):
        return f"{self.goal_name} - ₹{self.current_amount}/₹{self.target_amount}"
