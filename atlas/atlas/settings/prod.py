"""Atlas prod settings."""
import contextlib

from .base import *

# import custom overrides

with contextlib.suppress(ImportError):
    from .prod_cust import *
