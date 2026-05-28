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

### Coordinate system

All coordinates are in **feet** (decimal, e.g. `12.5`), measured from a **user-defined origin point** (set during initial yard setup — typically a corner of the property or house).

```
coordinate: { x: float, y: float }   // feet from origin
polygon:    [ coordinate, ... ]       // ordered vertices
```

The yard `boundary` polygon defines the property extents. All area and structure coordinates are relative to the same origin.

### Yard (top-level document)

```
Yard
├── id
├── name
├── boundary            → polygon (feet) — property boundary
├── orientation         → compass bearing of "front" / north arrow
├── origin_description  → free text ("NW corner of lot")
├── areas[]             → all ground-level zones
└── structures[]        → vertical/above-ground objects
```

### Areas

An **area** is any ground-level zone in the yard. A single `type` discriminator distinguishes different kinds.

```
Area
├── id
├── name                → e.g. "Front Foundation Bed", "Back Patio"
├── type                → enum (see table below)
├── shape               → polygon coordinates (feet)
├── sun_exposure        → full_sun | partial_sun | shade
├── notes               → free text
└── plantings[]         → list of plant placements (plantable types only)
```

**Area types:**

| Type | Plantable? | Description |
|------|-----------|-------------|
| `flower_bed` | ✅ | Annuals, perennials, ground covers |
| `shrub_bed` | ✅ | Shrubs and hedges |
| `tree_area` | ✅ | Trees (canopy footprint) |
| `garden` | ✅ | Vegetable/herb garden |
| `lawn` | ❌ | Grass/turf areas |
| `rock_gravel` | ❌ | Decorative rock, gravel, xeriscaping |
| `patio` | ❌ | Paved/flagstone seating area |
| `walkway` | ❌ | Paths, stepping stones |
| `driveway` | ❌ | Vehicle access |
| `water_feature` | ❌ | Pond, fountain, dry river bed |
| `utility` | ❌ | AC units, meter boxes, septic access |
| `other` | configurable | Catch-all |

### Structures

**Structures** are vertical built objects that rise above the ground plane and act as constraints/boundaries that areas are arranged around. They are reference objects — you don't plant in them and they rarely change between proposals.

```
Structure
├── id
├── name                → "House", "Shed", "Fence - south"
├── type                → house | shed | fence | pergola | trellis | retaining_wall | utility_box | other
├── footprint           → polygon (feet)
└── notes
```

### Plantings (within an area)

```
Planting
├── id
├── plant_id            → reference to plant database entry
├── position            → coordinate (feet) — center of plant within the yard
├── quantity            → int (for mass plantings)
├── date_planted        → date or null (for proposals)
└── notes
```

### Plants (database)

Track: common name, botanical name, perennial/annual, bloom time, mature size, color, companion plants, care notes.

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

## 6b. Proposal model

A **proposal** represents a planned set of changes to the current yard layout. It captures a frozen baseline so users can always see before/after.

### Proposal structure

```
Proposal
├── id
├── name                → "Add back patio + surrounding beds"
├── description         → free text
├── state               → draft | accepted | implemented
├── created_at
├── updated_at
├── baseline_snapshot   → full yard state at time of proposal creation (frozen)
├── changes[]           → list of change operations
├── versions[]          → saved draft versions (manual save points)
├── cost
│   ├── proposed        → decimal (estimated cost at proposal time)
│   ├── actual          → decimal (filled in after implementation)
│   └── notes           → free text ("contractor quoted $X for labor")
└── metadata            → tags, contractor name, etc.
```

### Change operations

Each entry in `changes[]` describes one modification to the yard:

```
Change
├── id
├── action              → add | remove | modify | move
├── target_type         → area | structure | planting
├── target_id           → id of existing item (for remove/modify/move) or null (for add)
├── before              → snapshot of target before change (auto-captured from baseline)
├── after               → desired state of target after change
└── notes
```

- **Before view** = `baseline_snapshot` (always available, frozen at creation)
- **After view** = `baseline_snapshot` + apply `changes[]` in order
- **Diff view** = highlight what changed between baseline and result

### Draft versioning

```
Version
├── version_number      → 1, 2, 3...
├── saved_at
├── changes[]           → the change-set as it existed at this save point
├── cost_proposed       → cost estimate at this version
└── label               → optional ("v1 - just patio", "v2 - added beds")
```

Multiple versions are saved while in `draft` state. When a proposal moves to `accepted`, the final version becomes canonical.

### State transitions

```
draft → accepted → implemented
  ↑        |
  └────────┘  (can revert to draft if plans change)
```

- **draft** — editable, multiple versions can be saved
- **accepted** — locked, `cost.proposed` is finalized, handed to contractor
- **implemented** — done, `cost.actual` filled in

### Composition

Proposals are **independent** — no composition or layering of proposals in v1.

---

## 6c. API surface

| Resource | Operations | Notes |
|----------|-----------|-------|
| `GET/POST /yards` | List, create | Top-level resource |
| `GET/PUT/DELETE /yards/{id}` | Read, update, delete | Includes origin, boundary |
| `GET/POST /yards/{id}/areas` | List, create | Ground-level zones |
| `GET/PUT/DELETE /yards/{id}/areas/{id}` | Read, update, delete | |
| `GET/POST /yards/{id}/structures` | List, create | Vertical objects |
| `GET/PUT/DELETE /yards/{id}/structures/{id}` | Read, update, delete | |
| `GET/POST /yards/{id}/areas/{id}/plantings` | List, create | Plants placed in an area |
| `GET/PUT/DELETE .../plantings/{id}` | Read, update, delete | |
| `GET /plants` | List, search | Plant database |
| `POST /plants` | Create custom entry | User-added plants |
| `GET/POST /yards/{id}/proposals` | List, create | Auto-captures baseline on create |
| `GET/PUT /yards/{id}/proposals/{id}` | Read, update changes | Update only in draft state |
| `PATCH /yards/{id}/proposals/{id}/state` | Transition state | draft→accepted→implemented |
| `GET/POST /yards/{id}/proposals/{id}/versions` | List, save version | Draft save points |
| `GET /yards/{id}/proposals/{id}/render` | Render "after" view | Baseline + changes applied |
| `GET /yards/{id}/proposals/{id}/diff` | Visual diff | Before vs. after |
| `POST /ai/query` | AI query | Plant suggestions, critique, schedule, NL queries |

---

## 6d. Visualization

### Canvas library: **Fabric.js** (recommended)

Fabric.js is recommended for v1 because:
- Built-in polygon drawing and editing (required for freeform beds)
- Drag/drop object manipulation out of the box
- Native JSON serialization maps directly to the data model
- Mature, well-documented, large community
- Closest to a "design tool" experience

Alternatives considered:
- **Konva.js** — good layer system but polygon editing is manual
- **SVG + vanilla JS** — simpler but requires building all interaction from scratch
- **Leaflet.js** — overkill (designed for geo maps), but useful if aerial photo overlay is added later

### Seasonal / year toggle

**Tabs or dropdown** for v1 (e.g. "Spring 2026 | Summer 2026 | Fall 2026"). A timeline slider or animation playback can be added when dynamic growth simulation is implemented.

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
| Visualisation | Fabric.js (interactive HTML5 canvas) |
