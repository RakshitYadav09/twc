"""Helpers for password hashing using bcrypt.

This module is intentionally small and readable — a couple of thin helpers
that wrap :class:`passlib.context.CryptContext` so the rest of the codebase
doesn't need to know about the underlying library.
"""

from passlib.context import CryptContext


# Keep the context here so it can be tweaked in one place.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashUtils:
    """Lightweight wrapper around `passlib` for password work.

    Methods mirror what callers expect: `hash_password`, `verify_password`,
    and `needs_update`. Docstrings are brief and practical.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a bcrypt hash for `password`.

        Keeps the call-site tidy by returning the hashed string directly.
        """
        password_hash = pwd_context.hash(password)
        return password_hash

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Check whether `plain_password` matches `hashed_password`.

        Returns `True` on match, `False` otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def needs_update(hashed_password: str) -> bool:
        """Return `True` if the hash should be re-created (algorithm upgrade).

        Useful for rolling hashes forward without forcing a password reset.
        """
        return pwd_context.needs_update(hashed_password)
