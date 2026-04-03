# EP2 — Ontology Validation Experiment Log

Validation benchmark for the FRAM Ontology, executed against `boil-water-model.jsonld` (ABox) and `fram.ttl` (TBox).

---

## v1.6.0 Validation (Current)

Executed against `fram.ttl` v1.6.0 (1133 TBox triples, ~1560 lines).

### Step 1: JSON-LD → Turtle Conversion

- **Status**: ✅ PASS
- **Input**: `boil-water-model.jsonld`
- **Output**: `boil-water-model.ttl` (124 RDF triples)
- **Method**: pyld (JSON-LD expansion + N-Quads) → rdflib (parse + serialize Turtle)
- **Notes**: All 124 triples generated successfully. Context resolution works correctly with v1.6.0 terms.

### Step 2: OWL-RL Reasoning & Consistency

- **Status**: ✅ PASS
- **TBox triples**: 1133
- **ABox triples**: 124
- **Total before reasoning**: 1257
- **Total after reasoning**: 3101
- **Inferred triples**: 1844
- **Reasoning time**: ~0.30s
- **Consistency**: PASS — 0 instances of `owl:Nothing`
- **Unsatisfiable classes**: PASS — 0 unsatisfiable classes
- **Notes**: The OWL-RL reasoner expanded the graph with type inferences, subclass propagation, inverse property entailments (27 inverse pairs), and 8 disjointness blocks. No contradictions found.

### Step 3: SHACL Shape Validation

- **Status**: ✅ PASS
- **Shapes validated**: 8 (S1–S8)
- **Data triples**: 1257 (TBox + ABox)
- **Conforms**: `true`
- **Notes**: All 8 SHACL shapes in `fram-shapes.ttl` were satisfied:
  - S1 (FRAMModelShape): Model has `name` and ≥1 function ✓
  - S2 (FunctionShape): Functions have `name`, `functionType`, ≥1 aspect ✓
  - S3 (CouplingShape): Couplings have `sourceFunction`, `targetFunction`, `sourceAspect`, `targetAspect` ✓
  - S4 (AspectShape): Aspects have valid `aspectType` and `aspectCode` ∈ {I, O, P, R, C, T} ✓
  - S5 (NormalDistributionShape): NormalDistribution has `mean` and `stdDev` > 0 ✓
  - S6 (PhenotypeShape): Phenotype has `phenotypeProbability` ∈ [0, 1] ✓
  - S7 (PhenotypeMappingRuleShape): No ABox instances to validate (shape defined for future use) ✓
  - S8 (WAIDeclarationShape): No ABox instances to validate (shape defined for future use) ✓

### Step 4: SPARQL Competency Questions

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

### Step 5: OOPS! Pitfall Scanning

- **Status**: ✅ PASS (only known false positive)
- **API**: `https://oops.linkeddata.es/rest`
- **Pitfalls detected**: 1
  - **P04** (Minor): 8 gUFO classes flagged as "unconnected" — these are external foundational ontology classes (`gufo:QualityValue`, `gufo:Object`, `gufo:Event`, `gufo:IntrinsicMode`, `gufo:Disposition`, `gufo:RelationalQuality`, `gufo:Quality`, `gufo:AbstractIndividual`) declared for alignment but not fully connected since gUFO is not imported. **Known false positive** — documented since v1.3.0.
- **Previously fixed in this version**:
  - **P13** (Missing inverses): 5 new v1.6.0 object properties initially lacked `owl:inverseOf`. Fixed by adding 5 inverse declarations.
  - **P05/P19** (Naming conflict): Initially created `isDimensionOf` as inverse of `mapsToDimension`, conflicting with existing `isDimensionOf` (inverse of `hasDimension`). Fixed by renaming to `isMappingDimensionOf`.
- **Notes**: See [oops_analysis.md](oops_analysis.md) for full pitfall history.

### v1.6.0 Overall Summary

| Step | Technique | Result |
|------|-----------|--------|
| 1 | JSON-LD → Turtle | ✅ PASS (124 triples) |
| 2 | OWL-RL Reasoning | ✅ PASS (consistent, 0 unsatisfiable, 1844 inferred) |
| 3 | SHACL Shapes | ✅ PASS (conforms, 8/8 shapes) |
| 4 | SPARQL CQs | ✅ PASS (6/6 questions) |
| 5 | OOPS! Scanner | ✅ PASS (P04 only — gUFO false positive) |

**Ontology version**: v1.6.0 (1133 TBox triples, ~1560 lines)
**Validation date**: April 2026

---

## v1.2.0 Validation (Baseline)

Executed against `fram.ttl` v1.2.0 (669 TBox triples, 1015 lines).

### Step 1: JSON-LD → Turtle Conversion

- **Status**: ✅ PASS
- **Input**: `boil-water-model.jsonld` (4,470 bytes)
- **Output**: `boil-water-model.ttl` (124 RDF triples)
- **Method**: pyld (JSON-LD expansion + N-Quads) → rdflib (parse + serialize Turtle)
- **Notes**: The remote `@context` (`https://flowfram.com/ontology/fram/context.jsonld`) was replaced with the local `context.jsonld` to ensure reproducibility. All 124 triples were generated successfully with prefixes `fram:`, `schema:`, `rdfs:`, and `xsd:` correctly mapped.

### Step 2: OWL-RL Reasoning & Consistency

- **Status**: ✅ PASS
- **TBox triples**: 669
- **ABox triples**: 124
- **Total before reasoning**: 793
- **Total after reasoning**: ~5,800+ (inferred)
- **Reasoning time**: ~2–4s
- **Consistency**: PASS — 0 instances of `owl:Nothing`
- **Unsatisfiable classes**: PASS — 0 unsatisfiable classes
- **Notes**: The OWL-RL reasoner successfully expanded the graph with type inferences, subclass propagation, and inverse property entailments. No contradictions found.

### Step 3: SHACL Shape Validation

- **Status**: ✅ PASS
- **Shapes validated**: 6 (S1–S6)
- **Data triples**: 793 (TBox + ABox)
- **Conforms**: `true`
- **Notes**: All 6 SHACL shapes in `fram-shapes.ttl` were satisfied.

### Step 4: SPARQL Competency Questions

- **Status**: ✅ PASS (6/6)

### Step 5: OOPS! Pitfall Scanning

- **Status**: ✅ PASS
- **v1.0 results**: 4 pitfalls (P04, P10, P11, P13) — see [oops_analysis.md](oops_analysis.md)
- **v1.2.0 results**: 0 pitfalls detected

### v1.2.0 Overall Summary

| Step | Technique | Result |
|------|-----------|--------|
| 1 | JSON-LD → Turtle | ✅ PASS (124 triples) |
| 2 | OWL-RL Reasoning | ✅ PASS (consistent, 0 unsatisfiable) |
| 3 | SHACL Shapes | ✅ PASS (conforms, 6/6 shapes) |
| 4 | SPARQL CQs | ✅ PASS (6/6 questions) |
| 5 | OOPS! Scanner | ✅ PASS (0 pitfalls in v1.2.0) |

**Ontology version**: v1.2.0 (793 triples, 1015 lines)
**Validation date**: February 2026
