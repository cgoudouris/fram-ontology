# FRAM Ontology Validation Benchmark

An eight-step automated validation benchmark for the [FRAM Ontology](../fram.ttl), based on the **Preliminary Study 2 (EP2)** conducted as part of a Design Science Research (DSR) thesis.

## Overview

This benchmark verifies the FRAM Ontology across eight complementary dimensions:

| Step | Technique | Tool | What it validates |
|------|-----------|------|-------------------|
| 1 | JSON-LD → Turtle conversion | pyld + rdflib | Context resolution, IRI expansion, serialization integrity |
| 2 | OWL-RL Reasoning | owlrl | Logical consistency, unsatisfiable classes, inferred triples |
| 3 | SHACL Shape Validation | pyshacl | Structural constraints via 8 custom shapes |
| 4 | SPARQL Competency Questions | rdflib | 5 CQs covering functions, couplings, aspects, variability |
| 5 | OOPS! Pitfall Scanning | OOPS! REST API | Common ontology design anti-patterns |
| 6 | Round-trip Fidelity | rdflib isomorphism | TTL ↔ JSON-LD serialization round-trip integrity |
| 7 | Gap Analysis | rdflib + pyld | Predicate-level differences between serializations |
| 8 | SPARQL Semantic Equivalence | rdflib SPARQL | Gold-standard query equivalence (10 queries) |

## Prerequisites

**Python 3.10+** with the following packages:

```bash
pip install rdflib pyld owlrl pyshacl requests
```

## Running the Benchmark

### Unified Runner (recommended)

The `validate_fram_model.py` script runs all 8 steps against **any** FRAM model:

```bash
cd validation

# Run Steps 2-4 only (TTL model, no JSON-LD counterpart)
python validate_fram_model.py examples/li-huang-2025.ttl

# Run Steps 2-8 (both TTL and JSON-LD available)
python validate_fram_model.py examples/li-huang-2025.ttl examples/li-huang-2025.jsonld

# Skip OOPS! API call (Step 5) for faster offline runs
python validate_fram_model.py examples/li-huang-2025.ttl examples/li-huang-2025.jsonld --skip-oops

# Run specific steps only
python validate_fram_model.py examples/li-huang-2025.ttl examples/li-huang-2025.jsonld --steps 2,3,4,8
```

### Individual Steps (legacy)

The original per-step scripts are still available but are hardcoded for the legacy boil-water example (not included in current examples):

```bash
cd validation

# Step 1: Convert the example JSON-LD model to Turtle
python step1_jsonld_to_ttl.py

# Step 2: Run OWL-RL reasoning (requires Step 1 output)
python step2_reasoning_validation.py

# Step 3: Validate against SHACL shapes (requires Step 1 output)
python step3_shacl_validation.py

# Step 4: Run SPARQL competency questions (requires Step 1 output)
python step4_sparql_competency.py

# Step 5: Submit to OOPS! pitfall scanner (requires internet)
python step5_oops_validation.py
```

Or run all legacy steps sequentially:

```bash
cd validation
for step in step1_jsonld_to_ttl.py step2_reasoning_validation.py step3_shacl_validation.py step4_sparql_competency.py step5_oops_validation.py; do
  echo "======== Running $step ========"
  python "$step"
  echo ""
done

# Steps 6-8 (require both TTL and JSON-LD)
python step6_roundtrip_fidelity.py ../examples/li-huang-2025.ttl ../examples/li-huang-2025.jsonld ../context.jsonld
python step7_gap_analysis.py ../examples/li-huang-2025.ttl ../examples/li-huang-2025.jsonld ../context.jsonld
python step8_sparql_equivalence.py ../examples/li-huang-2025.ttl ../examples/li-huang-2025.jsonld ../context.jsonld
```

> **Note:** Step 1 must run first because Steps 2–4 depend on the generated TTL file. Steps 5–8 are independent. Steps 6–8 require both TTL and JSON-LD exports of the same model.

## File Structure

