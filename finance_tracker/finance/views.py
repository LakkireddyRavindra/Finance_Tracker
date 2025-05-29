from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from itertools import chain
from operator import attrgetter

from .models import Income, Expense, SavingsGoal
from .forms import ExpenseForm, SavingsGoalForm
from django.db.models import Sum
from decimal import Decimal 


def dashboard(request):
    try:
        income_agg = Income.objects.filter(user=request.user).aggregate(total=Sum('amount'))
        total_income = income_agg['total'] or 0

        expense_agg = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))
        total_expense = expense_agg['total'] or 0

        account_balance = float(total_income) - float(total_expense)

        savings_agg = SavingsGoal.objects.filter(user=request.user).aggregate(
            total_saved=Sum('current_amount'),
            total_goal=Sum('target_amount')
        )

        total_savings = float(savings_agg['total_saved'] or 0)
        total_goal_amount = float(savings_agg['total_goal'] or 0)

        # Calculate percentage
        if total_goal_amount > 0:
            saving_percentage = (total_savings / total_goal_amount) * 100
        else:
            saving_percentage = 0

        # Compute the stroke offset safely
        stroke_offset = 282 - (saving_percentage * 2.82)
        stroke_offset = max(0, min(282, stroke_offset))  # Clamp between 0 and 282 for safety

        return render(request, 'finance/dashboard.html', {
            'account_balance': account_balance,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_savings': total_savings,
            'total_goal_amount': total_goal_amount,
            'saving_percentage': round(saving_percentage, 2),
            'stroke_offset': round(stroke_offset, 2),
            'user': request.user
        })

    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return render(request, 'finance/error.html', {'error': str(e)})



@login_required
def income(request):
    if request.method == 'POST':
        income_id = request.POST.get('income_id')
        if income_id:  # Editing existing income
            income = get_object_or_404(Income, id=income_id, user=request.user)
            form = IncomeForm(request.POST, instance=income)
        else:  # Creating new income
            form = IncomeForm(request.POST)
        
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('income')
    else:
        form = IncomeForm()

    income_records = Income.objects.filter(user=request.user).order_by('-date_received')
    return render(request, 'finance/income.html', {
        'form': form,
        'incomes': income_records,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Income

@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    if request.method == 'POST':
        income.delete()
        return redirect('income')
    # If not POST, still redirect but could show error
    return redirect('income')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import IncomeForm, ExpenseForm, SavingsGoalForm
from .models import Income, Expense, SavingsGoal


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def expenditure(request):
    if request.method == 'POST':
        expense_id = request.POST.get('expense_id')
        if expense_id:  # Editing existing expense
            expense = get_object_or_404(Expense, id=expense_id, user=request.user)
            form = ExpenseForm(request.POST, instance=expense)
        else:  # Creating new expense
            form = ExpenseForm(request.POST)
        
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expenditure')
    else:
        form = ExpenseForm()

    expenses = Expense.objects.filter(user=request.user).order_by('-date_incurred')
    return render(request, 'finance/expenditure.html', {
        'form': form,
        'expenses': expenses,
    })

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.delete()
    return redirect('expenditure')


@login_required
def savings(request):
    if request.method == 'POST':
        goal_id = request.POST.get('goal_id')
        if goal_id:
            goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
            form = SavingsGoalForm(request.POST, instance=goal)
        else:
            form = SavingsGoalForm(request.POST)
        
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('savings')
    else:
        form = SavingsGoalForm()

    goals = SavingsGoal.objects.filter(user=request.user).order_by('target_date', '-created_at')
    
    # Calculate statistics
    total_goals = goals.count()
    unique_goals_count = goals.values('goal_name').distinct().count()
    
    # Calculate amounts
    total_target_amount = goals.aggregate(Sum('target_amount'))['target_amount__sum'] or 0
    total_current_amount = goals.aggregate(Sum('current_amount'))['current_amount__sum'] or 0
    total_remaining_amount = total_target_amount - total_current_amount
    
    # Calculate progress percentage
    total_progress = 0
    if total_target_amount > 0:
        total_progress = (total_current_amount / total_target_amount) * 100

    context = {
        'form': form,
        'goals': goals,
        'page_title': 'Savings',
        'total_goals': total_goals,
        'unique_goals_count': unique_goals_count,
        'total_target_amount': total_target_amount,
        'total_current_amount': total_current_amount,
        'total_remaining_amount': total_remaining_amount,
        'total_progress': round(total_progress, 2),
    }
    return render(request, 'finance/savings.html', context)


@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
    return redirect('savings')

def add_goal(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('savings_goals')
    else:
        form = SavingsGoalForm(user=request.user)
    
    return render(request, 'finance/savings.html', {'form': form})
from django.utils import timezone
import logging
from itertools import chain
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from .models import Income, SavingsGoal, Expense
from datetime import date
from django.utils import timezone

logger = logging.getLogger(__name__)

@login_required
def transactions(request):
    try:
        # Get all user-specific data in one query each
        incomes = Income.objects.filter(user=request.user).select_related('user')
        savings = SavingsGoal.objects.filter(user=request.user).select_related('user')
        expenses = Expense.objects.filter(user=request.user).select_related('user')

        # Prepare objects for sorting with proper fallbacks
        for item in savings:
            item.transaction_type = 'savings'
            item.display_name = item.goal_name
            item.date_for_sort = make_datetime(item.created_at)
            item.display_date = item.created_at
            item.amount = item.current_amount

        for item in incomes:
            item.transaction_type = 'income'
            item.display_name = item.get_income_type_display()
            date_value = item.date_received or item.created_at
            item.date_for_sort = make_datetime(date_value)
            item.display_date = item.date_received
            item.amount = item.amount

        for item in expenses:
            item.transaction_type = 'expense'
            item.display_name = item.description
            date_value = item.date_incurred or item.created_at
            item.date_for_sort = make_datetime(date_value)
            item.display_date = item.date_incurred
            item.amount = item.amount


        # Combine and sort by date descending
        combined = sorted(
            chain(incomes, savings, expenses),
            key=lambda x: x.date_for_sort if x.date_for_sort else timezone.now(),
            reverse=True
        )

        context = {
            'transactions': combined,
            'page_title': 'Transactions',
        }
        return render(request, 'finance/transactions.html', context)

    except Exception as e:
        logger.error(f"Error in transactions view: {str(e)}", exc_info=True)
        messages.error(request, "Could not load transactions. Please try again later.")
        return render(request, 'finance/error.html', {'error': str(e)}, status=500)
    
from datetime import datetime
from django.utils.timezone import make_aware, is_naive

def make_datetime(dt):
    if isinstance(dt, datetime):
        return make_aware(dt) if is_naive(dt) else dt
    elif isinstance(dt, date):
        return make_aware(datetime.combine(dt, datetime.min.time()))
    return timezone.now()  # fallback