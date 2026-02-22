# EP2 — Ontology Validation Experiment Log

Validation benchmark for the FRAM Ontology, executed against `boil-water-model.jsonld` (ABox) and `fram.ttl` v1.2.0 (TBox).

## Step 1: JSON-LD → Turtle Conversion

- **Status**: ✅ PASS
- **Input**: `boil-water-model.jsonld` (4,470 bytes)
- **Output**: `boil-water-model.ttl` (124 RDF triples)
- **Method**: pyld (JSON-LD expansion + N-Quads) → rdflib (parse + serialize Turtle)
- **Notes**: The remote `@context` (`https://flowfram.com/ontology/fram/context.jsonld`) was replaced with the local `context.jsonld` to ensure reproducibility. All 124 triples were generated successfully with prefixes `fram:`, `schema:`, `rdfs:`, and `xsd:` correctly mapped.

## Step 2: OWL-RL Reasoning & Consistency

- **Status**: ✅ PASS
- **TBox triples**: 669
- **ABox triples**: 124
- **Total before reasoning**: 793
- **Total after reasoning**: ~5,800+ (inferred)
- **Reasoning time**: ~2–4s
- **Consistency**: PASS — 0 instances of `owl:Nothing`
- **Unsatisfiable classes**: PASS — 0 unsatisfiable classes
- **Notes**: The OWL-RL reasoner successfully expanded the graph with type inferences, subclass propagation, and inverse property entailments. No contradictions found.

## Step 3: SHACL Shape Validation

- **Status**: ✅ PASS
- **Shapes validated**: 6 (S1–S6)
- **Data triples**: 793 (TBox + ABox)
- **Conforms**: `true`
- **Notes**: All 6 SHACL shapes in `fram-shapes.ttl` were satisfied:
  - S1 (FRAMModelShape): Model has `name` and ≥1 function ✓
  - S2 (FunctionShape): Functions have `name`, `functionType`, ≥1 aspect ✓
  - S3 (CouplingShape): Couplings have `sourceFunction`, `targetFunction`, `sourceAspect`, `targetAspect` ✓
  - S4 (AspectShape): Aspects have valid `aspectType` and `aspectCode` ∈ {I, O, P, R, C, T} ✓
  - S5 (NormalDistributionShape): NormalDistribution has `mean` and `stdDev` > 0 ✓
  - S6 (PhenotypeShape): Phenotype has `phenotypeProbability` ∈ [0, 1] ✓

## Step 4: SPARQL Competency Questions

- **Status**: ✅ PASS (6/6)
- **Results**:

| CQ | Question | Expected | Actual | Status |
|----|----------|----------|--------|--------|
| CQ1 | Functions and their types | 3 functions | 3 | ✅ PASS |
| CQ2 | Couplings between functions | 2 couplings | 2 | ✅ PASS |
| CQ3 | Aspects of "Heat water to boiling" | 5 aspects | 5 | ✅ PASS |
| CQ4 | Variability distribution of "Heat water" | Normal(μ=4.0, σ=0.5) | 1 match | ✅ PASS |
| CQ5 | Phenotypes of "Fill kettle with water" | 2 phenotypes | 2 | ✅ PASS |
| CQ6 | Functions receiving input via couplings | 2 functions | 2 | ✅ PASS |

## Step 5: OOPS! Pitfall Scanning

- **Status**: ✅ PASS (v1.2.0)
- **API**: `https://oops.linkeddata.es/rest`
- **v1.0 results**: 4 pitfalls (P04, P10, P11, P13) — see [oops_analysis.md](oops_analysis.md)
- **v1.2.0 results**: 0 pitfalls detected
- **OOPS! response**: `<oops:OOPSResponse></oops:OOPSResponse>` (empty = no pitfalls)
- **Notes**: All 4 pitfalls identified in v1.0 were fixed in v1.1.0–v1.2.0. The empty response confirms zero remaining issues.

## Overall Summary

| Step | Technique | Result |
|------|-----------|--------|
| 1 | JSON-LD → Turtle | ✅ PASS (124 triples) |
| 2 | OWL-RL Reasoning | ✅ PASS (consistent, 0 unsatisfiable) |
| 3 | SHACL Shapes | ✅ PASS (conforms, 6/6 shapes) |
| 4 | SPARQL CQs | ✅ PASS (6/6 questions) |
| 5 | OOPS! Scanner | ✅ PASS (0 pitfalls in v1.2.0) |

**Ontology version**: v1.2.0 (793 triples, 1015 lines)
**Validation date**: February 2026
