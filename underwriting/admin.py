from django.contrib import admin

# Register your models here.
from .models import (
    AuditLog,
    Company,
    Customer,
    Department,
    FormFieldConfiguration,
    FormTemplate,
    OperationLog,
    PermissionPoint,
    InsuranceApplication,
    Policy,
    RiskAssessment,
    SystemRole,
    UnderwritingTask,
    UserProfile,
)

admin.site.site_header = "保险人工核保系统后台"
admin.site.site_title = "保险核保后台"
admin.site.index_title = "系统后台"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "customer_no",
        "name",
        "customer_type",
        "company_name",
        "phone",
        "contact_person",
        "contact_phone",
    )
    list_filter = ("customer_type",)
    search_fields = (
        "customer_no",
        "name",
        "phone",
        "id_number",
        "company_name",
        "unified_social_credit_code",
        "contact_person",
        "contact_phone",
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code", "remark")
    list_filter = ("is_active",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "code", "is_active")
    search_fields = ("name", "code", "company__name", "remark")
    list_filter = ("company", "is_active")


@admin.register(PermissionPoint)
class PermissionPointAdmin(admin.ModelAdmin):
    list_display = ("module", "name", "code", "sort_order")
    search_fields = ("module", "name", "code")
    list_filter = ("module",)


@admin.register(SystemRole)
class SystemRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code", "remark")
    list_filter = ("is_active",)
    filter_horizontal = ("permissions",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "department")
    search_fields = ("user__username", "user__first_name", "company__name", "department__name", "remark")
    filter_horizontal = ("roles",)


class FormFieldConfigurationInline(admin.TabularInline):
    model = FormFieldConfiguration
    extra = 1
    fields = (
        "sort_order",
        "field_label",
        "field_key",
        "control_type",
        "customer_type",
        "is_required",
        "default_value",
        "option_values",
        "is_enabled",
    )


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "form_type",
        "customer_type",
        "is_active",
        "updated_at",
    )
    list_filter = ("form_type", "customer_type", "is_active")
    search_fields = ("name", "code", "description", "fields__field_label")
    inlines = [FormFieldConfigurationInline]


@admin.register(FormFieldConfiguration)
class FormFieldConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "template",
        "sort_order",
        "field_label",
        "control_type",
        "customer_type",
        "is_required",
        "is_enabled",
    )
    list_filter = ("template", "control_type", "customer_type", "is_required", "is_enabled")
    search_fields = ("template__name", "field_key", "field_label", "help_text")



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


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "username", "module", "action", "target_type", "target_id", "result")
    list_filter = ("module", "action", "result")
    search_fields = ("username", "description", "target_type", "target_id")
