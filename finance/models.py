from django.db import models
from django.conf import settings
from datetime import date
import logging

logger = logging.getLogger(__name__)

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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    expense_type = models.CharField(
        max_length=20,
        choices=EXPENSE_TYPE_CHOICES,
        default='OTHER'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_incurred = models.DateField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'finance_expense'
        ordering = ['-date_incurred']

    def __str__(self):
        return f"{self.get_expense_type_display()} - ₹{self.amount}"

class SavingsGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    goal_name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_savingsgoal'
        ordering = ['target_date']

    @property
    def progress_percentage(self):
        try:
            if self.target_amount:
                return (self.current_amount / self.target_amount) * 100
        except (ZeroDivisionError, TypeError):
            pass
        return 0

    @property
    def days_remaining(self):
        return (self.target_date - date.today()).days

    def __str__(self):
        return f"{self.goal_name} - ₹{self.current_amount}/₹{self.target_amount}"
