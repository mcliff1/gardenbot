# Gardenbot – Design Specification

This document summarises all decisions captured in `docs/design_questions.md`.

---

## 1. Users and personas

| Decision | Detail |
|---|---|
| Primary user | Homeowner. Output (plans, visualizations, schedules) is handed off to a professional landscaper. |
| Technical skill | Comfortable in a terminal; UI also desired for quick visualization. |
| Multi-user | Start single-user; architecture should allow expansion to multiple profiles later. |
| Multi-property | Start single-property; may extend later. Properties are independent of each other. |

---

## 2. Interface and interaction

| Decision | Detail |
|---|---|
| Primary interface | Web-based UI (deployed on Ubuntu Server with Docker + DNS/SSL). |
| Secondary interface | CLI (optional), implemented as an interactive REPL session. |
| Recommended stack | **FastAPI** backend + **HTMX** (or lightweight JS framework). Streamlit is an alternative for rapid prototyping. |
| AI invocation | On-demand (specific commands/actions). Conversational/chat mode is a nice-to-have. |
| Visualization output | Interactive HTML page rendered in the web UI. |

---

## 3. Garden data model

### Beds / areas
Track: name, location/coordinates, shape, sun exposure, notes.  
Scope extends beyond flower beds: the full-yard view includes trees, bushes, hardscape (patio, shed), and utilities.

### Plants
Track: common name, botanical name, perennial/annual, bloom time, mature size, color, companion plants, care notes.

### Plant database
Ship a **small built-in starter database** of common plants.  
Users can add custom entries.  
External API integration (Trefle, USDA PLANTS) is a future enhancement.

### Layout templates (v1)
Rectangle and freeform polygon.  
MVP beds: two freeform foundation beds adjacent to the house + two rectangular beds elsewhere.

### Placement
Scaled canvas with free-form drag/drop placement.  
Optional snap-to-grid overlay.

---

## 4. Multi-year visualization

| Decision | Detail |
|---|---|
| What is shown | Plant sizes, bloom times, die-back, and spreading across years. |
| Default projection | 3 years. |
| Growth model | Rule-based (spread/growth rates stored in plant DB). Hooks for Ollama inference as optional enhancement. User overrides always allowed. |
| Plan vs. reality | Yes — users can annotate past years to compare planned vs. actual. |
| Seasonal variation | Yes — at minimum spring / summer / fall states per year. |

---

## 5. AI / Ollama integration

| Decision | Detail |
|---|---|
| Model selection | User-configurable. A vision-capable model (e.g. LLaVA or multimodal variant) must be supported. |
| Tasks handled | Plant suggestions, layout critique, care-schedule generation, natural language queries. |
| Plain-English explanations | Yes. |
| Inference backend | Local Ollama (8 B models) is primary. Optional cloud API fallback (OpenAI / Anthropic) configurable via API key. |
| Conversation history | Session transcripts are not persisted. Garden state/plan is updated after each AI interaction so the AI has current context in future sessions. |

---

## 6. Data storage and persistence

| Decision | Detail |
|---|---|
| Storage format | JSON files for local data; Docker-based deployment. |
| Export / import | Bidirectional. Export plans for contractor hand-off; import contractor bids as "proposal" records on the plan. |
| Cloud sync | Not required (server-based deployment). |
| Version history | Yes — undo/redo and date-based snapshots. |

---

## 7. Lawn management

In-scope features for v1: mowing schedule, fertiliser calendar, watering reminders, weed tracking, pest/disease logging.

Weather/forecast integration and irrigation system integration are **not** in scope for v1.  
Drip lines are expected to be physically in place; only manual watering notes are recorded.

---

## 8. Notifications and scheduling

| Decision | Detail |
|---|---|
| Schedule type | Weekly/monthly care schedule / task list. |
| Delivery | In-app (v1). |
| Task triggers | Both calendar-date-based and growth-stage-based tasks, as appropriate. |

---

## 9. MVP scope

**Required for first useful demo (definition of done):**
1. User can define their current garden layout.
2. User can create multiple proposals representing changes to that layout.
3. User can visualize any layout or proposal.

**Explicitly out of scope for v1:**
- User logins / authentication.
- Dynamic plant growth simulation (static layouts are acceptable; no animation or real-time modelling required).

---

## 10. Non-functional requirements

| Decision | Detail |
|---|---|
| Target platform | Ubuntu Server + Docker (primary). Cloud-portable to AWS / GCP in the future. |
| Performance | Local Ollama 8 B models. No hard latency SLA for v1; inference backend must be swappable. |
| Packaging | pip (Python package) **and** Docker (containerised deployment). |
| Privacy | No special privacy requirements; garden/location data is not considered sensitive. |

---

## Recommended tech stack summary

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | HTMX + minimal JS (or Streamlit for prototyping) |
| Data storage | JSON files |
| Containerisation | Docker + Docker Compose |
| AI inference | Ollama (local, 8 B models) with cloud API fallback |
| Visualisation | Interactive HTML/SVG canvas rendered in the web UI |
