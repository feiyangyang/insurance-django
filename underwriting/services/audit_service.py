from underwriting.models import AuditLog


def create_audit_log(
    task,
    decision,
    comment="",
    action="decision",
    operator="",
    from_status="",
    to_status="",
):
    return AuditLog.objects.create(
        task=task,
        action=action,
        operator=operator,
        from_status=from_status,
        to_status=to_status,
        decision=decision,
        comment=comment,
    )


def get_audit_logs_for_task(task):
    return task.auditlog_set.all().order_by("-created_at", "-id")


def get_audit_log_list():
    return (
        AuditLog.objects.select_related("task", "task__application", "task__policy")
        .all()
        .order_by("-created_at", "-id")
    )
