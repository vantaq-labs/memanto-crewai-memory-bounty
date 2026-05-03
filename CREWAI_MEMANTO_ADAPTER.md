# CrewAI + Memanto adapter notes

This note maps the runnable demo to a production CrewAI integration for the bounty reviewer.

## Integration shape

- Keep CrewAI agents/tasks unchanged.
- Inject a small memory object into tools or task callbacks.
- Use `remember(text, type, source_agent)` after a task produces durable facts, preferences, or decisions.
- Use `recall(query, type)` before a later task drafts or decides, so independent runs can recover prior context.

## Suggested taxonomy

- `fact`: project facts, extracted requirements, user constraints.
- `preference`: writing tone, formatting, recurring user choices.
- `decision`: prior agent decisions and rationale.
- metadata: `crew_id`, `agent_id`, `task_id`, `session_id`, `source_agent`.

## Contradictions

The local demo implements `supersede_matching()` to mark stale rows as `superseded` and recalls only `current` rows by default. With Memanto/Moorcheh, the same policy should be implemented as an upsert/versioning layer: keep history for auditability, but only inject current memories into active CrewAI context.

## Review commands

```bash
python3 src/crewai_memanto_demo.py --reset
python3 src/crewai_memanto_demo.py --phase research
python3 src/crewai_memanto_demo.py --phase writer
python3 src/crewai_memanto_demo.py --phase contradiction
```

Expected proof: the Writer Agent recalls facts stored by the Research Agent in a previous process, then the contradiction resolver replaces the stale tone preference.
