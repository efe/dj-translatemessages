# Migration Guide for 2.0.0

Version `2.0.0` renames the Django app from `yesglot` to `dj_translatemessages`.
This is a breaking change for imports, `INSTALLED_APPS`, and Django setting names.

## What to change

### 1. Update `INSTALLED_APPS`

Before:

```python
INSTALLED_APPS = [
    "yesglot",
]
```

After:

```python
INSTALLED_APPS = [
    "dj_translatemessages",
]
```

### 2. Update imports

Before:

```python
from yesglot.llm import translate_items
from yesglot.prompts import get_system_prompt
```

After:

```python
from dj_translatemessages.llm import translate_items
from dj_translatemessages.prompts import get_system_prompt
```

### 3. Rename Django settings

The old `YESGLOT_*` settings are no longer supported in `2.0.0`.

| Old setting | New setting |
| --- | --- |
| `YESGLOT_LLM_MODEL` | `DJ_TRANSLATEMESSAGES_LLM_MODEL` |
| `YESGLOT_API_KEY` | `DJ_TRANSLATEMESSAGES_API_KEY` |
| `YESGLOT_LLM_MODEL_TEMPERATURE` | `DJ_TRANSLATEMESSAGES_LLM_MODEL_TEMPERATURE` |
| `YESGLOT_SYSTEM_PROMPT_FUNCTION` | `DJ_TRANSLATEMESSAGES_SYSTEM_PROMPT_FUNCTION` |
| `YESGLOT_SYSTEM_PROMPT` | `DJ_TRANSLATEMESSAGES_SYSTEM_PROMPT` |
| `YESGLOT_PREAMBLE_TEMPLATE_FUNCTION` | `DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE_FUNCTION` |
| `YESGLOT_PREAMBLE_TEMPLATE` | `DJ_TRANSLATEMESSAGES_PREAMBLE_TEMPLATE` |
| `YESGLOT_SAFETY_MARGIN` | `DJ_TRANSLATEMESSAGES_SAFETY_MARGIN` |
| `YESGLOT_PER_ITEM_OUTPUT` | `DJ_TRANSLATEMESSAGES_PER_ITEM_OUTPUT` |

### 4. Reinstall the package if needed

Install the renamed distribution:

```bash
pip install dj-translatemessages
```

## What did not change

- The management command is still `python manage.py translatemessages`
- The package purpose and runtime behavior are unchanged outside of the rename
