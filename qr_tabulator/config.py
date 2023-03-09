"""Default configuration

Use env var to override
"""
import os

SECRET_KEY = os.getenv("SECRET_KEY")
# URL scheme to use outside of request context
