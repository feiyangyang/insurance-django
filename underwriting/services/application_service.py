from django.db.models import Q
from django.shortcuts import get_object_or_404

from underwriting.models import InsuranceApplication


def get_application_list():
    return (
        InsuranceApplication.objects.select_related("customer")
        .select_related("risk_assessment")
        .all()
        .order_by("-id")
    )


def get_application_by_id(application_id):
    return get_object_or_404(
        InsuranceApplication.objects.select_related("customer"),
        id=application_id,
    )


def delete_application(application_id):
    application = get_application_by_id(application_id)
    application.delete()
    return True


def search_applications(keyword):
    queryset = get_application_list()

    if keyword:
        queryset = queryset.filter(
            Q(application_no__icontains=keyword)
            | Q(customer__name__icontains=keyword)
            | Q(customer__company_name__icontains=keyword)
            | Q(subject_name__icontains=keyword)
            | Q(subject_address__icontains=keyword)
        )

    return queryset
