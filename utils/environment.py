import sys

def is_dev():
    """Return True if running in development (not built as an exe), False otherwise."""
    return not hasattr(sys, 'frozen')
