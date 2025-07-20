from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Income, Expense, SavingsGoal

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
            'goal_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Vacation Fund, New Car'
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
            'target_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date()
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
        }
        labels = {
            'goal_name': 'Goal Name',
            'target_amount': 'Target Amount (₹)',
            'current_amount': 'Currently Saved (₹)',
            'target_date': 'Target Date'
        }

    def clean_target_amount(self):
        amount = self.cleaned_data.get('target_amount')
        if amount is not None and amount <= 0:
            raise ValidationError("Target amount must be greater than zero")
        return amount

    def clean_current_amount(self):
        amount = self.cleaned_data.get('current_amount')
        if amount is not None and amount < 0:
            raise ValidationError("Current amount cannot be negative")
        return amount

class AddOrUpdateSavingsForm(forms.ModelForm): # NOTE: Changed to ModelForm
    """
    Handles creating, updating, and adding funds to savings goals.
    This form now correctly handles editing by inheriting from ModelForm.
    """
    # This is a custom field for selecting an existing goal to add funds to.
    # It's not part of the model fields, so we define it separately.
    existing_goal = forms.ModelChoiceField(
        queryset=SavingsGoal.objects.none(), # Populated in __init__
        required=False,
        empty_label="➕ Create new goal",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # This is also a custom field for logic. It will be used to set the
    # 'current_amount' on the model instance within the view.
    amount_to_add = forms.DecimalField(
        label="Amount to Save / Add",
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Amount to add now'
        })
    )

    class Meta:
        model = SavingsGoal
        # These are the fields from the model that this form can create or edit.
        fields = ['goal_name', 'target_amount', 'target_date']
        widgets = {
            'goal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Vacation Fund'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Target amount'}),
            'target_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Pop the custom 'user' kwarg before calling the parent's __init__
        user = kwargs.pop('user', None)
        
        # The parent ModelForm's __init__ will correctly handle the 'instance' kwarg
        super().__init__(*args, **kwargs)
        
        # Populate the queryset for the 'existing_goal' dropdown
        if user:
            self.fields['existing_goal'].queryset = SavingsGoal.objects.filter(user=user)

        # Make model fields not required by default.
        # Validation is now contextual in the clean() method.
        self.fields['goal_name'].required = False
        self.fields['target_amount'].required = False
        self.fields['target_date'].required = False

        # Set the min date for the target_date widget dynamically
        self.fields['target_date'].widget.attrs['min'] = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()
        existing_goal = cleaned_data.get('existing_goal')
        
        # We are creating a new goal if "Create new goal" is selected AND
        # we are not editing an existing instance (self.instance.pk is None for new objects).
        is_creating_new = not existing_goal and not self.instance.pk

        if is_creating_new:
            if not cleaned_data.get('goal_name'):
                self.add_error('goal_name', "A name is required for a new goal.")
            if cleaned_data.get('target_amount') is None:
                self.add_error('target_amount', "A target amount is required for a new goal.")
            if cleaned_data.get('target_date') is None:
                self.add_error('target_date', "A target date is required for a new goal.")
        
        # General validation for fields that might be present
        target_date = cleaned_data.get('target_date')
        if target_date and target_date < timezone.now().date():
            self.add_error('target_date', "Target date cannot be in the past.")

        target_amount = cleaned_data.get('target_amount')
        if target_amount is not None and target_amount <= 0:
            self.add_error('target_amount', "Target amount must be a positive number.")

        return cleaned_data

    def clean_amount_to_add(self):
        # This validation remains the same
        amount = self.cleaned_data.get('amount_to_add')
        if amount is not None and amount <= 0:
            raise ValidationError("Amount to add must be a positive number.")
        return amount
