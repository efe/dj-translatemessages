from django.test import SimpleTestCase
from django.test.utils import override_settings

from dj_translatemessages.exceptions import DjTranslateMessagesException
from dj_translatemessages.prompts import get_system_prompt, get_preamble_template
from dj_translatemessages.settings import DEFAULT_SYSTEM_PROMPT, DEFAULT_PREAMBLE_TEMPLATE


def dummy_function():
    return "dummy"


class SystemPromptTests(SimpleTestCase):
    @override_settings(
        DJ_TRANSLATEMESSAGES_SYSTEM_PROMPT_FUNCTION="tests.test_prompts.dummy_function",
        DJ_TRANSLATEMESSAGES_SYSTEM_PROMPT="literal",
    )
    def test_conflict_raises(self):
        with self.assertRaises(DjTranslateMessagesException):
            get_system_prompt()

    @override_settings(DJ_TRANSLATEMESSAGES_SYSTEM_PROMPT_FUNCTION="tests.test_prompts.dummy_function")
    def test_from_function(self):
        self.assertEqual(get_system_prompt(), "dummy")

    @override_settings(DJ_TRANSLATEMESSAGES_SYSTEM_PROMPT="literal-sp")
    def test_literal(self):
        self.assertEqual(get_system_prompt(), "literal-sp")

    def test_default(self):
        self.assertEqual(get_system_prompt(), DEFAULT_SYSTEM_PROMPT)


class PreambleTemplateTests(SimpleTestCase):
    @override_settings(
        DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE_FUNCTION="tests.test_prompts.dummy_function",
        DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE="literal",
    )
    def test_conflict_raises(self):
        with self.assertRaises(DjTranslateMessagesException):
            get_preamble_template()

    @override_settings(
        DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE_FUNCTION="tests.test_prompts.dummy_function",
        DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE="",
    )
    def test_from_function(self):
        self.assertEqual(get_preamble_template(), "dummy")

    @override_settings(
        DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE_FUNCTION="",
        DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE="Hi in {language}: ",
        DEFAULT_PREAMBLE_TEMPLATE="Default {language}: ",
    )
    def test_literal(self):
        self.assertEqual(get_preamble_template(), "Hi in {language}: ")

    @override_settings(
        DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE_FUNCTION="",
        DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE="",
        DEFAULT_PREAMBLE_TEMPLATE="Default {language}: ",
    )
    def test_default(self):
        self.assertEqual(get_preamble_template(), DEFAULT_PREAMBLE_TEMPLATE)
