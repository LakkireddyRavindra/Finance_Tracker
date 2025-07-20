# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import date, datetime, timedelta
import json
import csv
import logging
from django.core.serializers.json import DjangoJSONEncoder

from .models import Income, Expense, SavingsGoal
from .forms import IncomeForm, ExpenseForm, AddOrUpdateSavingsForm

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    try:
        total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
        total_savings = SavingsGoal.objects.filter(user=request.user).aggregate(Sum('current_amount'))['current_amount__sum'] or 0

        recent_incomes = Income.objects.filter(user=request.user).order_by('-date_received')[:5]
        recent_expenses = Expense.objects.filter(user=request.user).order_by('-date_incurred')[:5]
        savings_goals = SavingsGoal.objects.filter(user=request.user).order_by('target_date')[:3]

        income_qs = Income.objects.filter(user=request.user).annotate(
            month=TruncMonth('date_received')
        ).values('month').annotate(total=Sum('amount')).order_by('month')

        expense_qs = Expense.objects.filter(user=request.user).annotate(
            month=TruncMonth('date_incurred')
        ).values('month').annotate(total=Sum('amount')).order_by('month')

        income_months = [entry['month'].strftime('%b %Y') for entry in income_qs]
        income_totals = [float(entry['total'] or 0) for entry in income_qs]
        expense_months = [entry['month'].strftime('%b %Y') for entry in expense_qs]
        expense_totals = [float(entry['total'] or 0) for entry in expense_qs]

        context = {
            'total_income': total_income,
            'total_expense': total_expense,
            'total_savings': total_savings,
            'net_balance': total_income - total_expense - total_savings,
            'recent_incomes': recent_incomes,
            'recent_expenses': recent_expenses,
            'savings_goals': savings_goals,
            'income_months': json.dumps(income_months),
            'income_totals': json.dumps(income_totals),
            'expense_months': json.dumps(expense_months),
            'expense_totals': json.dumps(expense_totals),
        }
        return render(request, 'finance/dashboard.html', context)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        messages.error(request, "Could not load dashboard data.")
        return render(request, 'finance/dashboard.html')


@login_required
def income(request, id=None):
    income_instance = get_object_or_404(Income, id=id, user=request.user) if id else None

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income_instance)
        if form.is_valid():
            new_income = form.save(commit=False)
            new_income.user = request.user
            new_income.save()
            messages.success(request, "Income saved successfully")
            return redirect('finance:income')
    else:
        form = IncomeForm(instance=income_instance)

    incomes = Income.objects.filter(user=request.user).order_by('-date_received')
    total = incomes.aggregate(total=Sum('amount'))['total'] or 0

    income_types_data = [label for code, label in Income.INCOME_TYPE_CHOICES]
    type_codes = [code for code, _ in Income.INCOME_TYPE_CHOICES]

    now = datetime.now()
    income_totals_by_period = {}
    for months in [1, 3, 6, 12]:
        since = now - timedelta(days=30*months)
        filtered = incomes.filter(date_received__gte=since)
        totals = [0] * len(income_types_data)
        grouped = filtered.values('income_type').annotate(total=Sum('amount'))
        for item in grouped:
            try:
                index = type_codes.index(item['income_type'])
                totals[index] = float(item['total'])
            except ValueError:
                continue
        income_totals_by_period[f"income_totals_{months}m_json"] = json.dumps(totals)

    return render(request, 'finance/income.html', {
        'form': form,
        'incomes': incomes,
        'total_income': total,
        'editing': id is not None,
        'edit_id': id,
        'income_types_json': json.dumps(income_types_data),
        **income_totals_by_period,
    })


@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, "Income deleted successfully")
    return redirect('finance:income')


