"""
Step 4: Competency Question Validation with SPARQL
===================================================
Runs 6 competency questions (CQs) against the combined graph (TBox + ABox)
to verify that the ontology can answer fundamental questions about FRAM models.

Part of the FRAM Ontology Validation Benchmark (EP2).
"""

import os
import time
from rdflib import Graph, Namespace

FRAM = Namespace("https://flowfram.com/ontology/fram/")
SCHEMA = Namespace("https://schema.org/")

# Resolve paths relative to repository root
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
VALIDATION_DIR = os.path.dirname(__file__)

print("=" * 70)
print("STEP 4: COMPETENCY QUESTION VALIDATION WITH SPARQL")
print("=" * 70)

# ── 1. Load TBox + ABox ──
print("\n[1/2] Loading combined graph (TBox + ABox)...")
g = Graph()

tbox_path = os.path.join(REPO_ROOT, "fram.ttl")
abox_path = os.path.join(VALIDATION_DIR, "boil-water-model.ttl")

g.parse(tbox_path, format="turtle")
g.parse(abox_path, format="turtle")
g.bind("fram", FRAM)
g.bind("schema", SCHEMA)
print(f"      Total triples: {len(g)}")

# ── 2. Define and run the Competency Questions ──
print("\n[2/2] Running Competency Questions...\n")

competency_questions = [
    {
        "id": "CQ1",
        "question": "What are the model's functions and their types?",
        "expected": "3 functions: Fill kettle (human), Heat water (technological), Pour water (human)",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?funcName ?funcType WHERE {
                ?model a fram:FRAMModel ;
                       fram:hasFunction ?func .
                ?func schema:name ?funcName ;
                      fram:functionType ?funcType .
            }
            ORDER BY ?funcName
        """,
        "validate": lambda results: len(results) == 3
    },
    {
        "id": "CQ2",
        "question": "What are the couplings between functions?",
        "expected": "2 couplings: Fill->Heat and Heat->Pour",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?label ?srcName ?tgtName WHERE {
                ?model a fram:FRAMModel ;
                       fram:hasCoupling ?coupling .
                ?coupling rdfs:label ?label ;
                          fram:sourceFunction ?src ;
                          fram:targetFunction ?tgt .
                ?src schema:name ?srcName .
                ?tgt schema:name ?tgtName .
            }
            ORDER BY ?label
        """,
        "validate": lambda results: len(results) == 2
    },
    {
        "id": "CQ3",
        "question": "What aspects does the function 'Heat water to boiling' have?",
        "expected": "5 aspects: Input, Output, Resource, Control, Time",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?aspectName ?aspectType ?aspectCode WHERE {
                ?func schema:name "Heat water to boiling" ;
                      fram:hasAspect ?aspect .
                ?aspect schema:name ?aspectName ;
                        fram:aspectType ?aspectType ;
                        fram:aspectCode ?aspectCode .
            }
            ORDER BY ?aspectCode
        """,
        "validate": lambda results: len(results) == 5
    },
    {
        "id": "CQ4",
        "question": "What is the variability distribution of 'Heat water to boiling'?",
        "expected": "NormalDistribution with mean=4.0 and stdDev=0.5",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?distType ?mean ?stddev ?unit WHERE {
                ?func schema:name "Heat water to boiling" ;
                      fram:hasVariability ?var .
                ?var fram:hasDistribution ?dist .
                ?dist a ?distType ;
                      fram:distributionMean ?mean ;
                      fram:distributionStdDev ?stddev ;
                      fram:unit ?unit .
                FILTER(?distType != <http://www.w3.org/2002/07/owl#NamedIndividual>)
            }
        """,
        "validate": lambda results: len(results) >= 1
    },
    {
        "id": "CQ5",
        "question": "What are the variability phenotypes of 'Fill kettle with water'?",
        "expected": "2 phenotypes: TimingPhenotypeClass (on-time, 0.85) and PrecisionPhenotypeClass (acceptable, 0.90)",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT ?phenoType ?value ?prob WHERE {
                ?func schema:name "Fill kettle with water" ;
                      fram:hasVariability ?var .
                ?var fram:hasPhenotype ?pheno .
                ?pheno a ?phenoType ;
                       fram:phenotypeValue ?value ;
                       fram:phenotypeProbability ?prob .
                FILTER(?phenoType != <http://www.w3.org/2002/07/owl#NamedIndividual>)
            }
            ORDER BY ?phenoType
        """,
        "validate": lambda results: len(results) == 2
    },
    {
        "id": "CQ6",
        "question": "Which functions receive input from other functions via couplings?",
        "expected": "2 functions: Heat water to boiling and Pour boiling water",
        "sparql": """
            PREFIX fram: <https://flowfram.com/ontology/fram/>
            PREFIX schema: <https://schema.org/>
            SELECT DISTINCT ?tgtName WHERE {
                ?model a fram:FRAMModel ;
                       fram:hasCoupling ?coupling .
                ?coupling fram:targetFunction ?tgt .
                ?tgt schema:name ?tgtName .
            }
            ORDER BY ?tgtName
        """,
        "validate": lambda results: len(results) == 2
    }
]

all_pass = True
results_summary = []

for cq in competency_questions:
    print(f"--- {cq['id']}: {cq['question']} ---")
    print(f"    Expected: {cq['expected']}")

    start = time.time()
    qres = g.query(cq["sparql"])
    elapsed = time.time() - start

    results = list(qres)
    passed = cq["validate"](results)

    if not passed:
        all_pass = False

    status = "PASS ✅" if passed else "FAIL ❌"
    print(f"    Result: {len(results)} record(s) returned [{elapsed*1000:.1f}ms]")

    for row in results:
        values = [str(v) for v in row]
        print(f"      -> {' | '.join(values)}")

    print(f"    Status: {status}\n")
    results_summary.append({
        "id": cq["id"],
        "question": cq["question"],
        "expected": cq["expected"],
        "actual_count": len(results),
        "passed": passed,
        "time_ms": elapsed * 1000
    })

# ── 3. Summary ──
print("=" * 70)
print("STEP 4 SUMMARY")
print("=" * 70)
print(f"  Competency Questions:   {len(competency_questions)}")
print(f"  Passed:                 {sum(1 for r in results_summary if r['passed'])}")
print(f"  Failed:                 {sum(1 for r in results_summary if not r['passed'])}")
print(f"  Overall Result:         {'PASS ✅' if all_pass else 'FAIL ❌'}")

print("\n  Details:")
for r in results_summary:
    status = "PASS" if r["passed"] else "FAIL"
    print(f"    {r['id']}: {status} ({r['actual_count']} results, {r['time_ms']:.1f}ms)")
