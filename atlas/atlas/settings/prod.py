from .settings import *

# import custom overrides
try:
    from .prod_cust import *
except ImportError:
    pass