@login_required
def expense(request, edit_id=None):
    edit_expense = get_object_or_404(Expense, id=edit_id, user=request.user) if edit_id else None
    editing = bool(edit_expense)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=edit_expense)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('finance:expense')
    else:
        form = ExpenseForm(instance=edit_expense)

    expenses = Expense.objects.filter(user=request.user).order_by('-date_incurred')
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

    expense_types = list(Expense.objects.filter(user=request.user).values_list('expense_type', flat=True).distinct())
    expense_type_display = [dict(Expense.EXPENSE_TYPE_CHOICES).get(t, str(t)) for t in expense_types]

    def get_totals_by_type(months):
        since = timezone.now() - timedelta(days=30*months)
        qs = expenses.filter(date_incurred__gte=since)
        return [float(qs.filter(expense_type=t).aggregate(sum=Sum('amount'))['sum'] or 0) for t in expense_types]

    context = {
        'expenses': expenses,
        'total_expense': total_expense,
        'form': form,
        'editing': editing,
        'edit_id': edit_id,
        'expense_types_json': json.dumps(expense_type_display),
        'expense_totals_1m_json': json.dumps(get_totals_by_type(1)),
        'expense_totals_3m_json': json.dumps(get_totals_by_type(3)),
        'expense_totals_6m_json': json.dumps(get_totals_by_type(6)),
        'expense_totals_12m_json': json.dumps(get_totals_by_type(12)),
    }
    return render(request, 'finance/expense.html', context)


@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully")
    return redirect('finance:expense')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import SavingsGoal
from .forms import AddOrUpdateSavingsForm

@login_required
def savings(request, edit_id=None):
    user = request.user
    editing = edit_id is not None
    goal_to_edit = get_object_or_404(SavingsGoal, id=edit_id, user=user) if editing else None

    goals = SavingsGoal.objects.filter(user=user)
    incomplete_goals = goals.annotate(remaining=F('target_amount') - F('current_amount')).filter(remaining__gt=0)

    if request.method == 'POST':
        form = AddOrUpdateSavingsForm(request.POST, user=user)
        if form.is_valid():
            if editing and goal_to_edit:
                goal_to_edit.goal_name = form.cleaned_data['goal_name']
                goal_to_edit.target_amount = form.cleaned_data['target_amount']
                goal_to_edit.target_date = form.cleaned_data['target_date']
                amount_to_add = form.cleaned_data['amount_to_add']

                if amount_to_add >= form.cleaned_data['target_amount']:
                    goal_to_edit.current_amount = form.cleaned_data['target_amount']
                    messages.success(request, "Goal reached! Amount capped to target.")
                else:
                    goal_to_edit.current_amount = amount_to_add
                    messages.success(request, "Savings goal updated successfully.")

                goal_to_edit.save()

            else:
                existing_goal = form.cleaned_data.get('existing_goal')
                amount_to_add = form.cleaned_data['amount_to_add']

                if existing_goal:
                    needed = existing_goal.target_amount - existing_goal.current_amount
                    if amount_to_add >= needed:
                        existing_goal.current_amount += needed
                        existing_goal.save()
                        messages.success(request, f"Only ₹{needed} was needed; goal completed!")
                    else:
                        existing_goal.current_amount += amount_to_add
                        existing_goal.save()
                        messages.success(request, "Amount added to existing goal.")
                else:
                    # create new goal, replace old if exists (your requirement)
                    SavingsGoal.objects.filter(user=user, goal_name=form.cleaned_data['goal_name']).delete()
                    add_amount = min(amount_to_add, form.cleaned_data['target_amount'])
                    new_goal = SavingsGoal(
                        user=user,
                        goal_name=form.cleaned_data['goal_name'],
                        target_amount=form.cleaned_data['target_amount'],
                        target_date=form.cleaned_data['target_date'],
                        current_amount=add_amount
                    )
                    new_goal.save()
                    if amount_to_add > form.cleaned_data['target_amount']:
                        messages.success(request, f"New goal created. Only ₹{form.cleaned_data['target_amount']} needed; extra ignored.")
                    else:
                        messages.success(request, "New savings goal created successfully.")
            return redirect('finance:savings')
    else:
        initial = {}
        if editing and goal_to_edit:
            initial = {
                'goal_name': goal_to_edit.goal_name,
                'target_amount': goal_to_edit.target_amount,
                'target_date': goal_to_edit.target_date,
                'amount_to_add': goal_to_edit.current_amount,
            }
        form = AddOrUpdateSavingsForm(user=user, initial=initial)

    total_target = goals.aggregate(total=Sum('target_amount'))['total'] or 0
    total_saved = goals.aggregate(total=Sum('current_amount'))['total'] or 0
    remaining_amount = max(total_target - total_saved, 0)

    def totals(months=None):
        qs = goals
        if months:
            qs = qs.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30*months))
        return list(qs.values_list('current_amount', flat=True))

    context = {
        'form': form,
        'editing': editing,
        'goal_to_edit': goal_to_edit,
        'goals': goals,
        'incomplete_goals': incomplete_goals,
        'total_target': total_target,
        'total_saved': total_saved,
        'remaining_amount': remaining_amount,
        'savings_totals_all_json': json.dumps(totals(None), cls=DjangoJSONEncoder),
        'savings_totals_1m_json': json.dumps(totals(1), cls=DjangoJSONEncoder),
        'savings_totals_3m_json': json.dumps(totals(3), cls=DjangoJSONEncoder),
        'savings_totals_6m_json': json.dumps(totals(6), cls=DjangoJSONEncoder),
        'savings_totals_12m_json': json.dumps(totals(12), cls=DjangoJSONEncoder),
        'goal_names_json': json.dumps(list(goals.values_list('goal_name', flat=True)), cls=DjangoJSONEncoder),
    }
    return render(request, 'finance/savings.html', context)

