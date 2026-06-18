from .security import get_user_permissions


def permission_context(request):
    permissions = get_user_permissions(request.user)
    return {
        "current_permissions": permissions,
        "can": lambda code: code in permissions,
    }
