"""Step 1 — Convert a JSON-LD model to Turtle using the local context."""
from __future__ import annotations

import json
import os
import sys

from . import StepResult, ValidationContext, banner


STEP_ID = 1
STEP_NAME = "JSON-LD to Turtle conversion"


def run(ctx: ValidationContext) -> StepResult:
    banner("STEP 1: JSON-LD -> TURTLE CONVERSION")

    if not ctx.jsonld_path:
        print("  SKIP: no JSON-LD input provided")
        return StepResult(STEP_ID, STEP_NAME, "SKIP")

    from rdflib import Graph
    from pyld import jsonld

    with open(ctx.jsonld_path) as f:
        model_data = json.load(f)
    with open(ctx.context_path) as f:
        local_context = json.load(f)

    model_data["@context"] = local_context["@context"]
    nquads = jsonld.to_rdf(model_data, {"format": "application/n-quads"})

    g = Graph()
    g.parse(data=nquads, format="nquads")

    ttl_out = ctx.jsonld_path.replace(".jsonld", ".ttl")
    if ttl_out == ctx.jsonld_path:
        ttl_out = ctx.jsonld_path + ".ttl"
    g.serialize(ttl_out, format="turtle")

    print(f"  Input:   {ctx.jsonld_path}")
    print(f"  Output:  {ttl_out}")
    print(f"  Triples: {len(g)}")
    print("  STEP 1 RESULT: PASS")
    return StepResult(
        STEP_ID,
        STEP_NAME,
        "PASS",
        details={"output": ttl_out, "triples": len(g)},
    )


def _cli() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m validation.steps.step1_jsonld_to_ttl <model.jsonld>")
        return 1
    ctx = ValidationContext(ttl_path="", jsonld_path=os.path.abspath(sys.argv[1]))
    res = run(ctx)
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
