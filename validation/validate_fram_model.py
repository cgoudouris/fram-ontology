#!/usr/bin/env python3
"""
FRAM Ontology Validation Runner
================================
Thin orchestrator for the 8-step validation benchmark.

Each step lives in its own module under ``validation/steps/`` and
exposes ``run(ctx) -> StepResult``. This file selects the requested
steps, builds a shared :class:`ValidationContext`, invokes each step
in order, and prints a summary.

Usage:
    python validate_fram_model.py <model_ttl> [model_jsonld] [options]
    python -m validation.validate_fram_model <model_ttl> [model_jsonld] [options]

Examples:
    # Steps 2-4 (TBox-only validation against a TTL model)
    python validate_fram_model.py examples/eac1-li-huang-2025.ttl

    # Full 8-step pipeline (offline, skipping OOPS!)
    python validate_fram_model.py \\
        examples/eac1-li-huang-2025.ttl \\
        examples/eac1-li-huang-2025.jsonld \\
        --skip-oops

    # Run only specific steps
    python validate_fram_model.py model.ttl model.jsonld --steps 2,3,4,8

Each step can also be executed standalone for debugging:
    python -m validation.steps.step3_shacl examples/eac1-li-huang-2025.ttl

Part of the FRAM Ontology Validation Benchmark (EP2 of the FRAM thesis).
"""
from __future__ import annotations

import argparse
import os
import sys


# Allow direct script execution by ensuring the repo root is on sys.path.
if __package__ in (None, ""):
    _REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if _REPO_ROOT not in sys.path:
        sys.path.insert(0, _REPO_ROOT)

from validation.steps import (  # noqa: E402
    CONTEXT_PATH,
    SHAPES_PATH,
    TBOX_PATH,
    StepResult,
    ValidationContext,
    banner,
)
from validation.steps import (  # noqa: E402
    step1_jsonld_to_ttl,
    step2_reasoning,
    step3_shacl,
    step4_competency,
    step5_oops,
    step6_roundtrip,
    step7_gap_analysis,
    step8_sparql_equivalence,
)


STEP_REGISTRY = {
    1: step1_jsonld_to_ttl,
    2: step2_reasoning,
    3: step3_shacl,
    4: step4_competency,
    5: step5_oops,
    6: step6_roundtrip,
    7: step7_gap_analysis,
    8: step8_sparql_equivalence,
}


def _resolve(path: str | None) -> str | None:
    if path is None:
        return None
    if os.path.isabs(path):
        return path
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(repo_root, path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="FRAM Ontology Validation Runner (8-step benchmark)"
    )
    parser.add_argument("model_ttl", help="Path to the TTL model file")
    parser.add_argument(
        "model_jsonld", nargs="?", default=None,
        help="Path to the JSON-LD model file (enables Steps 6-8)",
    )
    parser.add_argument(
        "--skip-oops", action="store_true",
        help="Skip Step 5 (OOPS! API requires internet)",
    )
    parser.add_argument(
        "--steps", type=str, default=None,
        help="Comma-separated list of steps to run (e.g. '2,3,4,8')",
    )
    args = parser.parse_args()

    ttl_path = _resolve(args.model_ttl)
    jsonld_path = _resolve(args.model_jsonld)

    if not os.path.isfile(ttl_path):
        print(f"Error: TTL file not found: {ttl_path}", file=sys.stderr)
        return 1
    if jsonld_path and not os.path.isfile(jsonld_path):
        print(f"Error: JSON-LD file not found: {jsonld_path}", file=sys.stderr)
        return 1

    if args.steps:
        selected = {int(s) for s in args.steps.split(",")}
    else:
        selected = {2, 3, 4, 5, 6, 7, 8}

    if args.skip_oops:
        selected.discard(5)
    if not jsonld_path:
        selected -= {1, 6, 7, 8}

    ctx = ValidationContext(
        ttl_path=ttl_path,
        jsonld_path=jsonld_path,
        tbox_path=TBOX_PATH,
        shapes_path=SHAPES_PATH,
        context_path=CONTEXT_PATH,
    )

    banner("FRAM ONTOLOGY VALIDATION BENCHMARK")
    print(f"  TBox:     {TBOX_PATH}")
    print(f"  ABox TTL: {ttl_path}")
    if jsonld_path:
        print(f"  ABox JLD: {jsonld_path}")
    print(f"  Context:  {CONTEXT_PATH}")
    print(f"  Shapes:   {SHAPES_PATH}")
    print(f"  Steps:    {sorted(selected)}")

    results: dict[int, StepResult] = {}
    for step_id in sorted(selected):
        module = STEP_REGISTRY[step_id]
        results[step_id] = module.run(ctx)

    # ── Summary ──
    banner("VALIDATION SUMMARY")
    all_pass = True
    failing = []
    for step_id in sorted(results):
        res = results[step_id]
        status = res.status
        if status == "FAIL" or status == "ERROR":
            all_pass = False
            failing.append(step_id)
        print(f"  Step {step_id} ({res.name}): {status}")

    print()
    if all_pass:
        print("  OVERALL: PASS")
        return 0
    print(f"  OVERALL: FAIL (steps {failing})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
