"""Compatibility shims for running Django 4.2 on Python 3.14."""

from django.template.context import BaseContext


def _base_context_copy(self):
    """Copy a template context without relying on ``copy(super())``.

    Django's ``BaseContext.__copy__`` uses ``copy(super())`` to build a fresh
    context. On Python 3.14 ``copy.copy()`` of a ``super`` object returns the
    ``super`` object itself instead of a copy of the wrapped instance, so
    Django 4.2 raises ``AttributeError: 'super' object has no attribute
    'dicts'`` whenever a context is copied (Django admin list views, for
    example). Reproducing the same result without ``super()`` keeps the admin
    console working on this interpreter.
    """
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = list(self.dicts)
    return duplicate


def apply():
    """Install the context copy fix."""
    BaseContext.__copy__ = _base_context_copy
