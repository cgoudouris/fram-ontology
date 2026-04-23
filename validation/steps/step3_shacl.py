"""Step 3 — Structural conformance check using SHACL shapes."""
from __future__ import annotations

import os
import sys
import time

from . import StepResult, ValidationContext, banner


STEP_ID = 3
STEP_NAME = "SHACL Shape Validation"


def run(ctx: ValidationContext) -> StepResult:
    banner("STEP 3: SHACL SHAPE VALIDATION")

    from rdflib import Graph
    from pyshacl import validate

    data_graph = Graph()
    data_graph.parse(ctx.tbox_path, format="turtle")
    data_graph.parse(ctx.ttl_path, format="turtle")

    shapes_graph = Graph()
    shapes_graph.parse(ctx.shapes_path, format="turtle")

    print(f"  Data graph:   {len(data_graph)} triples")
    print(f"  Shapes graph: {len(shapes_graph)} triples")

    t0 = time.time()
    conforms, _, results_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
        meta_shacl=False,
        advanced=True,
        debug=False,
    )
    elapsed = time.time() - t0

    print(f"  Conforms: {conforms} ({elapsed:.2f}s)")
    if not conforms:
        print(f"  Violations:\n{results_text[:1000]}")

    status = "PASS" if conforms else "FAIL"
    print(f"  STEP 3 RESULT: {status}")
    return StepResult(
        STEP_ID,
        STEP_NAME,
        status,
        details={"conforms": bool(conforms), "elapsed_s": elapsed},
    )


def _cli() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m validation.steps.step3_shacl <model.ttl>")
        return 1
    ctx = ValidationContext(ttl_path=os.path.abspath(sys.argv[1]))
    res = run(ctx)
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
