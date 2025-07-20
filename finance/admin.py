from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Income, Expense, SavingsGoal

User = get_user_model()

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'income_type', 'amount', 'date_received')
    list_filter = ('income_type', 'date_received')
    search_fields = ('description', 'income_type')
    raw_id_fields = ('user',)  # Better for performance with many users

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'expense_type', 'amount', 'date_incurred', 'source')
    list_filter = ('expense_type', 'source', 'date_incurred')
    search_fields = ('description', 'expense_type')
    raw_id_fields = ('user',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_name', 'current_amount', 'target_amount', 'target_date', 'progress_display')
    list_filter = ('target_date',)
    search_fields = ('goal_name', 'description')
    raw_id_fields = ('user',)
    
    @admin.display(description='Progress')
    def progress_display(self, obj):
        return f"{obj.progress_percentage:.1f}%"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)