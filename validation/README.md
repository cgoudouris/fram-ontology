# FRAM Ontology Validation Benchmark

An eight-step automated validation benchmark for the [FRAM Ontology](../fram.ttl), based on the **Preliminary Study 2 (EP2)** conducted as part of a Design Science Research (DSR) thesis.

## Overview

This benchmark verifies the FRAM Ontology across eight complementary dimensions:

| Step | Technique | Tool | What it validates |
|------|-----------|------|-------------------|
| 1 | JSON-LD → Turtle conversion | pyld + rdflib | Context resolution, IRI expansion, serialization integrity |
| 2 | OWL-RL Reasoning | owlrl | Logical consistency, unsatisfiable classes, inferred triples |
| 3 | SHACL Shape Validation | pyshacl | Structural constraints via 8 custom shapes |
| 4 | SPARQL Competency Questions | rdflib | 6 CQs covering functions, couplings, aspects, variability, phenotypes |
| 5 | OOPS! Pitfall Scanning | OOPS! REST API | Common ontology design anti-patterns |
| 6 | Round-trip Fidelity | rdflib isomorphism | TTL ↔ JSON-LD serialization round-trip integrity |
| 7 | Gap Analysis | rdflib + pyld | Predicate-level differences between serializations |
| 8 | SPARQL Semantic Equivalence | rdflib SPARQL | Gold-standard query equivalence (10 queries) |

## Prerequisites

**Python 3.10+** with the following packages:

```bash
pip install rdflib pyld owlrl pyshacl requests
```

## Architecture

The benchmark follows a **modular architecture**: each of the eight steps is implemented as an independent Python module under `validation/steps/`, and a thin orchestrator (`validate_fram_model.py`) selects, configures and invokes them in order. There is no `subprocess` indirection — every step is invoked through a direct `module.run(ctx)` call against a shared `ValidationContext`.

Benefits:

- **No silent failures** — a missing step module raises `ImportError` at orchestrator startup instead of being silently skipped.
- **Standalone debugging** — each step is also a CLI: `python -m validation.steps.stepN_<name> <args>`.
- **Unit-testable** — every step exposes the same `run(ctx) -> StepResult` contract and can be imported into a test harness.
- **Zero subprocess overhead** — the Python interpreter is initialised once for the whole pipeline.

```
validation/
├── README.md                              # This file
├── __init__.py                            # Package marker
├── validate_fram_model.py                 # Thin orchestrator (~140 LOC)
├── fram_rdfxml.owl                        # RDF/XML conversion buffer (Step 5)
├── steps/                                 # 8 independent step modules
│   ├── __init__.py                        # Shared types: ValidationContext, StepResult
│   ├── step1_jsonld_to_ttl.py             # JSON-LD → Turtle conversion
│   ├── step2_reasoning.py                 # OWL-RL reasoning
│   ├── step3_shacl.py                     # SHACL shape validation
│   ├── step4_competency.py                # SPARQL competency questions
│   ├── step5_oops.py                      # OOPS! pitfall scanning
│   ├── step6_roundtrip.py                 # Round-trip fidelity (RT1–RT3)
│   ├── step7_gap_analysis.py              # Predicate-level gap report
│   └── step8_sparql_equivalence.py        # SPARQL semantic equivalence (10 SQs)
└── results/
    ├── experiment_log.md                  # Original experiment execution log
    └── oops_analysis.md                   # OOPS! pitfall analysis (v1.0 → v1.2.0)
```

Each step module exposes:

```python
from validation.steps import StepResult, ValidationContext

def run(ctx: ValidationContext) -> StepResult:
    ...
```

and can be invoked standalone for debugging:

```bash
python -m validation.steps.step3_shacl examples/eac1-li-huang-2025.ttl
python -m validation.steps.step6_roundtrip <model.ttl> <model.jsonld> [<context.jsonld>]
```

## Running the Full Benchmark

The `validate_fram_model.py` orchestrator runs all requested steps against any FRAM model:

