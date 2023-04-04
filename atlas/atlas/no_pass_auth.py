"""Custom auth model for debugging.

This auth will allow users to login with an email address
and password of "123", or whatever is set in model.
"""

from typing import Any, Optional

from django.http import HttpRequest
from index.models import Users


class Backend:
    """Log in to Django without providing a password."""

    # pylint: disable=R0201,W0613
    def authenticate(
        self, request: HttpRequest, username: Optional[str] = None, password: Any = None
    ) -> Optional[Users]:
        """Check that user exists."""
        try:
            return Users.objects.filter(email=username).first()
        except Users.DoesNotExist:
            return None

    # pylint: disable=R0201
    def get_user(self, user_id: int) -> Optional[Users]:
        """Get user object."""
        try:
            return Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return None
