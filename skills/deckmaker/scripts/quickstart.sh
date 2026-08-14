#!/usr/bin/env bash

set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  echo "Using existing uv; skipping the uv download and installer."
else
  if ! curl -LsSf https://astral.sh/uv/install.sh | sh; then
    echo "Could not install uv." >&2
    echo "Next: check network access to astral.sh, then rerun this script." >&2
    exit 1
  fi
  export PATH="${XDG_BIN_HOME:-$HOME/.local/bin}:$PATH"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not on PATH; restart the shell and rerun this script." >&2
  exit 1
fi

if ! uv tool install --upgrade deckmaker; then
  echo "Could not install deckmaker from PyPI." >&2
  echo "Next: check PyPI access and run 'uv tool install --upgrade deckmaker' again." >&2
  exit 1
fi
export PATH="$(uv tool dir --bin):$PATH"

if ! command -v deckmaker >/dev/null 2>&1; then
  echo "deckmaker was installed but its executable is not on PATH." >&2
  exit 1
fi

DECKMAKER_PROFILE="${DECKMAKER_PROFILE:-production}"
DECKMAKER_BASE_URL="${DECKMAKER_BASE_URL:-https://api.presentations.ai/api/v1}"
DECKMAKER_API_KEY_ENV="${DECKMAKER_API_KEY_ENV:-PRESENTATIONSAI_API_KEY}"
DECKMAKER_FORMAT="${DECKMAKER_FORMAT:-pdf}"
DECKMAKER_OUTPUT="${DECKMAKER_OUTPUT:-./deckmaker-example.${DECKMAKER_FORMAT}}"
DECKMAKER_TITLE="${DECKMAKER_TITLE:-AI Presentation Product Strategy}"
DECKMAKER_SLIDES="${DECKMAKER_SLIDES:-6}"
DECKMAKER_PROMPT="${DECKMAKER_PROMPT:-Create a concise product strategy presentation for an AI presentation tool. Cover the customer problem, solution, workflow, differentiation, go-to-market plan, and next steps. Use clear headings and concrete bullets.}"

if [[ ! "$DECKMAKER_API_KEY_ENV" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "DECKMAKER_API_KEY_ENV must be a valid environment-variable name." >&2
  exit 2
fi

if [[ -z "${!DECKMAKER_API_KEY_ENV:-}" ]]; then
  echo "Set $DECKMAKER_API_KEY_ENV to an API key, then rerun this script." >&2
  exit 2
fi

deckmaker config set "$DECKMAKER_PROFILE" \
  --base-url "$DECKMAKER_BASE_URL" \
  --api-key-env "$DECKMAKER_API_KEY_ENV" \
  --use

deckmaker auth status

deckmaker create deck "$DECKMAKER_PROMPT" \
  --deck-title "$DECKMAKER_TITLE" \
  --slides "$DECKMAKER_SLIDES" \
  --format "$DECKMAKER_FORMAT" \
  --output "$DECKMAKER_OUTPUT"

if [[ ! -s "$DECKMAKER_OUTPUT" ]]; then
  echo "Deck export was not written to $DECKMAKER_OUTPUT." >&2
  echo "Next: inspect the request with 'deckmaker get status REQUEST_ID' before resubmitting." >&2
  exit 1
fi

echo "Deck downloaded to $DECKMAKER_OUTPUT"
