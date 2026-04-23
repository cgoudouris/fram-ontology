"""Step 4 — Domain coverage check using SPARQL competency questions."""
from __future__ import annotations

import os
import sys

from . import StepResult, ValidationContext, banner


STEP_ID = 4
STEP_NAME = "SPARQL Competency Questions"


COMPETENCY_QUESTIONS = [
    {
        "id": "CQ1",
        "question": "What are the model's functions and their types?",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?funcName ?funcType WHERE {
                ?model a fram:FRAMModel ;
                       fram:hasFunction ?func .
                ?func schema:name ?funcName ;
                      fram:functionType ?funcType .
            } ORDER BY ?funcName
        """,
    },
    {
        "id": "CQ2",
        "question": "What are the couplings between functions?",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?srcName ?tgtName WHERE {
                ?model a fram:FRAMModel ;
                       fram:hasCoupling ?coupling .
                ?coupling fram:sourceFunction ?src ;
                          fram:targetFunction ?tgt .
                ?src schema:name ?srcName .
                ?tgt schema:name ?tgtName .
            } ORDER BY ?srcName
        """,
    },
    {
        "id": "CQ3",
        "question": "How many aspects does each function have?",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?funcName (COUNT(DISTINCT ?aspect) AS ?aspectCount) WHERE {
                ?func a fram:Function ;
                      schema:name ?funcName ;
                      fram:hasAspect ?aspect .
            } GROUP BY ?funcName ORDER BY ?funcName
        """,
    },
    {
        "id": "CQ4",
        "question": "Which functions have variability metadata?",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?funcName ?potential WHERE {
                ?func a fram:Function ;
                      schema:name ?funcName ;
                      fram:hasVariability ?var .
                ?var fram:variabilityPotential ?potential .
            } ORDER BY ?funcName
        """,
    },
    {
        "id": "CQ5",
        "question": "What are the variability phenotypes of the functions?",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?funcName ?timingPheno ?precisionPheno WHERE {
                ?func a fram:Function ;
                      schema:name ?funcName ;
                      fram:hasVariability ?var .
                ?var fram:timingPhenotype ?timingPheno ;
                     fram:precisionPhenotype ?precisionPheno .
            } ORDER BY ?funcName
        """,
    },
    {
        "id": "CQ6",
        "question": "Which functions receive input from other functions via couplings?",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT DISTINCT ?tgtName WHERE {
                ?model a fram:FRAMModel ;
                       fram:hasCoupling ?coupling .
                ?coupling fram:targetFunction ?tgt .
                ?tgt schema:name ?tgtName .
            } ORDER BY ?tgtName
        """,
    },
]


def run(ctx: ValidationContext) -> StepResult:
    banner("STEP 4: SPARQL COMPETENCY QUESTIONS")

    from rdflib import Graph

    g = Graph()
    g.parse(ctx.tbox_path, format="turtle")
    g.parse(ctx.ttl_path, format="turtle")

    all_pass = True
    counts = {}
    for cq in COMPETENCY_QUESTIONS:
        results = list(g.query(cq["sparql"]))
        passed = len(results) >= 1
        counts[cq["id"]] = len(results)
        if not passed:
            all_pass = False
        print(f"  {cq['id']}: {cq['question']}")
        print(f"       {len(results)} results -> {'PASS' if passed else 'FAIL'}")

    status = "PASS" if all_pass else "FAIL"
    print(f"  STEP 4 RESULT: {status} ({len(COMPETENCY_QUESTIONS)} CQs)")
    return StepResult(
        STEP_ID,
        STEP_NAME,
        status,
        details={"counts": counts, "total": len(COMPETENCY_QUESTIONS)},
    )


def _cli() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m validation.steps.step4_competency <model.ttl>")
        return 1
    ctx = ValidationContext(ttl_path=os.path.abspath(sys.argv[1]))
    res = run(ctx)
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
