# Gardenbot – Design Questions

Work through these questions to produce the design specification for the gardenbot application.
Fill in answers directly below each question (or create a linked discussion/issue).
Once a section is fully answered, summarise it in `docs/design_spec.md`.

---

## 1. Users and personas

1. Who are the primary users of gardenbot? (homeowner, professional landscaper, hobbyist, etc.)
   > **Answer:** Homeowner. The tool's output (plans, visualizations, schedules) is handed off to a professional landscaper for implementation.

2. What is the assumed technical skill level of the user when running the tool?
   > **Answer:** Comfortable in a terminal. A UI option is also desired for quick visualization.

3. Will there be multiple users / profiles on a single installation, or is it always a single-user tool?
   > **Answer:** Start with a single user. Design should allow expansion to multiple users/profiles later.

4. Does the user need to manage multiple separate properties/gardens, or just one?
   > **Answer:** Start with a single property. May extend to multiple properties later; separate properties are independent (no relationship between them required).

---

## 2. Interface and interaction

5. What is the primary interface? (CLI, web UI, desktop GUI, chat-based REPL, or a combination?)
   > **Answer:** Web-based UI is the default (deployed on an Ubuntu server with Docker + DNS/SSL). CLI is an optional secondary interface.

6. If CLI: should it be an interactive session or a command-per-invocation tool?
   > **Answer:** Interactive session (REPL-style).

7. If a web or desktop UI: what framework are you open to? (Flask/FastAPI + React, Streamlit, Tkinter, etc.)
   > **Answer:** Open to suggestions; lots of general coding experience but limited front-end experience. Recommendation: **FastAPI backend + HTMX or a lightweight JS framework** (avoids heavy React complexity while staying web-native). Streamlit is an alternative if rapid prototyping is prioritised.

8. Should the AI assistant (Ollama) feel like a chat companion, or should it be invoked only on specific commands?
   > **Answer:** Invoked on demand (specific commands/actions). A chat/conversation mode is a nice-to-have but not the default.

9. What should the output of a "flower bed visualization" look like — ASCII art in a terminal, a rendered image file, an interactive HTML page, or something else?
   > **Answer:** Interactive HTML page (rendered in the web UI).

---

## 3. Garden data model

> ✅ **Resolved** — full data schema (yard → areas → plantings, structures, coordinate system) documented in `docs/design_spec.md` §3.

10. What information do you want to track per flower bed? (name, location/coordinates, shape, soil type, sun exposure, irrigation zone, notes…)
    > **Answer:** Track: name, location/coordinates, shape, sun exposure, notes. **No need for soil type or irrigation zone.** Scope extends beyond flower beds — the full-yard view should include trees, bushes, hardscape (patio, shed), and utilities so the visualization shows the entire property.

11. What information do you want to track per plant? (common name, botanical name, perennial/annual, bloom time, mature size, color, companion plants, care notes…)
    > **Answer:** Yes — track all of the above: common name, botanical name, perennial/annual, bloom time, mature size, color, companion plants, and care notes.

12. Should the tool come with a built-in plant database, let the user build one, or query an external source?
    > **Answer:** Open to recommendation. Clarification of options: (a) **built-in curated database** shipped with the app (no internet needed, works offline); (b) **user-built** — user enters every plant manually; (c) **external API** (e.g., Trefle, USDA PLANTS) queried at runtime. Recommended approach: ship a **small built-in starter database** of common plants, with the ability for the user to add custom entries; external API can be added later.

13. How many layout templates should ship with the MVP? Do you have specific shapes in mind (rectangle, crescent, island, raised bed, etc.)?
    > **Answer:** MVP needs: **two freeform/irregular areas adjacent to the house** (foundation beds) and **two rectangular areas** elsewhere in the yard. Templates: rectangle + freeform polygon are sufficient for v1.

14. How should beds be positioned relative to one another — free-form placement or a grid-aligned plot map?
    > **Answer:** Not sure yet. Recommendation: use a **scaled canvas with free-form placement** (drag/drop on the interactive HTML view), which is more natural for an irregular yard than a strict grid. A grid overlay can be offered as an optional snap-to-grid aid.

---

## 4. Multi-year visualization

15. What does "visualize over the years" mean in practice — show predicted plant sizes, bloom colors, die-back, spreading, or all of the above?
    > **Answer:** All of: **plant sizes, bloom times, die-back, and spreading** should be animated/shown across years.

16. How far into the future should the default visualization project? (3 years, 5 years, custom?)
    > **Answer:** **3 years** as the default projection window.

17. Should the growth model be rule-based (hardcoded spread rates), AI-generated (Ollama inference), user-supplied, or a mix?
    > **Answer:** Not sure yet. Recommendation: start with a **rule-based model** (hardcoded spread/growth rates per plant type stored in the plant database), with hooks for Ollama inference as an optional enhancement. User overrides should always be allowed.

18. Should the user be able to annotate past years with what actually happened, so the tool can compare plan vs. reality?
    > **Answer:** **Yes** — plan vs. reality comparison is a desired feature.

