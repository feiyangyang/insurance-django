from django.shortcuts import render
from .models import Customer, Policy, UnderwritingTask


def dashboard(request):
    customer_count = Customer.objects.count()
    policy_count = Policy.objects.count()
    pending_count = UnderwritingTask.objects.filter(status="pending").count()
    finished_count = UnderwritingTask.objects.exclude(status__in=["pending", "reviewing"]).count()

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