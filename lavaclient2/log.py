# Attempt to import the NullHandler (not available in py2.6)
try:
    from logging import NullHandler
except ImportError:  # pragma: no cover
    from logging import Handler

    class NullHandler(Handler):
        def emit(self, record):
            pass