@login_required
def delete_savings(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    goal.delete()
    messages.success(request, "Savings goal deleted.")
    return redirect('finance:savings')


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
    

@login_required
def download_expenses(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Amount', 'Date', 'Source', 'Description'])
    expenses = Expense.objects.filter(user=request.user)
    for exp in expenses:
        writer.writerow([
            exp.get_expense_type_display(),
            float(exp.amount),
            exp.date_incurred.strftime('%Y-%m-%d'),
            exp.get_source_display(),
            exp.description or ''
        ])
    return response


@login_required
def download_income(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="income.csv"'
    writer = csv.writer(response)
    writer.writerow(['Type', 'Amount', 'Date', 'Description'])
    incomes = Income.objects.filter(user=request.user).order_by('-date_received')
    for i in incomes:
        writer.writerow([i.get_income_type_display(), i.amount, i.date_received, i.description])
    return response


@login_required
def download_savings(request):
    from django.http import HttpResponse
    import csv

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="savings.csv"'

    writer = csv.writer(response)
    writer.writerow(['Goal Name', 'Target Amount', 'Saved Amount', 'Start Date', 'Target Date'])

    savings = SavingsGoal.objects.filter(user=request.user)
    for saving in savings:
        writer.writerow([
            saving.goal_name,
            float(saving.target_amount),
            float(saving.current_amount),
            saving.created_at.strftime('%Y-%m-%d'),
            saving.target_date.strftime('%Y-%m-%d')
        ])

    return response

from django.contrib.auth.decorators import login_required

@login_required
def download_transactions(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Type', 'Amount', 'Description', 'Category', 'Date'])

    incomes = Income.objects.filter(user=request.user)
    savings = SavingsGoal.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    transactions_list = []

    def normalize_datetime(dt):
        if dt is None:
            return timezone.now()
        if isinstance(dt, date) and not isinstance(dt, datetime):
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
            'date': normalize_datetime(income.date_received or income.created_at)
        })

    for saving in savings:
        transactions_list.append({
            'type': 'savings',
            'amount': saving.current_amount,
            'description': saving.goal_name,
            'category': 'Savings',
            'date': normalize_datetime(saving.created_at)
        })

    for expense in expenses:
        transactions_list.append({
            'type': 'expense',
            'amount': -expense.amount,
            'description': expense.description,
            'category': expense.expense_type or 'Uncategorized',
            'date': normalize_datetime(expense.date_incurred or expense.created_at)
        })

    # Sort by date descending
    transactions_list.sort(key=lambda x: x['date'], reverse=True)

    for tx in transactions_list:
        writer.writerow([
            tx['type'],
            float(tx['amount']),
            tx['description'],
            tx['category'],
            tx['date'].strftime('%Y-%m-%d')
        ])

    return response
# Ensure the download_* views are protected by login_required