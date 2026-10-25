"""Domain exceptions for the application.

These are raised by services and mapped to HTTP responses in one place
(the exception handlers registered in create_app), so routers stay clean.
"""


class UserAlreadyExists(Exception):  # noqa: N818
    """Raised when registering with an email address that is already taken."""


class InvalidCredentials(Exception):  # noqa: N818
    """Raised when login credentials are wrong (unknown email or bad password)."""


class InvalidToken(Exception):  # noqa: N818
    """Raised by TokenService when a JWT cannot be decoded or has expired."""
