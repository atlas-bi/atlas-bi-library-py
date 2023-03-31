"""Custom Atlas Decorators."""
from functools import wraps
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.shortcuts import redirect, resolve_url
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

DEFAULT_MESSAGE = "Unauthorized action."


def user_passes_test(
    test_func: Any,
    login_url: Optional[str] = None,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
    message: str = DEFAULT_MESSAGE,
) -> Any:
    """Wrap decorator function.

    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func: Any) -> Any:
        @wraps(view_func)
        def _wrapped_view(
            request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
        ) -> Any:
            if not test_func(request.user):
                messages.add_message(request, messages.ERROR, message)
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator


def admin_required(
    view_func: Any = None,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
    login_url: str = settings.LOGIN_URL,
    message: str = DEFAULT_MESSAGE,
) -> Any:
    """Require admin to access function.

    Decorator for views that checks that the user is logged in and is a
    superuser, displaying message if provided.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser and u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


class NeverCacheMixin:
    """Use for class views where we don't want any caching."""

    @method_decorator(never_cache)
    def dispatch(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> Any:
        """Wrap function with decorator."""
        return super().dispatch(*args, **kwargs)  # type: ignore[misc]


class PermissionsCheckMixin:
    """Verify user permissions on class views."""

    request: HttpRequest = None
    required_permissions: Optional[Tuple[str, ...]] = None

    def get_permission_names(self) -> Any:
        """Return a list of permissions."""
        if self.required_permissions is None:
            raise ImproperlyConfigured(
                "PermissionsCheckMixin requires either a definition of ",
                "'required_permissions' or an implemenetatino of 'get_permission_names()'",
            )
        return self.required_permissions

    def dispatch(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> Any:
        """Wrap function with decorator."""
        if not self.request.user.has_perms(self.get_permission_names()):
            return redirect(
                request.META.get("HTTP_REFERER", "/")
                + "?error=You do not have permission to access that page."
            )
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]
