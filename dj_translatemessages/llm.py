import json
import logging

import tiktoken
from litellm import completion, completion_cost, get_max_tokens

from dj_translatemessages.prompts import get_system_prompt, get_preamble_template
from dj_translatemessages.settings import dj_translatemessages_settings

logging.getLogger("LiteLLM").setLevel(logging.ERROR)


def get_encoder(model):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text, enc):
    return len(enc.encode(text))


def make_batches(items, target_language, model):
    """Split items into token-safe batches."""
    encoder = get_encoder(model)

    # Precompute stable token costs
    system_tokens = count_tokens(get_system_prompt(), encoder)
    user_preamble = get_preamble_template().format(language=target_language)
    preamble_tokens = count_tokens(user_preamble, encoder)

    batches = []
    current = []

    for item in items:
        candidate = current + [item]

        # Variable part: JSON array of items
        items_json = json.dumps(candidate, ensure_ascii=False)
        items_tokens = count_tokens(items_json, encoder)

        # Estimated output tokens
        est_output_tokens = dj_translatemessages_settings.PER_ITEM_OUTPUT * len(candidate)

        # Total estimated tokens
        total_tokens = system_tokens + preamble_tokens + items_tokens + est_output_tokens

        max_context_tokens = get_max_tokens(dj_translatemessages_settings.LLM_MODEL)
        if current and total_tokens >= (
            max_context_tokens - dj_translatemessages_settings.SAFETY_MARGIN
        ):
            batches.append(current)
            current = [item]
        else:
            current = candidate

    if current:
        batches.append(current)

    return batches


def translate_batch(batch, target_language, model):
    user_prompt = get_preamble_template().format(language=target_language) + json.dumps(batch, ensure_ascii=False)
    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
        temperature=dj_translatemessages_settings.LLM_MODEL_TEMPERATURE,
        api_key=dj_translatemessages_settings.API_KEY,
    )
    cost = completion_cost(completion_response=response)

    content = response["choices"][0]["message"]["content"].strip()
    return json.loads(content), cost


def translate_items(items, target_language, model=dj_translatemessages_settings.LLM_MODEL):
    results = []
    total_cost = 0
    for batch in make_batches(items, target_language, model):
        translations, cost = translate_batch(batch, target_language, model)

        results.extend(translations)
        total_cost += cost

    return dict(zip(items, results)), total_cost
