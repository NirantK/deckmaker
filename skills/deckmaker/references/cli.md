# Deckmaker CLI reference

## Environments

| Environment | Base URL | Credential variable |
| --- | --- | --- |
| Production | `https://api.presentations.ai/api/v1` | `PRESENTATIONSAI_API_KEY` |

Configure a secret-free profile:

```sh
deckmaker config set production \
  --base-url https://api.presentations.ai/api/v1 \
  --api-key-env PRESENTATIONSAI_API_KEY \
  --use
deckmaker auth status
```

For another authorized API environment, substitute its base URL and credential variable name. The
profile stores the variable name, not its value. Use `deckmaker auth login` only when the user wants
the key stored in the OS credential store.

## Prompt-to-deck

```sh
deckmaker create deck \
  "Create a six-slide board update with decisions, risks, and next steps." \
  --deck-title "Board update" \
  --slides 6 \
  --format pdf \
  --output ./board-update.pdf
```

Generation waits for completion by default. Omit `--request-id` to use the stable ID derived from
the logical request. Repeating the same command safely resumes or replays it.

## Document-to-deck

```sh
deckmaker create deck \
  "Turn this source into an executive-ready narrative." \
  --deck-title "Quarterly review" \
  --file ./quarterly-review.pdf \
  --slides 6 \
  --format pdf \
  --output ./quarterly-review-deck.pdf
```

Repeat `--file` for multiple sources. Use `--source-text` or `--source-text-file` for plain text.

## Review an outline first

```sh
deckmaker create outline \
  "Create a six-slide board update grounded in the source." \
  --file ./quarterly-review.pdf \
  --slides 6 \
  --output ./reviewed-outline.json

deckmaker create deck \
  --deck-title "Quarterly review" \
  --outline ./reviewed-outline.json \
  --format pdf \
  --output ./quarterly-review-deck.pdf
```

An authored outline fixes the slide list; do not combine `--outline` with `--slides`, a prompt, or
source inputs.

## Recover and inspect

```sh
deckmaker get status REQUEST_ID
deckmaker list decks
deckmaker get deck DECK_ID
deckmaker get deck DECK_ID pdf --output ./deck.pdf
```

Use `--no-wait` only when the caller wants asynchronous submission. Resume with `get status`.

## Typed Python client

```python
import os

from deckmaker.client import PresentationsAIClient
from deckmaker.models import CreateDeckRequest

with PresentationsAIClient(
    api_key=os.environ["PRESENTATIONSAI_API_KEY"],
    base_url="https://api.presentations.ai/api/v1",
) as client:
    created = client.create_deck(
        CreateDeckRequest(deck_title="Board update", prompt="Summarize the quarter"),
        request_id="board-update-v1",
    )
    finished = client.wait_for_request(created.request_id, timeout=1800)
    print(finished.deck_id)
```

## Structured execution

For automation, request structured output and suppress progress messages:

```sh
deckmaker create deck \
  "Create a six-slide board update." \
  --deck-title "Board update" \
  --format pdf \
  --output ./board-update.pdf \
  --json --quiet
```

The CLI emits JSON for both success and handled failures when `--json` is present. Check the exit
status before reading `ok` and follow `references/errors.md` for recovery.
