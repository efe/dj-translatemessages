import io
from pathlib import Path
import vcr
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase

my_vcr = vcr.VCR(
    cassette_library_dir="cassettes",
    record_mode="once",
    filter_headers=["authorization"],
    decode_compressed_response=True,
)

class DjTranslateMessagesCommandTests(SimpleTestCase):
    def setUp(self):
        self.locale_root = Path(settings.LOCALE_PATHS[0]).resolve()
        self.po_file = self.locale_root / "tr" / "LC_MESSAGES" / "django.po"
        self._original_po = self.po_file.read_text(encoding="utf-8")

    def tearDown(self):
        self.po_file.write_text(self._original_po, encoding="utf-8")

    @my_vcr.use_cassette("translatemessages_tr.yaml")
    def test_translatemessages_writes_turkish_translation(self):
        out = io.StringIO()
        call_command("translatemessages", stdout=out, verbosity=2)

        updated = self.po_file.read_text(encoding="utf-8")
        assert 'msgid "Hello, world!"' in updated
        assert "msgstr" in updated and "Merhaba" in updated