19. Does seasonal variation within a year matter? (spring bloom vs. summer peak vs. fall die-back)
    > **Answer:** **Yes, this is important.** The visualization should show seasonal states within each year (at minimum: spring / summer / fall).

---

## 5. AI / Ollama integration

20. Which Ollama model(s) do you plan to use? (llama3, mistral, gemma, etc.) Should the model be user-configurable?
    > **Answer:** **User-configurable.** At minimum a vision-capable model must be supported (e.g. llava or a multimodal variant) because image input is a required use case.

21. What specific tasks should Ollama handle? (plant suggestions, layout critique, care-schedule generation, natural language queries, all of the above?)
    > **Answer:** **All of the above** — plant suggestions, layout critique, care-schedule generation, and natural language queries.

22. Should the AI be able to explain its recommendations in plain English?
    > **Answer:** **Yes.**

23. What should happen when Ollama is not running or not installed — hard failure, graceful degradation, or a fallback mode?
    > **Answer:** Ollama will be installed on a local server. The tool should also support an **optional cloud API fallback** (e.g. OpenAI / Anthropic) so the user can choose between local and cloud inference.

24. Do you want to store conversation history per garden plan so the AI can remember prior context?
    > **Answer:** Individual working-session transcripts do **not** need to be persisted. However, the overall garden **state/plan should be updated** after each AI interaction so that the AI has current context in future sessions.

---

## 6. Data storage and persistence

25. Where should data be stored? (local files — JSON/YAML/SQLite, or a hosted database?)
    > **Answer:** Prefer a **Docker-based solution** for deployment; otherwise **JSON** files for local data storage.

26. Should garden plans be exportable and importable (e.g., share a plan with someone else)?
    > **Answer:** **Yes — bidirectional.** Export plans for implementation (e.g. hand off to a contractor). Import contractor bids to create or append to a **"proposal"** record on the plan.

27. Do you need cloud backup or sync across devices?
    > **Answer:** **No.** The tool is expected to be server-based; no cloud sync needed.

28. Should the tool support version history for a garden plan (undo/redo, snapshots by date)?
    > **Answer:** **Yes.**

---

## 7. Lawn management (beyond flower beds)

29. What lawn-specific features are in scope for v1? (mowing schedule, fertiliser calendar, watering reminders, weed tracking, pest/disease logging?)
    > **Answer:** **Yes — include the suggested features:** mowing schedule, fertiliser calendar, watering reminders, weed tracking, and pest/disease logging.

30. Should the tool integrate with weather data (local forecasts, historical frost dates, USDA hardiness zone)?
    > **Answer:** **Future enhancement** — not in scope for v1.

31. Should it support irrigation system management or just manual watering notes?
    > **Answer:** Drip lines are expected to be in place physically, but **no integration with the irrigation system** — manual watering notes only.

---

## 8. Notifications and scheduling

32. Should gardenbot generate a weekly/monthly care schedule or task list?
    > **Answer:** **Yes.**

33. How should reminders be delivered — in-app, email, push notification, or just a printed checklist?
    > **Answer:** **In-app to start.**

34. Should tasks be tied to calendar dates or to growth stages?
    > **Answer:** **As needed** — support both calendar-date and growth-stage-based tasks as appropriate.

---

## 9. MVP scope

35. Of all the capabilities discussed above, which **three** are absolutely required for a useful MVP?
    > **Answer:** 1) Define garden beds; 2) Visualize current state of the garden; 3) Support proposals/plans for landscaping changes.
36. Which capabilities are explicitly out of scope for v1?
    > **Answer:** Out of scope for v1: user logins/authentication, dynamic plant growth simulation. Static layouts are acceptable — no need to animate or model real-time changes.
37. What does "done" look like for the first working demo?
    > **Answer:** "Done" means: (1) a user can define their current garden layout; (2) the user can create multiple proposals representing changes to that layout; (3) the user can visualize any layout or proposal.

---

## 10. Non-functional requirements

38. Target OS / platform? (Linux, macOS, Windows, or cross-platform?)
    > **Answer:** Primary target is **Ubuntu Server with Docker**. Future hosting on AWS or GCP is possible; the application should be cloud-portable.

39. Any performance constraints? (max response time for AI queries, max beds/plants before it gets slow?)
    > **Answer:** AI inference runs against a **local Ollama instance running 8 B-parameter models**. Cloud API key support must also be available as an alternative. No hard latency SLA for v1, but the architecture should make it easy to swap inference backends.

40. Should the tool be packaged for easy install (pip, Docker, standalone binary)?
    > **Answer:** Both **pip** (Python package) and **Docker** (containerised deployment).

41. Are there any privacy requirements — should plant or location data ever leave the local machine?
    > **Answer:** **No special privacy requirements.** Garden/location data is not considered sensitive.

---

*Once all sections are answered, create `docs/design_spec.md` summarising the decisions.*
