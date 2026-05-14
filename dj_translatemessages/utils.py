from pathlib import Path

from babel import Locale
from django.apps import apps
from django.conf import settings

BASE_DIR = Path(settings.BASE_DIR).resolve()
BANNED_PARTS = {"site-packages", "dist-packages", ".venv", "venv", ".tox", ".cache"}


def is_project_path(p: Path):
    p = p.resolve()
    try:
        p.relative_to(BASE_DIR)
    except ValueError:
        return False
    return not any(part in BANNED_PARTS for part in p.parts)


def get_project_po_files():  # noqa
    """
    Return {language_code: [list of django.po paths]} using Django's search rules:
    - settings.LOCALE_PATHS
    - each app's ./locale/
    Excludes anything in virtualenvs/site-packages, even if under BASE_DIR.
    """
    results = {}

    # 1) Project-level LOCALE_PATHS
    for base in getattr(settings, "LOCALE_PATHS", []):
        for po in Path(base).rglob("LC_MESSAGES/django.po"):
            if is_project_path(po):
                lang = po.parent.parent.name  # locale/<lang>/LC_MESSAGES/django.po
                results.setdefault(lang, []).append(str(po))

    # 2) App-level locale dirs
    for app in apps.get_app_configs():
        loc = Path(app.path) / "locale"
        if loc.exists():
            for po in loc.rglob("LC_MESSAGES/django.po"):
                if is_project_path(po):
                    lang = po.parent.parent.name
                    results.setdefault(lang, []).append(str(po))

    return results


def get_language_name(locale_code: str) -> str:
    """
    Get the human-readable language name from a locale code (e.g., 'en_US').

    Args:
        locale_code (str): Locale code like 'en_US', 'fr_FR', etc.

    Returns:
        str: Human-readable language name, or 'Unknown' if not found.
    """
    locale = Locale.parse(locale_code)
    return locale.get_display_name(locale)
