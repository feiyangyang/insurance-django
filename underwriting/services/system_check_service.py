import os

from django.conf import settings

from underwriting.models import AuditLog, Customer, Policy, UnderwritingTask


def get_database_check_status():
    database_config = settings.DATABASES.get("default", {})

    return {
        "database_engine": database_config.get("ENGINE", "未知"),
        "has_database_url": bool(os.environ.get("DATABASE_URL")),
        "customer_count": Customer.objects.count(),
        "policy_count": Policy.objects.count(),
        "underwriting_task_count": UnderwritingTask.objects.count(),
        "audit_log_count": AuditLog.objects.count(),
    }
