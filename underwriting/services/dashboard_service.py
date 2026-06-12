from django.db.models import Count

from underwriting.models import (
    Customer,
    InsuranceApplication,
    Policy,
    RiskAssessment,
    UnderwritingTask,
)


def get_dashboard_context():
    task_queryset = UnderwritingTask.objects.select_related(
        "application",
        "application__customer",
        "policy",
        "policy__customer",
    )

    risk_counts = {
        item["risk_level"]: item["count"]
        for item in RiskAssessment.objects.values("risk_level").annotate(count=Count("id"))
    }

    return {
        "customer_count": Customer.objects.count(),
        "application_count": InsuranceApplication.objects.count(),
        "policy_count": Policy.objects.count(),
        "pending_count": task_queryset.filter(status="pending").count(),
        "approved_count": task_queryset.filter(status="approved").count(),
        "rejected_count": task_queryset.filter(status="rejected").count(),
        "high_risk_count": RiskAssessment.objects.filter(risk_level="high").count(),
        "risk_counts": {
            "low": risk_counts.get("low", 0),
            "medium": risk_counts.get("medium", 0),
            "high": risk_counts.get("high", 0),
        },
        "tasks": task_queryset.order_by("-created_at")[:10],
        "applications": (
            InsuranceApplication.objects.select_related("customer", "risk_assessment")
            .all()
            .order_by("-created_at")[:8]
        ),
    }
