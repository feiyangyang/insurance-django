from django.shortcuts import get_object_or_404
from django.db.models import Q

from underwriting.models import Customer


def get_customer_list():
    return Customer.objects.all().order_by("-id")


def get_customer_by_id(customer_id):
    return get_object_or_404(Customer, id=customer_id)


def delete_customer(customer_id):
    customer = get_customer_by_id(customer_id)
    customer.delete()
    return True


def search_customers(keyword):
    queryset = Customer.objects.all().order_by("-id")

    if keyword:
        queryset = queryset.filter(
            Q(name__icontains=keyword)
            | Q(customer_no__icontains=keyword)
            | Q(phone__icontains=keyword)
            | Q(id_number__icontains=keyword)
            | Q(company_name__icontains=keyword)
            | Q(unified_social_credit_code__icontains=keyword)
            | Q(contact_person__icontains=keyword)
            | Q(contact_phone__icontains=keyword)
        )

    return queryset
