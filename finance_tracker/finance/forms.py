from django import forms
from .models import Income, Expense, SavingsGoal

# Choices could be moved to models.py and referenced as ModelName.CHOICES
INCOME_CHOICES = [
    ('salary', 'Salary'),
    ('business', 'Business'),
    ('freelance', 'Freelance'),
    ('investment', 'Investment'),
    ('other', 'Other')
]

EXPENSE_CHOICES = [
    ('housing', 'Housing'),
    ('food', 'Food'),
    ('transportation', 'Transportation'),
    ('utilities', 'Utilities'),
    ('entertainment', 'Entertainment'),
    ('other', 'Other')
]

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['income_type', 'amount', 'date_received', 'description']
        widgets = {
            'income_type': forms.Select(attrs={
                'class': 'form-control income-type-field',
                'style': 'background-color: #f8f9fa; border-radius: 4px;'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control amount-field',
                'placeholder': '0.00'
            }),
            'date_received': forms.DateInput(attrs={
                'class': 'form-control date-field',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control description-field',
                'rows': 3,
                'placeholder': 'Enter description...'
            }),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'amount', 'date_incurred', 'description']
        widgets = {
            'expense_type': forms.Select(attrs={
                'class': 'form-control expense-type-field',
                'style': 'background-color: #f8f9fa; border-radius: 4px;'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control amount-field',
                'placeholder': '0.00'
            }),
            'date_incurred': forms.DateInput(attrs={
                'class': 'form-control date-field',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control description-field',
                'rows': 3,
                'placeholder': 'Enter description...'
            }),
        }

# finance/forms.py
from django import forms
from .models import SavingsGoal
import datetime

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'target_amount', 'current_amount', 'target_date']
        widgets = {
            'goal_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter goal name...'
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'current_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk is None:  # Only for new instances
            self.initial['current_amount'] = 0  # Set default current amount
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:  # If this is a new instance
            instance.user = self.user
        if commit:
            instance.save()
        return instance