```bash
cd validation

# Run Steps 2–4 only (TTL model, no JSON-LD counterpart)
python validate_fram_model.py ../examples/eac1-li-huang-2025.ttl

# Run Steps 2–8 (both TTL and JSON-LD available)
python validate_fram_model.py \
    ../examples/eac1-li-huang-2025.ttl \
    ../examples/eac1-li-huang-2025.jsonld

# Skip OOPS! API call (Step 5) for faster offline runs
python validate_fram_model.py \
    ../examples/eac1-li-huang-2025.ttl \
    ../examples/eac1-li-huang-2025.jsonld \
    --skip-oops

# Run specific steps only
python validate_fram_model.py \
    ../examples/eac1-li-huang-2025.ttl \
    ../examples/eac1-li-huang-2025.jsonld \
    --steps 2,3,4,8

# Validate the second reference model (EAC2 — Patriarca et al. 2024)
python validate_fram_model.py \
    ../examples/eac2-patriarca-et-al.-2024.ttl \
    ../examples/eac2-patriarca-et-al.-2024.jsonld \
    --skip-oops
```

> **Note:** Step 1 runs only when a JSON-LD input is provided. Steps 6–8 require both TTL and JSON-LD exports of the same model. The orchestrator deselects them automatically when the JSON-LD input is omitted.

### Repository-Level Files Used

| File | Role |
|------|------|
| [`../fram.ttl`](../fram.ttl) | TBox — canonical ontology definition (1309 triples; 59 classes; 129 properties) |
| [`../context.jsonld`](../context.jsonld) | JSON-LD context for term resolution |
| [`../fram-shapes.ttl`](../fram-shapes.ttl) | SHACL shapes (8 shapes: S1–S8) |
| [`../examples/eac1-li-huang-2025.ttl`](../examples/eac1-li-huang-2025.ttl) | ABox — Li & Huang (2025) HSR model (20 functions, 34 couplings, 2860 triples) |
| [`../examples/eac1-li-huang-2025.jsonld`](../examples/eac1-li-huang-2025.jsonld) | ABox — Li & Huang (2025) JSON-LD serialization |
| [`../examples/eac2-patriarca-et-al.-2024.ttl`](../examples/eac2-patriarca-et-al.-2024.ttl) | ABox — Patriarca et al. (2024) FRW model (14 functions, 21 couplings, 2196 triples) |
| [`../examples/eac2-patriarca-et-al.-2024.jsonld`](../examples/eac2-patriarca-et-al.-2024.jsonld) | ABox — Patriarca et al. (2024) JSON-LD serialization |

## SHACL Shapes

The [`fram-shapes.ttl`](../fram-shapes.ttl) file defines 8 SHACL shapes:

| Shape | Target | Constraints |
|-------|--------|-------------|
| S1: FRAMModelShape | `fram:FRAMModel` | Must have `schema:name` and ≥1 `fram:hasFunction` |
| S2: FunctionShape | `fram:Function` | Must have `schema:name`, `fram:functionType`, ≥1 `fram:hasAspect` |
| S3: CouplingShape | `fram:Coupling` | Must have `sourceFunction`, `targetFunction`, `sourceAspect`, `targetAspect` |
| S4: AspectShape | `fram:Aspect` (via SPARQL) | Must have valid `aspectType` and `aspectCode` ∈ {I, O, P, R, C, T} |
| S5: NormalDistShape | `fram:NormalDistribution` | Must have `distributionMean` and `distributionStdDev` > 0 |
| S6: PhenotypeShape | `fram:Phenotype` (via SPARQL) | Must have `phenotypeProbability` ∈ [0, 1] |
| S7: PhenotypeMappingRuleShape | `fram:PhenotypeMappingRule` | Must have `mapsToVariable` (string) and `mapsToDimension` (VariabilityDimension) |
| S8: WAIDeclarationShape | `fram:WAIDeclaration` | Must have `dominantPhenotype` (string) and `waiConfidence` ∈ {Low, Medium, High} |

## Competency Questions

