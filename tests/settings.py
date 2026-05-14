from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SECRET_KEY = "test"
DEBUG = True
USE_I18N = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "dj_translatemessages",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = []
ROOT_URLCONF = "tests.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [str(BASE_DIR / "templates")],
    "APP_DIRS": True,
    "OPTIONS": {},
}]

# 🌍 Language setup
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("tr", "Turkish"),
]

# Locale path will be overridden to a tmp dir per test
LOCALE_PATHS = [str(BASE_DIR / "locale")]

DJ_TRANSLATEMESSAGES_LLM_MODEL = "openai/gpt-4o-mini"
DJ_TRANSLATEMESSAGES_API_KEY = "sk-proj-test"
DJ_TRANSLATEMESSAGES_SAFETY_MARGIN = 1000
DJ_TRANSLATEMESSAGES_PER_ITEM_OUTPUT = 100
DJ_TRANSLATEMESSAGES_LLM_MODEL_TEMPERATURE = 0
