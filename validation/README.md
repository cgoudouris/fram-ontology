# FRAM Ontology Validation Benchmark

A five-step automated validation benchmark for the [FRAM Ontology](../fram.ttl), based on the **Preliminary Study 2 (EP2)** conducted as part of a Design Science Research (DSR) thesis.

## Overview

This benchmark verifies the FRAM Ontology across five complementary dimensions:

| Step | Technique | Tool | What it validates |
|------|-----------|------|-------------------|
| 1 | JSON-LD → Turtle conversion | pyld + rdflib | Context resolution, IRI expansion, serialization integrity |
| 2 | OWL-RL Reasoning | owlrl | Logical consistency, unsatisfiable classes, inferred triples |
| 3 | SHACL Shape Validation | pyshacl | Structural constraints via 6 custom shapes |
| 4 | SPARQL Competency Questions | rdflib | 6 CQs covering functions, couplings, aspects, distributions, phenotypes |
| 5 | OOPS! Pitfall Scanning | OOPS! REST API | Common ontology design anti-patterns |

## Prerequisites

**Python 3.10+** with the following packages:

```bash
pip install rdflib pyld owlrl pyshacl requests
```

## Running the Benchmark

All scripts must be run **from the `validation/` directory**:

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

Or run all steps sequentially:

```bash
cd validation
for step in step1_jsonld_to_ttl.py step2_reasoning_validation.py step3_shacl_validation.py step4_sparql_competency.py step5_oops_validation.py; do
  echo "======== Running $step ========"
  python "$step"
  echo ""
done
```

> **Note:** Step 1 must run first because Steps 2–4 depend on the generated `boil-water-model.ttl` file. Step 5 is independent and can run at any time.

## File Structure

```
validation/
├── README.md                          # This file
├── step1_jsonld_to_ttl.py             # JSON-LD → Turtle conversion
├── step2_reasoning_validation.py      # OWL-RL reasoning & consistency
├── step3_shacl_validation.py          # SHACL shape validation
├── step4_sparql_competency.py         # SPARQL competency questions
├── step5_oops_validation.py           # OOPS! pitfall scanning
└── results/
    ├── experiment_log.md              # Original experiment execution log
    └── oops_analysis.md               # OOPS! pitfall analysis (v1.0 → v1.2.0)
```

### Repository-Level Files Used

| File | Role |
|------|------|
| [`../fram.ttl`](../fram.ttl) | TBox — canonical ontology definition |
| [`../context.jsonld`](../context.jsonld) | JSON-LD context for term resolution |
| [`../fram-shapes.ttl`](../fram-shapes.ttl) | SHACL shapes (6 shapes: S1–S6) |
| [`../examples/boil-water-model.jsonld`](../examples/boil-water-model.jsonld) | ABox — example FRAM model |

## SHACL Shapes

The [`fram-shapes.ttl`](../fram-shapes.ttl) file defines 6 SHACL shapes:

| Shape | Target | Constraints |
|-------|--------|-------------|
| S1: FRAMModelShape | `fram:FRAMModel` | Must have `schema:name` and ≥1 `fram:hasFunction` |
| S2: FunctionShape | `fram:Function` | Must have `schema:name`, `fram:functionType`, ≥1 `fram:hasAspect` |
| S3: CouplingShape | `fram:Coupling` | Must have `sourceFunction`, `targetFunction`, `sourceAspect`, `targetAspect` |
| S4: AspectShape | `fram:Aspect` (via SPARQL) | Must have valid `aspectType` and `aspectCode` ∈ {I, O, P, R, C, T} |
| S5: NormalDistShape | `fram:NormalDistribution` | Must have `distributionMean` and `distributionStdDev` > 0 |
| S6: PhenotypeShape | `fram:Phenotype` (via SPARQL) | Must have `phenotypeProbability` ∈ [0, 1] |

## Competency Questions

Step 4 validates the ontology against 6 SPARQL-based competency questions:

| CQ | Question | Expected Answer |
|----|----------|-----------------|
| CQ1 | What are the model's functions and their types? | 3 functions (human, technological, human) |
| CQ2 | What are the couplings between functions? | 2 couplings (Fill→Heat, Heat→Pour) |
| CQ3 | What aspects does "Heat water to boiling" have? | 5 aspects (I, O, R, C, T) |
| CQ4 | What is the variability distribution of "Heat water"? | Normal(μ=4.0, σ=0.5) |
| CQ5 | What are the phenotypes of "Fill kettle"? | 2 phenotypes (timing: on-time, precision: acceptable) |
| CQ6 | Which functions receive input via couplings? | 2 functions (Heat water, Pour water) |

## Expected Results (v1.2.0)

All steps should pass with the current ontology version:

| Step | Expected |
|------|----------|
| Step 1 | ~124 triples generated |
| Step 2 | PASS — consistent, 0 unsatisfiable classes |
| Step 3 | PASS — conforms to all 6 shapes |
| Step 4 | PASS — all 6 CQs answered correctly |
| Step 5 | Improved — pitfalls P04, P10, P11, P13 found in v1.0 were fixed in v1.1–v1.2.0 |

## Generated Files

Scripts may generate the following intermediate files (gitignored):

- `boil-water-model.ttl` — Turtle conversion of the JSON-LD example (Step 1)
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
