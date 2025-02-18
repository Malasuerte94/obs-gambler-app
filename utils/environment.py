import sys

def is_dev():
    """Detect if the app is running as a compiled .exe."""
    return getattr(sys, 'frozen', True)
