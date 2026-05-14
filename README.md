# dj-translatemessages (formerly yesglot) 

[![](https://img.shields.io/pypi/v/yesglot)](https://pypi.org/project/yesglot) [![](https://img.shields.io/codecov/c/github/efe/yesglot)](https://app.codecov.io/github/efe/yesglot) [![](https://img.shields.io/github/check-runs/efe/yesglot/main)](https://github.com/efe/yesglot/actions?query=branch%3Amain) [![](https://img.shields.io/github/license/efe/yesglot)](https://github.com/efe/yesglot/blob/main/LICENSE) ![](https://img.shields.io/pypi/frameworkversions/django/yesglot)

> LLM-powered Django translations ✨

A Django app that autofills missing translations in `.po` files using an LLM, while respecting [ICU](https://unicode-org.github.io/icu/) format placeholders and source references.

## Why yesglot?

- 🧠 LLM-powered: works with [100+ LLM models](https://models.litellm.ai/) through LiteLLM’s unified API
- 🔒 Placeholder-safe: keeps {name}, {{handlebars}}, URLs, and emails intact
- 📦 Django-native: one management command: python manage.py translatemessages
- 🧮 Cost-aware: prints per-file and total cost (via LiteLLM)
- 🧱 Token-safe batching: automatically splits work to avoid context overflows

## 🚀Quick Start

### Installation

```python
pip install yesglot
```

Add yesglot to your Django settings:

```python
INSTALLED_APPS = [
    # ...
    "yesglot",
]
```

## Configuration

Set the model from [100+ LLM models](https://models.litellm.ai/) and API key in your Django settings:

```python
YESGLOT_LLM_MODEL = "openai/gpt-4o-mini"
YESGLOT_API_KEY = "sk-..."
```


## Usage

A typical workflow with Django translations:

1. Extract messages into .po files (creates entries with empty msgstr):

```
python manage.py makemessages -all
```

2. Autofill missing translations with *yesglot*:

```
python manage.py translatemessages
```

Example output:

```
▶ Translation run started.
Using translation model: openai/gpt-4o-mini

• Language: French [fr]
  - Scanning: locale/fr/LC_MESSAGES/django.po
    Missing entries: 12. Translating…
    Filled 12 entries in 3.21s • Cost: $0.0123

============================================================
Done in 3.76s • Files: 1 • Missing found: 12 • Filled: 12 • Total cost: $0.0123
```

3. Compile translations into .mo files (so Django can use them at runtime):

```
python manage.py compilemessages
```

## django-modeltranslation support

If you use [django-modeltranslation](https://github.com/deschler/django-modeltranslation) for dynamic model fields, install the optional extra and run the new command:

```bash
pip install "yesglot[modeltranslation]"
python manage.py translatemodels --models blog.Post shop.Product --languages fr de --source-language en
```

The command will detect registered modeltranslation fields, translate only the models you list, fill missing values, and save them back to the database.

## Advantage Usage

Optional parameters,

- `YESGLOT_SAFETY_MARGIN`: 1000 (default)
- `YESGLOT_PER_ITEM_OUTPUT`: 100 (default)
- `YESGLOT_LLM_MODEL_TEMPERATURE`: 0 (default)

### System Prompt

It is preconfigured, though you may override it to tailor the behavior of your translation.

- `SYSTEM_PROMPT_FUNCTION`: for example, `"myproject.myapp.utils.get_system_prompt"`
- `SYSTEM_PROMPT`: string

Default:

> You are a professional translator. Translate into the target language.
> - Keep placeholders like {name} / {{handlebars}} unchanged.
> - Keep URLs and emails unchanged.
> - Return ONLY a JSON array of strings in the same order.


### Preamble Template

It’s already configured, but you can override it to adjust how your translation behaves.

- `PREAMBLE_TEMPLATE_FUNCTION`: for example, `"myproject.myapp.utils.get_preamble"`
- `PREAMBLE_TEMPLATE`: string

Default:

> Translate these items into {language}. Return ONLY a JSON array:

# License

Mozilla Public License Version 2.0

![Yesglot Logo](assets/logo.png)
