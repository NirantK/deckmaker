# Deckmaker

An open Agent Skill for creating presentation decks from briefs, documents, reviewed outlines, and
relevant repository context with the `deckmaker` CLI and typed Python client.

It supports prompt-to-deck and document-to-deck workflows, optional brief interviews, bounded
repository context discovery, PDF/PPTX/image exports, retry-safe generation, and actionable error
recovery.

## Install

Install interactively with the open skills CLI:

```sh
npx skills add deck-in/deckmaker --skill deckmaker
```

Or install globally and non-interactively for the universal agent path:

```sh
npx skills add deck-in/deckmaker --skill deckmaker --agent universal --global --yes
```

The skill installs the `deckmaker` Python CLI with uv when needed. A PresentationsAI API key is
required for deck generation; credentials remain in an environment variable or operating-system
credential store.

API overview: https://www.presentations.ai/solutions/api

## License

MIT
