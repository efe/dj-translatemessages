from django.conf import settings as django_settings


# Default values
DEFAULT_SYSTEM_PROMPT = (
    "You are a professional translator. Translate into the target language.\n"
    "- Keep placeholders like {name} / {{handlebars}} unchanged.\n"
    "- Keep URLs and emails unchanged.\n"
    "- Return ONLY a JSON array of strings in the same order."
)
DEFAULT_PREAMBLE_TEMPLATE = "Translate these items into {language}. Return ONLY a JSON array:\n"


def _get_setting(name, default=None, *, required=False):
    if hasattr(django_settings, name):
        return getattr(django_settings, name)
    if required:
        raise AttributeError(f"Missing required setting: {name}")
    return default


class DjTranslateMessagesSettings:
    """Lazy loading of settings so override_settings works in tests"""

    @property
    def LLM_MODEL(self):
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_LLM_MODEL",
            required=True,
        )

    @property
    def API_KEY(self):
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_API_KEY",
            required=True,
        )

    @property
    def LLM_MODEL_TEMPERATURE(self):
        # Lower temperature makes outputs more predictable and factual, while higher temperature
        # increases randomness for more diverse and creative results.
        # https://www.youtube.com/shorts/XsLK3tPy9SI
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_LLM_MODEL_TEMPERATURE",
            0,
        )

    @property
    def SYSTEM_PROMPT_FUNCTION(self):
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_SYSTEM_PROMPT_FUNCTION",
        )

    @property
    def SYSTEM_PROMPT(self):
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_SYSTEM_PROMPT",
        )

    @property
    def PREAMBLE_TEMPLATE_FUNCTION(self):
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE_FUNCTION",
        )

    @property
    def PREAMBLE_TEMPLATE(self):
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE",
        )

    @property
    def SAFETY_MARGIN(self):
        # cushion to avoid hitting the hard limit
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_SAFETY_MARGIN",
            1000,
        )

    @property
    def PER_ITEM_OUTPUT(self):
        # rough estimate of tokens per translated item
        return _get_setting(
            "DJ_TRANSLATEMESSAGES_PER_ITEM_OUTPUT",
            100,
        )


dj_translatemessages_settings = DjTranslateMessagesSettings()