Step 4 validates the ontology against 6 SPARQL-based competency questions executed against the reference ABoxes in [`../examples/`](../examples/):

| CQ | Question | EAC1 (Li & Huang, 2025) | EAC2 (Patriarca et al., 2024) |
|----|----------|:---:|:---:|
| CQ1 | What are the model's functions and their types? | 20 | 14 |
| CQ2 | What are the couplings between functions? | 34 | 21 |
| CQ3 | How many aspects does each function have? | 20 | 14 |
| CQ4 | Which functions have variability metadata? | 20 | 14 |
| CQ5 | What are the variability phenotypes of the functions? | 20 | 14 |
| CQ6 | Which functions receive input from other functions via couplings? | 17 | 11 |

## Expected Results (v1.8.0)

All steps should pass with the current ontology version against both reference ABoxes:

| Step | EAC1 (Li & Huang, 2025) | EAC2 (Patriarca et al., 2024) |
|------|---|---|
| 1 | JSON-LD → TTL conversion succeeds (skipped if input is already TTL) | idem |
| 2 | PASS — TBox 1309 / ABox 2860 / 5321 inferred; consistent; 0 unsatisfiable | PASS — TBox 1309 / ABox 2196 / 4376 inferred; consistent; 0 unsatisfiable |
| 3 | PASS — conforms to all 8 shapes | PASS — conforms to all 8 shapes |
| 4 | PASS — 6/6 CQs answered | PASS — 6/6 CQs answered |
| 5 | PASS — 0 pitfalls at any severity (executed against TBox; same result for both ABoxes) | idem |
| 6 | RT1 PASS; RT2 / RT3 expected FAIL (BNode instability and structural differences) | idem |
| 7 | 56/71 predicates matching (78.9%) — informational | 58/74 predicates matching (78.4%) — informational |
| 8 | PASS — 9/9 applicable SPARQL queries equivalent (100%) | PASS — 9/9 applicable SPARQL queries equivalent (100%) |

> **Step 7 (Gap Analysis) is informational, not a pass/fail criterion.** Coverage cannot reach 100% by construction: the TTL serialization exposes every RDF predicate in the TBox (including `owl:imports`, `rdfs:label`, structural metadata, and named aspect IRIs such as `fram:Input`, `fram:Control`, `fram:Time`), while the compact JSON-LD serialization projects a subset of those predicates onto named keys via the `@context`. Some predicates appear only in JSON-LD (`fram:framPrinciples`, populated by JSON-LD framing). Reaching 100% would require an expanded JSON-LD form, which would defeat the legibility goal of the compact serialization. Semantic equivalence between the two serializations is verified by Step 6 (graph isomorphism, RT1) and Step 8 (gold-standard SPARQL equivalence), which are the binding criteria.

## Generated Files

The runner may generate the following intermediate files (gitignored):

- `*-model.ttl` — Turtle conversion of JSON-LD input (Step 1)
- `fram_rdfxml.owl` — RDF/XML conversion for OOPS! submission (Step 5)
- `oops_response.xml` — Raw OOPS! API response (Step 5)
- `shacl_violations.txt` — SHACL violation report, if any (Step 3)

## Background

This validation benchmark was developed as part of **Preliminary Study 2 (EP2)** in a Design Science Research (DSR) thesis investigating the formalization of FRAM models as Linked Data. The methodology follows established ontology evaluation practices:

- **Logical validation**: OWL-RL reasoning (Motik et al., 2012)
- **Structural validation**: SHACL (Knublauch & Kontokostas, 2017)
- **Competency validation**: SPARQL-based CQs (Grüninger & Fox, 1995)
- **Pitfall detection**: OOPS! (Poveda-Villalón et al., 2014)
- **Round-trip & semantic equivalence**: serialization-independence verification across TTL and JSON-LD (added in v1.8.0)
- **Modular runner architecture**: 8 independent step modules + thin orchestrator (refactored from the v1.8.0 mixed inline/subprocess runner; no behavioural change for end users)

## License

Same as the parent ontology — [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
