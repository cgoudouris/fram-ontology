"""Step 2 — Logical consistency check using an OWL-RL reasoner."""
from __future__ import annotations

import os
import sys
import time

from . import StepResult, ValidationContext, banner


STEP_ID = 2
STEP_NAME = "OWL-RL Reasoning"


def run(ctx: ValidationContext) -> StepResult:
    banner("STEP 2: OWL-RL REASONING")

    from rdflib import Graph, RDF, OWL, RDFS
    import owlrl

    g = Graph()
    g.parse(ctx.tbox_path, format="turtle")
    tbox_count = len(g)
    g.parse(ctx.ttl_path, format="turtle")
    abox_count = len(g) - tbox_count
    total_before = len(g)

    print(f"  TBox: {tbox_count} triples")
    print(f"  ABox: {abox_count} triples")
    print(f"  Total before reasoning: {total_before}")

    t0 = time.time()
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    elapsed = time.time() - t0
    total_after = len(g)
    inferred = total_after - total_before

    nothing_instances = list(g.subjects(RDF.type, OWL.Nothing))
    unsatisfiable = [
        c for c in g.subjects(RDF.type, OWL.Class)
        if (c, RDFS.subClassOf, OWL.Nothing) in g and c != OWL.Nothing
    ]

    print(f"  Total after reasoning: {total_after}")
    print(f"  Inferred triples: {inferred} ({elapsed:.2f}s)")
    print(f"  owl:Nothing instances: {len(nothing_instances)}")
    print(f"  Unsatisfiable classes: {len(unsatisfiable)}")

    passed = not nothing_instances and not unsatisfiable
    status = "PASS" if passed else "FAIL"
    print(f"  STEP 2 RESULT: {status}")

    return StepResult(
        STEP_ID,
        STEP_NAME,
        status,
        details={
            "tbox": tbox_count,
            "abox": abox_count,
            "inferred": inferred,
            "elapsed_s": elapsed,
            "owl_nothing": len(nothing_instances),
            "unsatisfiable_classes": len(unsatisfiable),
        },
    )


def _cli() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m validation.steps.step2_reasoning <model.ttl>")
        return 1
    ctx = ValidationContext(ttl_path=os.path.abspath(sys.argv[1]))
    res = run(ctx)
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
