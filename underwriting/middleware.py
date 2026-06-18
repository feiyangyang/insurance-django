from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._requires_login(request) and not request.user.is_authenticated:
            login_url = reverse("login")
            return redirect(f"{login_url}?next={request.get_full_path()}")

        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)

    def _requires_login(self, request):
        path = request.path
        public_prefixes = (
            reverse("login"),
            "/static/",
            "/admin/",
        )
        return not any(path.startswith(prefix) for prefix in public_prefixes)
