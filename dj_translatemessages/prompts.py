from django.utils.module_loading import import_string

from dj_translatemessages.exceptions import DjTranslateMessagesException
from dj_translatemessages.settings import (
    DEFAULT_PREAMBLE_TEMPLATE,
    DEFAULT_SYSTEM_PROMPT,
    dj_translatemessages_settings,
)


def get_system_prompt():
    if (
        dj_translatemessages_settings.SYSTEM_PROMPT_FUNCTION
        and dj_translatemessages_settings.SYSTEM_PROMPT
    ):
        raise DjTranslateMessagesException(
            "You can't use system prompt function and system prompt at the same time."
        )
    elif dj_translatemessages_settings.SYSTEM_PROMPT_FUNCTION:
        func = import_string(dj_translatemessages_settings.SYSTEM_PROMPT_FUNCTION)
        return func()
    elif dj_translatemessages_settings.SYSTEM_PROMPT:
        return dj_translatemessages_settings.SYSTEM_PROMPT
    else:
        return DEFAULT_SYSTEM_PROMPT


def get_preamble_template():
    if (
        dj_translatemessages_settings.PREAMBLE_TEMPLATE_FUNCTION
        and dj_translatemessages_settings.PREAMBLE_TEMPLATE
    ):
        raise DjTranslateMessagesException(
            "You can't use system prompt function and system prompt at the same time."
        )
    elif dj_translatemessages_settings.PREAMBLE_TEMPLATE_FUNCTION:
        func = import_string(dj_translatemessages_settings.PREAMBLE_TEMPLATE_FUNCTION)
        return func()
    elif dj_translatemessages_settings.PREAMBLE_TEMPLATE:
        return dj_translatemessages_settings.PREAMBLE_TEMPLATE
    else:
        return DEFAULT_PREAMBLE_TEMPLATE
