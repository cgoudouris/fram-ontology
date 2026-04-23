"""
FRAM Ontology Validation Steps
==============================

Each step is implemented as an independent module under this package.
A step exposes:

    def run(ctx: ValidationContext) -> StepResult

and a ``__main__`` entry point so the step can be executed standalone:

    python -m validation.steps.step3_shacl <model.ttl>

The orchestrator ``validate_fram_model.py`` imports and invokes the
``run`` function of each requested step in sequence. There is no
``subprocess`` indirection between the orchestrator and the steps.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TBOX_PATH = os.path.join(REPO_ROOT, "fram.ttl")
SHAPES_PATH = os.path.join(REPO_ROOT, "fram-shapes.ttl")
CONTEXT_PATH = os.path.join(REPO_ROOT, "context.jsonld")


# ---------------------------------------------------------------------------
# Shared types
# ---------------------------------------------------------------------------
@dataclass
class ValidationContext:
    """All paths and shared configuration needed by a step."""
    ttl_path: str
    jsonld_path: Optional[str] = None
    tbox_path: str = TBOX_PATH
    shapes_path: str = SHAPES_PATH
    context_path: str = CONTEXT_PATH


@dataclass
class StepResult:
    """Outcome of a single validation step."""
    step_id: int
    name: str
    status: str  # "PASS" | "FAIL" | "SKIP" | "ERROR"
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


# ---------------------------------------------------------------------------
# Output helpers (kept small and dependency-free on purpose)
# ---------------------------------------------------------------------------
def banner(title: str, width: int = 70) -> None:
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def shorten(uri: str) -> str:
    """Compact common ontology IRIs for log readability."""
    return (
        str(uri)
        .replace("https://flowfram.com/models/", "model:")
        .replace("https://flowfram.com/ontology/fram/", "fram:")
        .replace("https://schema.org/", "schema:")
        .replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:")
        .replace("http://www.w3.org/2000/01/rdf-schema#", "rdfs:")
        .replace("http://www.w3.org/2002/07/owl#", "owl:")
        .replace("http://www.w3.org/2001/XMLSchema#", "xsd:")
    )
