# gardenbot

An AI-assisted system for landscaping and gardening.

## Initial system specifications

### Goals
- Manage lawn and garden planning in one place.
- Start with requirements and a clear MVP scope.

### Technical direction
- Primary language: **Python**.
- Local AI runtime: **Ollama** (for planning and recommendation workflows).

### Core capability (first feature)
- Let the user select a flower bed layout template.
- Visualize that layout over multiple years to show how the bed evolves over time.

### MVP notes
- Inputs should include layout choice, plant list, and start year.
- Outputs should include year-by-year bed views and simple growth assumptions.

## Design process

Before implementation begins, we are working through a structured set of design questions.

| Document | Purpose |
|----------|---------|
| [`docs/design_questions.md`](docs/design_questions.md) | Open questions to answer before writing code |
| `docs/design_spec.md` | *(future)* Final design spec, populated as questions are answered |

## Agent context

A Copilot coding-agent context file lives at [`.github/agents/gardenbot.md`](.github/agents/gardenbot.md).
It provides coding conventions, domain vocabulary, and instructions the agent should follow in every session.
