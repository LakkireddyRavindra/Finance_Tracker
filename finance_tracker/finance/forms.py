from django import forms
from .models import Income, Expense, SavingsGoal
from django.utils import timezone
from django.core.exceptions import ValidationError

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['income_type', 'amount', 'date_received', 'description']
        widgets = {
            'date_received': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date()
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.01,
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'income_type': 'Income Type',
            'date_received': 'Date Received'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['income_type'].widget.attrs.update({'class': 'form-select'})

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero")
        return amount

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'amount', 'date_incurred', 'source', 'description']
        widgets = {
            'date_incurred': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date()
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.01,
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'expense_type': 'Expense Category',
            'date_incurred': 'Date Incurred'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expense_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['source'].widget.attrs.update({'class': 'form-select'})

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero")
        return amount

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'target_amount', 'current_amount', 'target_date', 'description']
        widgets = {
            'target_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date()
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.01,
                'step': '0.01'
            }),
            'current_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'goal_name': 'Goal Name',
            'target_amount': 'Target Amount (₹)',
            'current_amount': 'Currently Saved (₹)',
            'target_date': 'Target Date'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['goal_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'e.g. Vacation Fund, New Car'
        })

    def clean(self):
        cleaned_data = super().clean()
        target_amount = cleaned_data.get('target_amount')
        current_amount = cleaned_data.get('current_amount')
        target_date = cleaned_data.get('target_date')

        if target_amount and current_amount and current_amount > target_amount:
            self.add_error('current_amount', 
                          "Current amount cannot exceed target amount")

        if target_date and target_date < timezone.now().date():
            self.add_error('target_date', 
                          "Target date cannot be in the past")

        return cleaned_data

    def clean_target_amount(self):
        target_amount = self.cleaned_data.get('target_amount')
        if target_amount <= 0:
            raise ValidationError("Target amount must be greater than zero")
        return target_amount

    def clean_current_amount(self):
        current_amount = self.cleaned_data.get('current_amount')
        if current_amount < 0:
            raise ValidationError("Current amount cannot be negative")
        return current_amount