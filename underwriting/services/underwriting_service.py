from django.db.models import Q
from django.shortcuts import get_object_or_404

from underwriting.models import InsuranceApplication, UnderwritingTask
from underwriting.services.audit_service import create_audit_log


def get_underwriting_task_list():
    return (
        UnderwritingTask.objects.select_related(
            "application",
            "application__customer",
            "application__risk_assessment",
            "policy",
            "policy__customer",
        )
        .all()
        .order_by("-id")
    )


def search_underwriting_tasks(keyword):
    queryset = get_underwriting_task_list()

    if keyword:
        queryset = queryset.filter(
            Q(task_no__icontains=keyword)
            | Q(application__application_no__icontains=keyword)
            | Q(application__customer__name__icontains=keyword)
            | Q(application__customer__company_name__icontains=keyword)
            | Q(policy__policy_no__icontains=keyword)
            | Q(policy__customer__name__icontains=keyword)
            | Q(assigned_to__icontains=keyword)
        )

    return queryset


def get_underwriting_task_by_id(task_id):
    return get_object_or_404(get_underwriting_task_list(), id=task_id)


def delete_underwriting_task(task_id):
    task = get_underwriting_task_by_id(task_id)
    task.delete()
    return True


def build_task_initial_from_application(application_id):
    if not application_id:
        return {}

    application = get_object_or_404(InsuranceApplication, id=application_id)
    initial = {
        "application": application,
        "task_no": f"UW-{application.application_no}",
        "status": "pending",
    }

    try:
        initial["risk_level"] = application.risk_assessment.risk_level
    except InsuranceApplication.risk_assessment.RelatedObjectDoesNotExist:
        initial["risk_level"] = "medium"

    return initial


def save_underwriting_task(form):
    task = form.save()

    if task.application and task.application.status in ["submitted", "need_material"]:
        task.application.status = "underwriting"
        task.application.save(update_fields=["status", "updated_at"])

    return task


def submit_underwriting_decision(task, form, operator=""):
    from_status = task.status
    task.status = form.cleaned_data["status"]
    task.risk_level = form.cleaned_data["risk_level"]
    task.remark = form.cleaned_data["remark"]
    task.save(update_fields=["status", "risk_level", "remark", "updated_at"])

    if task.application:
        if task.status == "approved":
            task.application.status = "approved"
        elif task.status == "rejected":
            task.application.status = "rejected"
        elif task.status == "need_material":
            task.application.status = "need_material"
        else:
            task.application.status = "underwriting"

        task.application.save(update_fields=["status", "updated_at"])

    create_audit_log(
        task=task,
        action="decision",
        operator=operator or task.assigned_to,
        from_status=from_status,
        to_status=task.status,
        decision=task.get_status_display(),
        comment=task.remark,
    )

    return task