```
validation/
├── README.md                          # This file
├── validate_fram_model.py             # Unified model-agnostic runner (all 8 steps)
├── step1_jsonld_to_ttl.py             # JSON-LD → Turtle conversion (legacy, boil-water only)
├── step2_reasoning_validation.py      # OWL-RL reasoning & consistency (legacy)
├── step3_shacl_validation.py          # SHACL shape validation (legacy)
├── step4_sparql_competency.py         # SPARQL competency questions (legacy)
├── step5_oops_validation.py           # OOPS! pitfall scanning (legacy)
├── step6_roundtrip_fidelity.py        # Round-trip fidelity: TTL ↔ JSON-LD
├── step7_gap_analysis.py              # Predicate-level gap analysis
├── step8_sparql_equivalence.py        # SPARQL semantic equivalence (10 queries)
└── results/
    ├── experiment_log.md              # Original experiment execution log
    └── oops_analysis.md               # OOPS! pitfall analysis (v1.0 → v1.2.0)
```

### Repository-Level Files Used

| File | Role |
|------|------|
| [`../fram.ttl`](../fram.ttl) | TBox — canonical ontology definition |
| [`../context.jsonld`](../context.jsonld) | JSON-LD context for term resolution |
| [`../fram-shapes.ttl`](../fram-shapes.ttl) | SHACL shapes (8 shapes: S1–S8) |
| [`../examples/boil-water-model.jsonld`](../examples/boil-water-model.jsonld) | ABox — simple example (3 functions, 2 couplings) — **removed in v1.7.0** |
| [`../examples/li-huang-2025.ttl`](../examples/li-huang-2025.ttl) | ABox — Li-Huang 2025 HSR FRAM model (20 functions, 34 couplings) |
| [`../examples/li-huang-2025.jsonld`](../examples/li-huang-2025.jsonld) | ABox — Li-Huang 2025 (JSON-LD) |

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

Step 4 validates the ontology against SPARQL-based competency questions. The unified runner uses 5 model-agnostic CQs; the legacy scripts use 6 CQs specific to the boil-water example.

### Unified Runner (Li-Huang 2025)

| CQ | Question | Expected (Li-Huang) |
|----|----------|---------------------|
| CQ1 | What are the model's functions and their types? | 20 functions |
| CQ2 | What are the couplings between functions? | 34 couplings |
| CQ3 | How many aspects does each function have? | 20 functions (6 each) |
| CQ4 | Which functions have variability metadata? | 20 functions |
| CQ5 | Which functions receive input from other functions via couplings? | 17 functions |

### Legacy Scripts (boil-water)

| CQ | Question | Expected (boil-water) |
|----|----------|----------------------|
| CQ1 | What are the model's functions and their types? | 3 functions (human, technological, human) |
| CQ2 | What are the couplings between functions? | 2 couplings (Fill→Heat, Heat→Pour) |
| CQ3 | What aspects does "Heat water to boiling" have? | 5 aspects (I, O, R, C, T) |
| CQ4 | What is the variability distribution of "Heat water"? | Normal(μ=4.0, σ=0.5) |
| CQ5 | What are the phenotypes of "Fill kettle"? | 2 phenotypes (timing: on-time, precision: acceptable) |
| CQ6 | Which functions receive input via couplings? | 2 functions (Heat water, Pour water) |

## Expected Results (v1.8.0)

All steps should pass with the current ontology version:

| Step | Expected |
|------|----------|
| Step 1 | ~124 triples generated (boil-water legacy) |
| Step 2 | PASS — TBox: 1357, ABox: 3292 (Li-Huang), Inferred: ~5625, consistent, 0 unsatisfiable |
| Step 3 | PASS — conforms to all 8 shapes |
| Step 4 | PASS — all 5 CQs answered correctly |
| Step 5 | PASS -- 0 pitfalls at any severity level |
| Step 6 | RT1: PASS, RT2: FAIL (expected — BNode instability), RT3: FAIL (expected — structural differences) |
| Step 7 | 56/83 predicates matching (67.5%) — informational |
| Step 8 | PASS — 9/9 applicable SPARQL queries equivalent (100%) |

## Generated Files

Scripts may generate the following intermediate files (gitignored):

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

## License

Same as the parent ontology — [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
