from django.shortcuts import render, redirect
from .forms import CustomerForm
from .models import Customer, Policy, UnderwritingTask
from .services.customer_service import (
    get_customer_list,
    get_customer_by_id,
    delete_customer,
    search_customers,
)

from .forms import PolicyForm
from .services.policy_service import (
    search_policies,
    get_policy_by_id,
    delete_policy,
)
from .services.system_check_service import get_database_check_status


def dashboard(request):
    customer_count = Customer.objects.count()
    policy_count = Policy.objects.count()
    pending_count = UnderwritingTask.objects.filter(status="pending").count()
    finished_count = UnderwritingTask.objects.exclude(
        status__in=["pending", "reviewing"]
    ).count()

    tasks = UnderwritingTask.objects.select_related(
        "policy",
        "policy__customer"
    ).order_by("-created_at")[:10]

    return render(request, "dashboard.html", {
        "customer_count": customer_count,
        "policy_count": policy_count,
        "pending_count": pending_count,
        "finished_count": finished_count,
        "tasks": tasks,
    })


def customer_list(request):
    keyword = request.GET.get("keyword", "")
    customers = search_customers(keyword)

    return render(request, "customer_list.html", {
        "customers": customers,
        "keyword": keyword,
    })


def customer_add(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()

    return render(request, "customer_form.html", {
        "title": "新增客户",
        "form": form,
    })


def customer_edit(request, customer_id):
    customer = get_customer_by_id(customer_id)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)

    return render(request, "customer_form.html", {
        "title": "编辑客户",
        "form": form,
    })


def customer_delete(request, customer_id):
    delete_customer(customer_id)
    return redirect("customer_list")

def policy_list(request):
    keyword = request.GET.get("keyword", "")
    policies = search_policies(keyword)

    return render(request, "policy_list.html", {
        "policies": policies,
        "keyword": keyword,
    })


def policy_add(request):
    form = PolicyForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("policy_list")

    return render(request, "policy_form.html", {
        "title": "新增保单",
        "form": form,
    })


def policy_edit(request, policy_id):
    policy = get_policy_by_id(policy_id)
    form = PolicyForm(request.POST or None, instance=policy)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("policy_list")

    return render(request, "policy_form.html", {
        "title": "编辑保单",
        "form": form,
    })


def policy_delete(request, policy_id):
    delete_policy(policy_id)
    return redirect("policy_list")


def system_db_check(request):
    return render(request, "system_db_check.html", get_database_check_status())
