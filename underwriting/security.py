from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import OperationLog, PermissionPoint, UserProfile

DEMO_PERMISSION_CODES = {
    "customer.create",
    "customer.edit",
    "customer.delete",
    "application.create",
    "application.edit",
    "application.delete",
    "risk.edit",
    "underwriting.create",
    "underwriting.decision",
    "underwriting.edit",
    "underwriting.delete",
    "policy.edit",
    "policy.delete",
    "system.form_config",
    "system.user",
    "system.role",
    "system.company",
    "system.department",
    "system.operation_log",
    "system.db_check",
}


def get_user_permissions(user):
    if settings.PUBLIC_DEMO_MODE:
        return DEMO_PERMISSION_CODES | set(PermissionPoint.objects.values_list("code", flat=True))
    if not user.is_authenticated:
        return set()
    if user.is_superuser:
        return set(PermissionPoint.objects.values_list("code", flat=True))

    profile, _ = UserProfile.objects.get_or_create(user=user)
    return set(
        PermissionPoint.objects.filter(roles__users=profile, roles__is_active=True)
        .values_list("code", flat=True)
        .distinct()
    )


def user_has_permission(user, permission_code):
    if not permission_code:
        return True
    return permission_code in get_user_permissions(user)


def permission_required(permission_code):
    def decorator(view_func):
        if settings.PUBLIC_DEMO_MODE:
            @wraps(view_func)
            def demo_wrapped(request, *args, **kwargs):
                return view_func(request, *args, **kwargs)
            return demo_wrapped

        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if not user_has_permission(request.user, permission_code):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def log_operation(request, module, action, target=None, description="", result="success"):
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    profile = None
    if user:
        profile, _ = UserProfile.objects.get_or_create(user=user)

    OperationLog.objects.create(
        user=user,
        username=user.username if user else "",
        company_name=profile.company.name if profile and profile.company else "",
        department_name=profile.department.name if profile and profile.department else "",
        module=module,
        action=action,
        target_type=target.__class__.__name__ if target else "",
        target_id=str(getattr(target, "id", "")) if target else "",
        description=description,
        path=request.path if request else "",
        ip_address=_get_ip(request),
        result=result,
    )


def _get_ip(request):
    if not request:
        return None
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
