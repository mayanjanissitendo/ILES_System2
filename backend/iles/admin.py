from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Evaluation, EvaluationCriteria, InternshipPlacement, WeeklyLog, WorkflowStatusHistory


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("ILES profile", {"fields": ("role", "phone_number", "student_number")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = UserAdmin.list_filter + ("role",)


@admin.register(InternshipPlacement)
class InternshipPlacementAdmin(admin.ModelAdmin):
    list_display = ("student", "organization_name", "start_date", "end_date", "is_active")
    list_filter = ("is_active", "start_date")
    search_fields = ("student__username", "organization_name", "position_title")


@admin.register(WeeklyLog)
class WeeklyLogAdmin(admin.ModelAdmin):
    list_display = ("placement", "week_number", "status", "hours_worked", "submitted_at")
    list_filter = ("status", "week_start_date")


@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "max_score", "is_active")
    list_filter = ("category", "is_active")


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("placement", "evaluation_type", "score", "weighted_score", "evaluator", "submitted_at")
    list_filter = ("evaluation_type", "submitted_at")


@admin.register(WorkflowStatusHistory)
class WorkflowStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("weekly_log", "from_status", "to_status", "changed_by", "created_at")
    list_filter = ("from_status", "to_status", "created_at")
