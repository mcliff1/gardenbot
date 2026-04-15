# Gardenbot – Design Questions

Work through these questions to produce the design specification for the gardenbot application.
Fill in answers directly below each question (or create a linked discussion/issue).
Once a section is fully answered, summarise it in `docs/design_spec.md`.

---

## 1. Users and personas

1. Who are the primary users of gardenbot? (homeowner, professional landscaper, hobbyist, etc.)
2. What is the assumed technical skill level of the user when running the tool?
3. Will there be multiple users / profiles on a single installation, or is it always a single-user tool?
4. Does the user need to manage multiple separate properties/gardens, or just one?

---

## 2. Interface and interaction

5. What is the primary interface? (CLI, web UI, desktop GUI, chat-based REPL, or a combination?)
6. If CLI: should it be an interactive session or a command-per-invocation tool?
7. If a web or desktop UI: what framework are you open to? (Flask/FastAPI + React, Streamlit, Tkinter, etc.)
8. Should the AI assistant (Ollama) feel like a chat companion, or should it be invoked only on specific commands?
9. What should the output of a "flower bed visualization" look like — ASCII art in a terminal, a rendered image file, an interactive HTML page, or something else?

---

## 3. Garden data model

10. What information do you want to track per flower bed? (name, location/coordinates, shape, soil type, sun exposure, irrigation zone, notes…)
11. What information do you want to track per plant? (common name, botanical name, perennial/annual, bloom time, mature size, color, companion plants, care notes…)
12. Should the tool come with a built-in plant database, let the user build one, or query an external source?
13. How many layout templates should ship with the MVP? Do you have specific shapes in mind (rectangle, crescent, island, raised bed, etc.)?
14. How should beds be positioned relative to one another — free-form placement or a grid-aligned plot map?

---

## 4. Multi-year visualization

15. What does "visualize over the years" mean in practice — show predicted plant sizes, bloom colors, die-back, spreading, or all of the above?
16. How far into the future should the default visualization project? (3 years, 5 years, custom?)
17. Should the growth model be rule-based (hardcoded spread rates), AI-generated (Ollama inference), user-supplied, or a mix?
18. Should the user be able to annotate past years with what actually happened, so the tool can compare plan vs. reality?
19. Does seasonal variation within a year matter? (spring bloom vs. summer peak vs. fall die-back)

---

## 5. AI / Ollama integration

20. Which Ollama model(s) do you plan to use? (llama3, mistral, gemma, etc.) Should the model be user-configurable?
21. What specific tasks should Ollama handle? (plant suggestions, layout critique, care-schedule generation, natural language queries, all of the above?)
22. Should the AI be able to explain its recommendations in plain English?
23. What should happen when Ollama is not running or not installed — hard failure, graceful degradation, or a fallback mode?
24. Do you want to store conversation history per garden plan so the AI can remember prior context?

---

## 6. Data storage and persistence

25. Where should data be stored? (local files — JSON/YAML/SQLite, or a hosted database?)
26. Should garden plans be exportable and importable (e.g., share a plan with someone else)?
27. Do you need cloud backup or sync across devices?
28. Should the tool support version history for a garden plan (undo/redo, snapshots by date)?

---

## 7. Lawn management (beyond flower beds)

29. What lawn-specific features are in scope for v1? (mowing schedule, fertiliser calendar, watering reminders, weed tracking, pest/disease logging?)
30. Should the tool integrate with weather data (local forecasts, historical frost dates, USDA hardiness zone)?
31. Should it support irrigation system management or just manual watering notes?

---

## 8. Notifications and scheduling

32. Should gardenbot generate a weekly/monthly care schedule or task list?
33. How should reminders be delivered — in-app, email, push notification, or just a printed checklist?
34. Should tasks be tied to calendar dates or to growth stages?

---

## 9. MVP scope

35. Of all the capabilities discussed above, which **three** are absolutely required for a useful MVP?
36. Which capabilities are explicitly out of scope for v1?
37. What does "done" look like for the first working demo?

---

## 10. Non-functional requirements

38. Target OS / platform? (Linux, macOS, Windows, or cross-platform?)
39. Any performance constraints? (max response time for AI queries, max beds/plants before it gets slow?)
40. Should the tool be packaged for easy install (pip, Docker, standalone binary)?
41. Are there any privacy requirements — should plant or location data ever leave the local machine?

---

*Once all sections are answered, create `docs/design_spec.md` summarising the decisions.*
