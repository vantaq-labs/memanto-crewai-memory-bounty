#!/usr/bin/env python3
"""CrewAI + Memanto long-term memory demo.

The local JSON backend makes the demo runnable without API keys. The MemantoCliMemory
adapter shows the two calls needed to use the real Memanto CLI in CrewAI tasks.
"""
from __future__ import annotations
import argparse, json, subprocess, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

STORE = Path(__file__).resolve().parents[1] / "demo" / "memory_store.json"

@dataclass
class MemoryRecord:
    text: str
    type: str = "fact"
    source_agent: str = "agent"
    status: str = "current"
    created_at: float = 0.0

class LocalMemantoLikeMemory:
    """Tiny persistent memory with Memanto-like remember/recall semantics."""
    def __init__(self, path: Path = STORE):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def _load(self) -> list[dict]:
        return json.loads(self.path.read_text())

    def _save(self, rows: list[dict]) -> None:
        self.path.write_text(json.dumps(rows, indent=2, sort_keys=True))

    def remember(self, text: str, type: str = "fact", source_agent: str = "agent") -> None:
        rows = self._load()
        rows.append(asdict(MemoryRecord(text=text, type=type, source_agent=source_agent, created_at=time.time())))
        self._save(rows)

    def supersede_matching(self, needle: str) -> None:
        rows = self._load()
        for row in rows:
            if needle.lower() in row["text"].lower():
                row["status"] = "superseded"
        self._save(rows)

    def recall(self, query: str, type: str | None = None, current_only: bool = True) -> list[MemoryRecord]:
        terms = [t.lower() for t in query.replace("=", " ").split() if len(t) > 2]
        hits = []
        for row in self._load():
            if type and row["type"] != type:
                continue
            if current_only and row.get("status") != "current":
                continue
            hay = row["text"].lower()
            if any(t in hay for t in terms):
                hits.append(MemoryRecord(**row))
        return hits

class MemantoCliMemory:
    """Adapter for real Memanto CLI usage inside CrewAI tasks/tools."""
    def __init__(self, agent: str = "crewai-bounty-demo"):
        self.agent = agent

    def remember(self, text: str, type: str = "fact", source_agent: str = "agent") -> None:
        subprocess.run(["memanto", "remember", text, "--type", type], check=True)

    def recall(self, query: str, type: str | None = None) -> list[str]:
        cmd = ["memanto", "recall", query]
        if type:
            cmd += ["--type", type]
        out = subprocess.check_output(cmd, text=True)
        return [line for line in out.splitlines() if line.strip()]

class ResearchAgent:
    name = "Research Agent"
    def run(self, memory: LocalMemantoLikeMemory) -> None:
        memory.remember("target audience=Python AI builders", type="fact", source_agent=self.name)
        memory.remember("tone=concise technical", type="preference", source_agent=self.name)
        memory.remember("publish channel=README tutorial", type="fact", source_agent=self.name)
        print("Research Agent stored 3 durable memories")

class WriterAgent:
    name = "Writer Agent"
    def run(self, memory: LocalMemantoLikeMemory) -> None:
        facts = memory.recall("target audience tone publish channel", current_only=True)
        summary = "; ".join(r.text for r in facts)
        print(f"Writer Agent recalled: {summary}")
        print("Draft: A concise README tutorial for Python AI builders using durable Memanto memory.")

class ContradictionAgent:
    name = "Contradiction Resolver"
    def run(self, memory: LocalMemantoLikeMemory) -> None:
        memory.supersede_matching("tone=")
        memory.remember("tone=step-by-step beginner friendly", type="preference", source_agent=self.name)
        current = memory.recall("tone", type="preference")
        print("Current tone memory:", "; ".join(r.text for r in current))

def main(argv: Iterable[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["research", "writer", "contradiction", "all"], default="all")
    ap.add_argument("--reset", action="store_true")
    ns = ap.parse_args(argv)
    if ns.reset and STORE.exists():
        STORE.unlink()
    memory = LocalMemantoLikeMemory()
    phases = [ns.phase] if ns.phase != "all" else ["research", "writer", "contradiction"]
    for phase in phases:
        {"research": ResearchAgent, "writer": WriterAgent, "contradiction": ContradictionAgent}[phase]().run(memory)

if __name__ == "__main__":
    main()
