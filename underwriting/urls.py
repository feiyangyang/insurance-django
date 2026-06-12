from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("customer/", views.customer_list, name="customer_list"),
    path("customer/add/", views.customer_add, name="customer_add"),
    path("customer/<int:customer_id>/edit/", views.customer_edit, name="customer_edit"),
    path("customer/<int:customer_id>/delete/", views.customer_delete, name="customer_delete"),

    path("application/", views.application_list, name="application_list"),
    path("application/add/", views.application_add, name="application_add"),
    path("application/<int:application_id>/edit/", views.application_edit, name="application_edit"),
    path("application/<int:application_id>/delete/", views.application_delete, name="application_delete"),
    path("risk-assessment/", views.risk_assessment_list, name="risk_assessment_list"),
    path(
        "application/<int:application_id>/risk/",
        views.risk_assessment_edit,
        name="risk_assessment_edit",
    ),
    path("underwriting/", views.underwriting_task_list, name="underwriting_task_list"),
    path("underwriting/add/", views.underwriting_task_add, name="underwriting_task_add"),
    path("underwriting/<int:task_id>/", views.underwriting_task_detail, name="underwriting_task_detail"),
    path("underwriting/<int:task_id>/edit/", views.underwriting_task_edit, name="underwriting_task_edit"),
    path("underwriting/<int:task_id>/delete/", views.underwriting_task_delete, name="underwriting_task_delete"),
    path("underwriting/<int:task_id>/generate-policy/", views.generate_policy, name="generate_policy"),
    path("audit-log/", views.audit_log_list, name="audit_log_list"),

    path("policy/", views.policy_list, name="policy_list"),
    path("policy/add/", views.policy_add, name="policy_add"),
    path("policy/<int:policy_id>/edit/", views.policy_edit, name="policy_edit"),
    path("policy/<int:policy_id>/delete/", views.policy_delete, name="policy_delete"),

    path("system/db-check/", views.system_db_check, name="system_db_check"),
]
