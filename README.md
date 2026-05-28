# gardenbot

An AI-assisted system for landscaping and gardening.

## Quick start

### Local development

```bash
# Clone and install
git clone https://github.com/mcliff1/gardenbot.git
cd gardenbot
pip install -e ".[dev]"

# Run the dev server
gardenbot
# → http://localhost:8000
```

### Docker

```bash
docker compose up --build
# → http://localhost:8000
# Ollama available at http://localhost:11434
```

### Run tests

```bash
pytest
```

### Lint

```bash
ruff check src/ tests/
```

## Project structure

```
src/gardenbot/
├── main.py              # FastAPI app entry point
├── models/              # Pydantic data models
│   └── yard.py          # Yard, Area, Structure, Proposal models
├── routers/             # API route handlers
│   ├── yards.py         # Yard/area/structure CRUD
│   ├── plants.py        # Plant database
│   ├── proposals.py     # Proposal lifecycle
│   └── ai.py            # Ollama / AI integration
└── services/            # Business logic (future)

tests/                   # Test suite
static/                  # JS/CSS assets (Fabric.js, etc.)
templates/               # Jinja2 HTML templates
data/                    # JSON data files (runtime)
docs/                    # Design documentation
```

## Design documentation

| Document | Purpose |
|----------|---------|
| [`docs/design_questions.md`](docs/design_questions.md) | Design questions and answers |
| [`docs/design_spec.md`](docs/design_spec.md) | Final design specification |

## Configuration

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

Key settings:
- `GARDENBOT_DATA_DIR` — where JSON data files are stored
- `OLLAMA_BASE_URL` — Ollama server URL
- `OLLAMA_MODEL` — default model name
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` — optional cloud AI fallback
