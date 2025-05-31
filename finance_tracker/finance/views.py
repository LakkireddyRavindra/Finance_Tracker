from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import date, datetime
from itertools import chain
from .models import Income, Expense, SavingsGoal
from .forms import IncomeForm, ExpenseForm, SavingsGoalForm
import logging
from django.contrib.auth.models import User
from django.conf import settings

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    try:
        # Calculate totals
        total_income = Income.objects.filter(user=request.user).aggregate(
            Sum('amount'))['amount__sum'] or 0
        total_expense = Expense.objects.filter(user=request.user).aggregate(
            Sum('amount'))['amount__sum'] or 0
        total_savings = SavingsGoal.objects.filter(user=request.user).aggregate(
            Sum('current_amount'))['current_amount__sum'] or 0
        
        # Recent transactions (last 5)
        recent_incomes = Income.objects.filter(user=request.user).order_by('-date_received')[:5]
        recent_expenses = Expense.objects.filter(user=request.user).order_by('-date_incurred')[:5]
        
        # Savings goals progress
        savings_goals = SavingsGoal.objects.filter(user=request.user).order_by('target_date')[:3]
        
        context = {
            'total_income': total_income,
            'total_expense': total_expense,
            'total_savings': total_savings,
            'net_balance': total_income - total_expense - total_savings,
            'recent_incomes': recent_incomes,
            'recent_expenses': recent_expenses,
            'savings_goals': savings_goals,
        }
        return render(request, 'finance/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        messages.error(request, "Could not load dashboard data")
        return render(request, 'finance/dashboard.html')

# views.py
@login_required
def income(request, id=None):
    if id:  # Edit existing income
        income = get_object_or_404(Income, id=id, user=request.user)
    else:  # New income
        income = None
    
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, "Income saved successfully")
            return redirect('finance:income')
    else:
        form = IncomeForm(instance=income)
    
    # Get all incomes for listing
    incomes = Income.objects.filter(user=request.user).order_by('-date_received')
    total = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'finance/income.html', {
        'form': form,
        'incomes': incomes,
        'total_income': total,
        'editing': id is not None,
        'edit_id': id
    })

@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, "Income deleted successfully")
    return redirect('finance:income')


# For Expenses
@login_required
def expense(request, id=None):
    if id:
        expense = get_object_or_404(Expense, id=id, user=request.user)
    else:
        expense = None
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense saved successfully")
            return redirect('finance:expense')
    else:
        form = ExpenseForm(instance=expense)
    
    expenses = Expense.objects.filter(user=request.user).order_by('-date_incurred')
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'finance/expense.html', {
        'form': form,
        'expenses': expenses,
        'total_expense': total,
        'editing': id is not None,
        'edit_id': id
    })

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully")
    return redirect('finance:expense')

# For Savings
@login_required
def savings(request, id=None):
    if id:
        savings = get_object_or_404(SavingsGoal, id=id, user=request.user)
    else:
        savings = None
    
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=savings)
        if form.is_valid():
            savings = form.save(commit=False)
            savings.user = request.user
            savings.save()
            messages.success(request, "Savings goal saved successfully")
            return redirect('finance:savings')
    else:
        form = SavingsGoalForm(instance=savings)
    
    goals = SavingsGoal.objects.filter(user=request.user).order_by('target_date')
    total_target = goals.aggregate(Sum('target_amount'))['target_amount__sum'] or 0
    total_saved = goals.aggregate(Sum('current_amount'))['current_amount__sum'] or 0
    
    return render(request, 'finance/savings.html', {
        'form': form,
        'goals': goals,
        'total_target': total_target,
        'total_saved': total_saved,
        'remaining_amount': total_target - total_saved,
        'editing': id is not None,
        'edit_id': id  # Make sure this is passed to template
    })

@login_required
def delete_savings(request, id):
    savings = get_object_or_404(SavingsGoal, id=id, user=request.user)
    if request.method == 'POST':
        savings.delete()
        messages.success(request, "Savings goal deleted successfully")
    return redirect('finance:savings')

# views.py
from django.utils import timezone
from datetime import datetime
import logging
from django.contrib.auth.decorators import login_required

@login_required
def transactions(request):
    try:
        # Get all user-specific data
        incomes = Income.objects.filter(user=request.user).select_related('user')
        savings = SavingsGoal.objects.filter(user=request.user).select_related('user')
        expenses = Expense.objects.filter(user=request.user).select_related('user')

        # Prepare transaction data with consistent timezone handling
        transactions_list = []
        
        def normalize_datetime(dt):
            """Convert date or datetime to timezone-aware datetime"""
            if dt is None:
                return timezone.now()
            if isinstance(dt, date) and not isinstance(dt, datetime):
                # Convert date to datetime at midnight
                dt = datetime.combine(dt, datetime.min.time())
            if not timezone.is_aware(dt):
                dt = timezone.make_aware(dt)
            return dt

        for income in incomes:
            transactions_list.append({
                'type': 'income',
                'amount': income.amount,
                'description': income.get_income_type_display(),
                'category': 'Income',
                'date': normalize_datetime(income.date_received or income.created_at),
                'display_date': income.date_received or income.created_at,
            })
            
        for saving in savings:
            transactions_list.append({
                'type': 'savings',
                'amount': saving.current_amount,
                'description': saving.goal_name,
                'category': 'Savings',
                'date': normalize_datetime(saving.created_at),
                'display_date': saving.created_at,
            })
            
        for expense in expenses:
            transactions_list.append({
                'type': 'expense',
                'amount': -expense.amount,
                'description': expense.description,
                'category': getattr(expense, 'expense_type', 'Uncategorized'),
                'date': normalize_datetime(expense.date_incurred or expense.created_at),
                'display_date': expense.date_incurred or expense.created_at,
            })

        # Sort transactions by date (newest first)
        transactions_list.sort(key=lambda x: x['date'], reverse=True)
        
        # Calculate totals
        income_total = sum(t['amount'] for t in transactions_list if t['type'] == 'income')
        expense_total = abs(sum(t['amount'] for t in transactions_list if t['type'] == 'expense'))
        savings_total = sum(t['amount'] for t in transactions_list if t['type'] == 'savings')
        net_balance = income_total - expense_total - savings_total

        context = {
            'transactions': transactions_list,
            'income_total': income_total,
            'expense_total': expense_total,
            'savings_total': savings_total,
            'net_balance': net_balance,
            'page_title': 'Transactions',
        }
        return render(request, 'finance/transactions.html', context)

    except Exception as e:
        logger.error(f"Error in transactions view: {str(e)}", exc_info=True)
        return render(request, 'finance/error.html', {
            'error_message': "Could not load transactions. Please try again later.",
            'error_details': str(e)
        }, status=500)
    
