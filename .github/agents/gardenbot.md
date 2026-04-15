# Gardenbot – Copilot Agent Context

This file provides context for the GitHub Copilot coding agent working in this repository.

## Project summary

**Gardenbot** is an AI-assisted lawn and garden management system.  
Primary language: **Python**.  
Local AI runtime: **Ollama** (local LLM for planning and recommendation workflows).

## Current phase

We are in the **design specification phase**.  
The goal is to answer the questions in [`docs/design_questions.md`](../../docs/design_questions.md)
and use those answers to produce a complete design spec before writing production code.

## Repository layout (target)

```
gardenbot/
├── .github/
│   └── agents/
│       └── gardenbot.md      ← this file
├── docs/
│   ├── design_questions.md   ← open design questions to work through
│   └── design_spec.md        ← (future) completed design spec
├── gardenbot/                ← (future) Python package
│   ├── __init__.py
│   ├── cli.py
│   ├── layouts/              ← flower-bed layout templates
│   └── ai/                   ← Ollama integration layer
├── tests/
├── README.md
└── pyproject.toml
```

## Coding conventions

- Follow [PEP 8](https://peps.python.org/pep-0008/) for all Python code.
- Use type hints throughout.
- Prefer `pytest` for tests.
- Use `rich` or `matplotlib` for terminal/visual output; choose based on the design spec answers.
- Keep Ollama calls isolated in `gardenbot/ai/` so they can be swapped or mocked in tests.

## Key domain concepts

| Term | Meaning |
|------|---------|
| **Flower bed** | A defined planting area with a shape, dimensions, and a list of plants. |
| **Layout** | A template that defines bed shape, zones, and recommended plant combinations. |
| **Season / Year view** | A rendered snapshot of how a bed looks (or is predicted to look) in a given year. |
| **Growth model** | Rules or AI-generated estimates for how each plant spreads and matures over time. |
| **Garden plan** | A collection of beds, a start year, and user preferences. |

## Agent instructions

1. Read `docs/design_questions.md` before suggesting or writing any implementation code.
2. Do not begin implementing features until the design questions are answered (they will be filled in by the user or a future session).
3. When a design question is answered, update `docs/design_spec.md` accordingly.
4. When adding new capabilities, add a corresponding section to `docs/design_spec.md` and tests under `tests/`.
5. Keep Ollama interactions fully abstracted so the app still runs (in a degraded mode) if Ollama is unavailable.
