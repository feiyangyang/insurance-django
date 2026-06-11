from django.db.models import Q
from django.shortcuts import get_object_or_404
from underwriting.models import Policy


def search_policies(keyword):
    queryset = Policy.objects.select_related("customer").all().order_by("-id")

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