from django.db.models import Q
from django.shortcuts import get_object_or_404
from underwriting.models import Policy
from underwriting.services.audit_service import create_audit_log


def search_policies(keyword):
    queryset = Policy.objects.select_related("customer", "application").all().order_by("-id")

    if keyword:
        queryset = queryset.filter(
            Q(policy_no__icontains=keyword)
            | Q(proposal_no__icontains=keyword)
            | Q(product_name__icontains=keyword)
            | Q(customer__name__icontains=keyword)
            | Q(applicant_name__icontains=keyword)
            | Q(insured_name__icontains=keyword)
        )

    return queryset


def get_policy_by_id(policy_id):
    return get_object_or_404(Policy, id=policy_id)


def delete_policy(policy_id):
    policy = get_policy_by_id(policy_id)
    policy.delete()


def can_generate_policy(task):
    return bool(
        task.status == "approved"
        and task.application
        and not hasattr(task.application, "policy")
    )


def generate_policy_from_task(task, operator=""):
    if not can_generate_policy(task):
        return None

    application = task.application
    policy = Policy.objects.create(
        customer=application.customer,
        application=application,
        policy_no=f"POL-{application.application_no}",
        proposal_no=application.application_no,
        product_name=application.get_insurance_type_display(),
        product_type=application.insurance_type,
        applicant_name=str(application.customer),
        insured_name=application.subject_name,
        premium=application.estimated_premium,
        insured_amount=application.insured_amount,
        status="approved",
        remark=application.remark,
    )

    task.policy = policy
    task.save(update_fields=["policy", "updated_at"])

    create_audit_log(
        task=task,
        action="create_policy",
        operator=operator or task.assigned_to,
        from_status=task.status,
        to_status=task.status,
        decision="生成保单",
        comment=f"已生成保单 {policy.policy_no}",
    )

    return policy
