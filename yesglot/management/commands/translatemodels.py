from collections import defaultdict
from time import perf_counter

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from yesglot.llm import translate_items
from yesglot.settings import yesglot_settings
from yesglot.utils import get_language_name

try:
    from modeltranslation.translator import translator
    from modeltranslation.utils import build_localized_fieldname
except ImportError as exc:  # pragma: no cover - exercised via CommandError
    translator = None
    build_localized_fieldname = None
    _import_error = exc
else:
    _import_error = None


def _ensure_modeltranslation_installed():
    if translator is None or build_localized_fieldname is None:
        raise CommandError(
            "django-modeltranslation is required for this command. "
            "Install it with `pip install yesglot[modeltranslation]` or add it to your project."
        ) from _import_error


class Command(BaseCommand):
    help = "Fill missing django-modeltranslation fields on selected models using yesglot."

    def add_arguments(self, parser):  # noqa: D401
        parser.add_argument(
            "--models",
            nargs="+",
            required=True,
            help="Model labels to translate, e.g. blog.Post shop.Product.",
        )
        parser.add_argument(
            "--languages",
            nargs="+",
            help="Target language codes. Defaults to MODELTRANSLATION_LANGUAGES or settings.LANGUAGES.",
        )
        parser.add_argument(
            "--source-language",
            dest="source_language",
            help="Language code to translate from. Defaults to settings.LANGUAGE_CODE.",
        )

    def handle(self, *args, **options):  # noqa: D401
        _ensure_modeltranslation_installed()

        start = perf_counter()
        self.stdout.write(self.style.SUCCESS("▶ Modeltranslation run started."))
        self.stdout.write(f"Using translation model: {self.style.NOTICE(yesglot_settings.LLM_MODEL)}\n")

        languages = (
            options["languages"]
            or getattr(settings, "MODELTRANSLATION_LANGUAGES", None)
            or [code for code, _ in getattr(settings, "LANGUAGES", [])]
        )
        source_language = options["source_language"] or settings.LANGUAGE_CODE
        if source_language not in languages:
            languages = [source_language] + list(languages)

        target_languages = [lang for lang in languages if lang != source_language]
        if not target_languages:
            raise CommandError("No target languages to translate. Adjust --languages or --source-language.")

        total_models = 0
        total_items = 0
        total_translated = 0
        total_cost = 0.0
        errors = 0

        for model_label in options["models"]:
            try:
                model = apps.get_model(model_label)
            except LookupError as exc:
                raise CommandError(f"Unknown model label '{model_label}'.") from exc

            try:
                opts = translator.get_options_for_model(model)
            except Exception as exc:  # pragma: no cover - defensive
                raise CommandError(f"Model '{model_label}' is not registered with django-modeltranslation.") from exc

            base_fields = getattr(opts, "fields", None)
            if not base_fields:
                self.stdout.write(
                    self.style.WARNING(f"• {model_label}: no translation fields registered, skipping.")
                )
                continue

            model_field_names = {f.name for f in model._meta.get_fields() if getattr(f, "concrete", False)}

            # Build field maps
            source_field_map = {}
            target_field_map = {}
            fetch_fields = {"pk"}

            for field_name in base_fields:
                source_field = build_localized_fieldname(field_name, source_language)
                if source_field not in model_field_names:
                    source_field = field_name  # fallback to base column
                source_field_map[field_name] = source_field
                fetch_fields.add(source_field)

                per_language_targets = {}
                for lang in target_languages:
                    localized = build_localized_fieldname(field_name, lang)
                    if localized in model_field_names:
                        per_language_targets[lang] = localized
                        fetch_fields.add(localized)
                if per_language_targets:
                    target_field_map[field_name] = per_language_targets

            if not target_field_map:
                self.stdout.write(
                    self.style.WARNING(f"• {model_label}: no target translation fields found for selected languages.")
                )
                continue

            self.stdout.write(f"• Model: {model_label}")
            total_models += 1

            rows = list(model.objects.values(*sorted(fetch_fields)))
            pending_by_lang = defaultdict(list)
            seen_texts_by_lang = defaultdict(list)

            for row in rows:
                for base_field in base_fields:
                    source_field = source_field_map.get(base_field)
                    source_value = row.get(source_field) or row.get(base_field)
                    if source_value in (None, ""):
                        continue

                    text_value = str(source_value)
                    targets = target_field_map.get(base_field, {})

                    for lang, localized_field in targets.items():
                        current_value = row.get(localized_field)
                        if current_value not in (None, ""):
                            continue

                        pending_by_lang[lang].append((row["pk"], localized_field, text_value))
                        seen_texts_by_lang[lang].append(text_value)
                        total_items += 1

            if not pending_by_lang:
                self.stdout.write(self.style.WARNING("  No missing translations found."))
                continue

            updates = defaultdict(dict)

            for lang, records in pending_by_lang.items():
                unique_texts = list(dict.fromkeys(seen_texts_by_lang[lang]))
                target_name = get_language_name(lang) or lang
                self.stdout.write(f"  - Language: {target_name} [{lang}] • Missing: {len(records)}. Translating…")

                translations, cost = translate_items(items=unique_texts, target_language=target_name)
                total_cost += cost or 0.0

                for pk, localized_field, source_text in records:
                    translated = translations.get(source_text)
                    if translated in (None, ""):
                        errors += 1
                        self.stderr.write(
                            self.style.ERROR(
                                f"    Missing translation for pk={pk} field={localized_field!r} ({model_label})."
                            )
                        )
                        continue

                    updates[pk][localized_field] = translated
                    total_translated += 1

            # Persist updates
            for pk, fields in updates.items():
                model.objects.filter(pk=pk).update(**fields)

            updated_fields = sum(len(v) for v in updates.values())
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Filled {updated_fields} entr{'y' if updated_fields == 1 else 'ies'}."
                )
            )

        elapsed = perf_counter() - start
        self.stdout.write("\n" + ("=" * 60))
        self.stdout.write(
            self.style.SUCCESS(
                f"Done in {elapsed:.2f}s • Models: {total_models} • Missing found: {total_items} • "
                f"Filled: {total_translated} • Total cost: ${total_cost:.4f}"
            )
        )
        if errors:
            self.stderr.write(self.style.ERROR(f"Completed with {errors} error{'s' if errors != 1 else ''}."))

