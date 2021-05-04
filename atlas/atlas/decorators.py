"""Custom Atlas Decorators."""
from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import resolve_url

DEFAULT_MESSAGE = "Unauthorised action."


def user_passes_test(
    test_func,
    login_url=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    message=DEFAULT_MESSAGE,
):
    """Wrap decorator function.

    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
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
    view_func=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url="/login",
    message=DEFAULT_MESSAGE,
):
    """Require admin to access function.

    Decorator for views that checks that the user is logged in and is a
    superuser, displaying message if provided.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_admin and u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
