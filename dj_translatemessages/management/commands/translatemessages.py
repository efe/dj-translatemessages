from time import perf_counter

from django.core.management.base import BaseCommand

from dj_translatemessages.llm import translate_items
from dj_translatemessages.settings import dj_translatemessages_settings
from dj_translatemessages.translation_files import fill_translations, parse_empty_translations
from dj_translatemessages.utils import get_language_name, get_project_po_files


class Command(BaseCommand):
    help = "Fill missing translations in .po files across the project."

    def handle(self, **options):  # noqa
        start = perf_counter()
        self.stdout.write(self.style.SUCCESS("▶ Translation run started."))
        self.stdout.write(
            f"Using translation model: {self.style.NOTICE(dj_translatemessages_settings.LLM_MODEL)}\n"
        )

        project_po_files = get_project_po_files()
        if not project_po_files:
            self.stdout.write(self.style.WARNING("No .po files found. Nothing to do."))
            return

        total_files = 0
        total_items = 0
        total_translated = 0
        total_cost = 0.0
        errors = 0

        for locale_code, po_file_paths in project_po_files.items():
            language_name = get_language_name(locale_code) or locale_code
            self.stdout.write(f"\n• Language: {language_name} [{locale_code}]")

            for po_file_path in po_file_paths:
                total_files += 1
                file_start = perf_counter()
                self.stdout.write(f"  - Scanning: {po_file_path}")

                try:
                    empty_translations = parse_empty_translations(po_file_path=po_file_path)
                    count_missing = len(empty_translations)
                    total_items += count_missing

                    if count_missing == 0:
                        self.stdout.write(self.style.WARNING("    No missing entries found."))
                        continue

                    self.stdout.write(f"    Missing entries: {count_missing}. Translating…")
                    translations, cost = translate_items(items=empty_translations, target_language=language_name)

                    produced = len(translations)
                    fill_translations(
                        po_file_path=po_file_path,
                        translations=translations,
                        output_file_path=po_file_path,
                    )

                    total_translated += produced
                    total_cost += cost or 0.0
                    elapsed = perf_counter() - file_start
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    Filled {produced} entr{'y' if produced == 1 else 'ies'} "
                            f"in {elapsed:.2f}s • Cost: ${cost:.4f}"
                        )
                    )

                except Exception as exc:
                    errors += 1
                    self.stderr.write(self.style.ERROR(f"    Error processing {po_file_path}: {exc!r}"))

        elapsed = perf_counter() - start
        self.stdout.write("\n" + ("=" * 60))
        self.stdout.write(
            self.style.SUCCESS(
                f"Done in {elapsed:.2f}s • Files: {total_files} • Missing found: {total_items} • "
                f"Filled: {total_translated} • Total cost: ${total_cost:.4f}"
            )
        )
        if errors:
            self.stderr.write(self.style.ERROR(f"Completed with {errors} error{'s' if errors != 1 else ''}."))
