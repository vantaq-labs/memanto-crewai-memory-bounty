# CrewAI + Memanto Long-Term Memory Demo

Bounty submission for moorcheh-ai/memanto#37.

This repo shows a small multi-agent CrewAI-style workflow where a **Research Agent** stores durable project facts in Memanto-compatible memory and a later **Writer Agent** recalls them in a separate run. It also demonstrates contradiction handling: a stale preference is superseded by a newer fact.

## What this demonstrates

- Research output survives across process runs.
- A second agent can retrieve context written by the first agent.
- Old facts can be marked as superseded and filtered out.
- The code is safe to run without paid keys: it uses a local JSON store by default, and includes a `MemantoCliMemory` adapter showing how to swap the storage calls to `memanto remember` / `memanto recall` when a Moorcheh API key is configured.

## Quick start

```bash
python3 src/crewai_memanto_demo.py --reset
python3 src/crewai_memanto_demo.py --phase research
python3 src/crewai_memanto_demo.py --phase writer
python3 src/crewai_memanto_demo.py --phase contradiction
```

Expected writer output includes the remembered facts from a previous run:

```text
Writer Agent recalled: target audience=Python AI builders; tone=concise technical; publish channel=README tutorial
```

## Swap standard CrewAI memory for Memanto

1. Install and configure Memanto:

```bash
pip install memanto
memanto  # prompts for Moorcheh API key
memanto agent create crewai-bounty-demo
```

2. Replace the demo memory backend:

```python
from crewai_memanto_demo import MemantoCliMemory
memory = MemantoCliMemory(agent="crewai-bounty-demo")
```

3. Store and recall through the adapter from each CrewAI task/tool instead of relying only on in-process CrewAI memory. The demo keeps the calls narrow:

```python
memory.remember("target audience=Python AI builders", type="fact", source_agent="Research Agent")
results = memory.recall("target audience", type="fact")
```

## Visual proof

A terminal transcript is in [`demo/terminal-proof.txt`](demo/terminal-proof.txt). It shows reset -> research run -> writer run -> contradiction update/retrieval.

## Notes

- `crewai` integration is represented by small `Agent`/`Task` wrappers when the package is not installed, so reviewers can run the memory proof immediately. If CrewAI is installed, the same memory adapter can be called from CrewAI tools/tasks.
- No wallet, seed phrase, payment, or private credential is used.
