from django.contrib import admin

# Register your models here.
from .models import (
    AuditLog,
    Customer,
    InsuranceApplication,
    Policy,
    RiskAssessment,
    UnderwritingTask,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "customer_type",
        "company_name",
        "phone",
        "contact_person",
        "contact_phone",
    )
    list_filter = ("customer_type",)
    search_fields = (
        "name",
        "phone",
        "id_number",
        "company_name",
        "unified_social_credit_code",
        "contact_person",
        "contact_phone",
    )



@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        "policy_no",
        "application",
        "customer",
        "product_name",
        "insured_amount",
        "premium",
        "status",
        "created_at",
    )
    list_filter = ("status", "product_type")
    search_fields = (
        "policy_no",
        "proposal_no",
        "application__application_no",
        "customer__name",
        "customer__company_name",
        "product_name",
    )


@admin.register(InsuranceApplication)
class InsuranceApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "application_no",
        "customer",
        "insurance_type",
        "subject_name",
        "insured_amount",
        "estimated_premium",
        "status",
        "created_at",
    )
    list_filter = ("insurance_type", "status")
    search_fields = (
        "application_no",
        "customer__name",
        "customer__company_name",
        "subject_name",
        "subject_address",
    )



@admin.register(UnderwritingTask)
class UnderwritingTaskAdmin(admin.ModelAdmin):
    list_display = (
        "task_no",
        "application",
        "policy",
        "risk_level",
        "status",
        "assigned_to",
        "created_at",
    )
    list_filter = ("risk_level", "status")
    search_fields = (
        "task_no",
        "application__application_no",
        "application__customer__name",
        "application__customer__company_name",
        "policy__policy_no",
        "assigned_to",
    )


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "risk_level",
        "risk_score",
        "updated_at",
    )
    list_filter = ("risk_level",)
    search_fields = (
        "application__application_no",
        "application__customer__name",
        "application__customer__company_name",
        "risk_factors",
        "conclusion",
    )



@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "action",
        "operator",
        "from_status",
        "to_status",
        "decision",
        "created_at",
    )
    list_filter = ("action", "to_status")
    search_fields = ("task__task_no", "operator", "decision", "comment")
