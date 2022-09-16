"""Atlas Group views."""

import io
import re

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from index.models import (
    FavoriteFolders,
    StarredReports,
    UserPreferences,
    UserRoles,
    Users,
)
from PIL import Image, ImageDraw, ImageFont

from atlas.decorators import admin_required


@login_required
def index(request, pk=None):
    """User profile page."""
    return render(request, "group/index.html.dj")
