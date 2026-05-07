# FRAM Ontology

An OWL 2 ontology for the **Functional Resonance Analysis Method (FRAM)**, enabling formal representation of FRAM models as Linked Data.

<a href="https://oops.linkeddata.es"><img src="https://oops.linkeddata.es/images/conformance/oops_free.png" alt="OOPS! pitfall free" height="69" /></a>

This badge certifies that the FRAM ontology was scanned with OOPS! (OntOlogy Pitfall Scanner), a tool that detects structural and semantic pitfalls in OWL ontologies.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18880157.svg)](https://doi.org/10.5281/zenodo.18880157)

This badge resolves to the latest version of the FRAM Ontology archived on Zenodo (concept DOI `10.5281/zenodo.18880157`). Version-specific DOIs are minted automatically for every GitHub release (e.g. v1.8.0 → `10.5281/zenodo.19959352`).

## Overview

![FRAM Ontology — Class Hierarchy and gUFO Alignment](visualization/fram_ontology_diagram.svg?v=2)

*Class hierarchy and gUFO foundational alignment (30 of 54 classes shown). The companion figure [`fram_ontology_properties.svg`](visualization/fram_ontology_properties.svg) presents the network of key object properties (domain → range).*

The FRAM Ontology provides a formal vocabulary for describing FRAM models, including:

- **Functions** — human, technological, organisational, and background activities
- **Aspects** — the six characterizing aspects of each function (Input, Output, Precondition, Resource, Control, Time)
- **Couplings** — directed connections between function outputs and other functions' aspects
- **Variability** — multi-dimensional performance variability with seven dimensions (Timing, Duration, Sequence, Precision, Force, Distance, Direction) and corresponding phenotypes
- **Variability Dimensions** — extensible hierarchy of variability dimensions based on Hollnagel (2012), Delikhoon et al. (2024), and Karevan & Nadeau (2025)
- **Performance Conditions** — Common Performance Conditions (CPCs) that influence variability
- **Functional Resonance** — emergent phenomena arising from the interaction of everyday variability

## Namespace

| Prefix | IRI |
|--------|-----|
| `fram:` | `https://flowfram.com/ontology/fram/` |
| `gufo:` | `http://purl.org/nemo/gufo#` |

## Files

| File | Description |
|------|-------------|
| [`fram.ttl`](fram.ttl) | Canonical ontology definition in Turtle format |
| [`context.jsonld`](context.jsonld) | JSON-LD context file for use in `@context` references |
| [`fram-model.schema.json`](fram-model.schema.json) | JSON Schema (2020-12) for validating FRAM model documents |
| [`fram.owl`](fram.owl) | OWL/RDF-XML serialization (auto-generated from `fram.ttl`) |
| [`fram-shapes.ttl`](fram-shapes.ttl) | SHACL shapes for structural validation (7 shapes) |
| [`examples/`](examples/) | Example FRAM models serialized as JSON-LD |
| [`validation/`](validation/) | 8-step automated validation benchmark (Python) |
| [`visualization/`](visualization/) | Class-diagram generator (`rdflib` + `graphviz`) and two canonical figures: `fram_ontology_diagram.{svg,png}` (class hierarchy + gUFO alignment) and `fram_ontology_properties.{svg,png}` (object-property network) |

## Quick Start

### Using the JSON-LD Context

The `context.jsonld` file is a **JSON-LD Context** — a mapping dictionary that translates concise, human-readable property names (e.g. `"Function"`, `"hasAspect"`, `"couplingStrength"`) into their full ontology IRIs. It also declares namespace prefixes, data types (`xsd:decimal`, `xsd:dateTime`), and container types (`@set`), so that JSON-LD processors can interpret your data as proper RDF without requiring verbose URIs everywhere.

Reference the hosted context in your JSON-LD documents:

```json
{
  "@context": "https://flowfram.com/ontology/fram/context.jsonld",
  "@type": "FRAMModel",
  "name": "My FRAM Model",
  "hasFunction": [
    {
      "@type": ["Function", "HumanFunction"],
      "name": "Perform task",
      "functionType": "human",
      "hasAspect": [
        { "@type": "InputAspect", "name": "Task request" },
        { "@type": "OutputAspect", "name": "Task completed" }
      ]
    }
  ]
}
```

### Content Negotiation

The ontology is hosted at `https://flowfram.com/ontology/fram/` with content negotiation:

| Accept Header | Response |
|---------------|----------|
| `text/turtle` | Turtle ontology (`fram.ttl`) |
| `application/ld+json` | JSON-LD context (`context.jsonld`) |
| `application/rdf+xml` | RDF/XML serialization |
| `text/html` | Human-readable documentation |

```bash
# Get Turtle format
curl -H "Accept: text/turtle" https://flowfram.com/ontology/fram/

# Get JSON-LD context
curl -H "Accept: application/ld+json" https://flowfram.com/ontology/fram/

# Default (HTML documentation)
curl https://flowfram.com/ontology/fram/
```

## Ontology Structure

### Class Hierarchy

```
owl:Thing
├── fram:FRAMModel ─────────────── rdfs:subClassOf gufo:Object
├── fram:Function ─────────────── rdfs:subClassOf gufo:Event
│   ├── fram:HumanFunction
│   ├── fram:TechnologicalFunction
│   ├── fram:OrganisationalFunction

│   ├── fram:BackgroundFunction
│   ├── fram:EntryFunction
│   ├── fram:ExitFunction
│   └── fram:ForegroundFunction
├── fram:Aspect ───────────────── rdfs:subClassOf gufo:IntrinsicMode
│   ├── fram:InputAspect
│   ├── fram:OutputAspect
│   ├── fram:PreconditionAspect
│   ├── fram:ResourceAspect
│   ├── fram:ControlAspect
│   └── fram:TimeAspect
├── fram:Coupling ─────────────── rdfs:subClassOf gufo:RelationalQuality
├── fram:Variability ──────────── rdfs:subClassOf gufo:Quality
│   ├── fram:InternalVariability
│   ├── fram:ExternalVariability
│   ├── fram:UpstreamVariability
│   └── fram:DownstreamVariability
├── fram:VariabilityDimension ─── rdfs:subClassOf gufo:Quality
│   ├── fram:TimingDimension
│   ├── fram:DurationDimension
│   ├── fram:SequenceDimension
│   ├── fram:PrecisionDimension
│   ├── fram:ForceDimension
│   ├── fram:DistanceDimension
│   └── fram:DirectionDimension
├── fram:PerformanceCondition ─── rdfs:subClassOf gufo:Disposition
├── fram:FunctionalResonance ──── rdfs:subClassOf gufo:Event
├── fram:Phenotype ────────────── rdfs:subClassOf gufo:QualityValue
│   ├── fram:TimingPhenotype
│   ├── fram:DurationPhenotype
│   ├── fram:SequencePhenotype
│   ├── fram:PrecisionPhenotype
│   ├── fram:ForcePhenotype
│   ├── fram:DistancePhenotype
│   └── fram:DirectionPhenotype
├── fram:PhenotypeMappingRule ──── rdfs:subClassOf gufo:AbstractIndividual
├── fram:WAIDeclaration ────────── rdfs:subClassOf gufo:AbstractIndividual
├── fram:EmergentPhenotypeResult ─ rdfs:subClassOf gufo:Event
├── fram:WAIWADComparison ──────── rdfs:subClassOf gufo:AbstractIndividual
├── fram:ModelSummary ─────────── ← NEW v1.8.0
├── fram:QuantitativeMetadata ──── ← NEW v1.8.0
├── fram:VariabilityPropagation ── ← NEW v1.8.0
├── fram:FRAMPrinciple ────────── ← NEW v1.8.0
└── fram:FRAMScenario ─────────── rdfs:subClassOf gufo:Object
```

### Key Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `hasFunction` | FRAMModel | Function | Model contains function |
| `hasCoupling` | FRAMModel | Coupling | Model contains coupling |
| `hasAspect` | Function | Aspect | Function has aspect |
| `sourceFunction` | Coupling | Function | Coupling source |
| `targetFunction` | Coupling | Function | Coupling target |
| `hasVariability` | Function | Variability | Function's variability |
| `hasPhenotype` | Variability | Phenotype | Qualitative phenotype |
| `hasPhenotypeMappingRule` | Function | PhenotypeMappingRule | Analyst-defined classification rule |
| `hasWAIDeclaration` | PhenotypeMappingRule | WAIDeclaration | Expected phenotype (Work-as-Imagined) |
| `hasEmergentResult` | PhenotypeMappingRule | EmergentPhenotypeResult | Observed phenotype (Work-as-Done) |
| `hasWAIWADComparison` | Function | WAIWADComparison | WAI/WAD comparison result |
| `discordanceIndex` | WAIWADComparison | xsd:decimal | Δ(WAI-WAD) in [0,1] |
| `couplingStrength` | Coupling | xsd:decimal | Strength (0–1) |

### Phenotype Individuals

**Timing**: `TooEarly`, `OnTime`, `TooLate`, `NotAtAll`

**Duration**: `TooShort`, `Appropriate`, `TooLong`

**Sequence**: `CorrectOrder`, `WrongOrder`, `Skipped`, `Repeated`

**Precision**: `Precise`, `Acceptable`, `Imprecise`

**Force**: `TooLow`, `OnTarget`, `TooHigh`

**Distance** and **Direction**: classes defined; individuals are domain-specific (extend as needed)

## JSON Schema Validation

The `fram-model.schema.json` file provides a [JSON Schema (Draft 2020-12)](https://json-schema.org/draft/2020-12/json-schema-core) for validating FRAM model documents. While the OWL ontology (`fram.ttl`) defines the formal semantics and the JSON-LD context (`context.jsonld`) maps terms to IRIs, the JSON Schema enforces **structural constraints** — required fields, allowed values, data types, and cardinality — that are difficult to express in OWL alone.

### What the Schema Validates

- **Required properties**: every `Function` must have `name`, `@type`, and `functionType`
- **Enumerated values**: `functionType` ∈ {human, technological, organisational, background}, `aspectCode` ∈ {I, O, P, R, C, T}, phenotype values, etc.
- **Numeric constraints**: `couplingStrength` ∈ [0, 1], probability values ∈ [0, 1]
- **Conditional rules**: `WAIDeclaration` requires `dominantPhenotype` and `waiConfidence` ∈ {Low, Medium, High}; `PhenotypeMappingRule` requires `mapsToVariable` and `mapsToDimension`
- **Structural integrity**: correct nesting of functions, aspects, couplings, variability, and scenarios

### Validating a Model

Using [ajv-cli](https://github.com/ajv-validator/ajv-cli):

```bash
npx -y ajv-cli validate -s fram-model.schema.json -d examples/eac1-li-huang-2025.jsonld --spec=draft2020
```

Or programmatically with [ajv](https://ajv.js.org/):

```javascript
const fs = require('fs');
const Ajv2020 = require('ajv/dist/2020').default;
const addFormats = require('ajv-formats');

const ajv = new Ajv2020({ allErrors: true });
addFormats(ajv);

const schema = JSON.parse(fs.readFileSync('fram-model.schema.json', 'utf8'));
const data = JSON.parse(fs.readFileSync('examples/eac1-li-huang-2025.jsonld', 'utf8'));

const validate = ajv.compile(schema);
if (validate(data)) {
  console.log('Valid FRAM model');
} else {
  console.error('Validation errors:', validate.errors);
}
```

### Ontology vs. Schema: Complementary Roles

| Concern | OWL Ontology (`fram.ttl`) | JSON-LD Context (`context.jsonld`) | JSON Schema (`fram-model.schema.json`) |
|---------|--------------------------|-----------------------------------|---------------------------------------|
| Formal semantics | ✅ Class hierarchy, axioms | — | — |
| Term → IRI mapping | — | ✅ Compact ↔ expanded | — |
| Structural validation | Limited | — | ✅ Required fields, types, enums |
| Conditional constraints | Limited | — | ✅ if/then, oneOf |
| Tooling ecosystem | Protégé, reasoners | JSON-LD processors | ajv, IDE autocompletion |

Using all three together provides **semantic precision** (OWL), **Linked Data interoperability** (JSON-LD), and **practical data validation** (JSON Schema).

## Validation

The [`validation/`](validation/) directory contains an **8-step automated benchmark** that verifies the ontology across multiple dimensions:

| Step | Technique | What it validates |
|------|-----------|-------------------|
| 1 | JSON-LD → Turtle | Context resolution, serialization integrity |
| 2 | OWL-RL Reasoning | Logical consistency, unsatisfiable classes |
| 3 | SHACL Shapes | Structural constraints (7 shapes in [`fram-shapes.ttl`](fram-shapes.ttl)) |
| 4 | SPARQL CQs | 6 competency questions against example model |
| 5 | OOPS! Scanner | Common ontology design anti-patterns |
| 6 | Round-trip Fidelity | TTL ↔ JSON-LD serialization integrity |
| 7 | Gap Analysis | Predicate-level coverage between serializations |
| 8 | SPARQL Equivalence | Gold-standard semantic equivalence (10 queries) |

Each step is implemented as an independent module under `validation/steps/` and invoked through a thin orchestrator (`validate_fram_model.py`). Steps can also be executed standalone for debugging.

```bash
pip install rdflib pyld owlrl pyshacl requests
cd validation

# Full benchmark via the orchestrator (recommended)
python validate_fram_model.py \
    ../examples/eac1-li-huang-2025.ttl \
    ../examples/eac1-li-huang-2025.jsonld \
    --skip-oops

# Or run a single step standalone
python -m validation.steps.step3_shacl ../examples/eac1-li-huang-2025.ttl
```

See [`validation/README.md`](validation/README.md) for full instructions and expected results.

## Foundational Ontology Alignment (gUFO)

Since v1.3.0, the FRAM Ontology includes a lightweight alignment with the **Unified Foundational Ontology** ([gUFO](https://purl.org/nemo/gufo)) — Guizzardi et al. (2021). This anchors FRAM domain concepts in well-established ontological categories. As of v1.8.1, the alignment comprises **15 `rdfs:subClassOf` axioms**.

### Alignment Table

| FRAM Class | gUFO Category | Rationale |
|------------|--------------|----------|
| `Function` | `gufo:Event` | Functions are activities that unfold in time |
| `HumanFunction` | `gufo:Event` | Intentional event (via Function) |
| `Aspect` | `gufo:IntrinsicMode` | Intrinsic property particular inhering in a Function |
| `Coupling` | `gufo:RelationalQuality` | First-class relation between two Functions |
| `Variability` | `gufo:Quality` | Measurable property with an associated quality space |
| `PerformanceCondition` | `gufo:Disposition` | Latent property that manifests under specific conditions |
| `FunctionalResonance` | `gufo:Event` | Emergent complex event |
| `Phenotype` | `gufo:QualityValue` | Point in the quality space of variability |
| `VariabilityDimension` | `gufo:Quality` | Measurable dimension of performance variability |
| `PhenotypeMappingRule` | `gufo:AbstractIndividual` | Abstract classification specification |
| `WAIDeclaration` | `gufo:AbstractIndividual` | Abstract expectation declaration |
| `EmergentPhenotypeResult` | `gufo:Event` | Observed simulation outcome |
| `WAIWADComparison` | `gufo:AbstractIndividual` | Comparison artifact with discordance index |
| `FRAMModel` | `gufo:Object` | Persistent endurant aggregating functions and couplings |
| `FRAMScenario` | `gufo:Object` | Persistent configuration for comparative analysis |

### Design Decision: Function as Event (not Disposition)

Lališ et al. (2019) proposed mapping FRAM Functions to UFO *Dispositions* — latent properties that manifest through events. We diverge: a FRAM Function is "what people have to do or what has to take place" (Hollnagel, 2012) — the activity itself, not the capacity to perform it. The Disposition mapping is reused for `PerformanceCondition` (CPC), which genuinely represents latent properties influencing variability.

### References

- Guizzardi, G. (2005). *Ontological Foundations for Structural Conceptual Models*. PhD Thesis, University of Twente.
- Guizzardi, G. et al. (2021). gUFO: A Lightweight Implementation of the UFO. *Applied Ontology*, 17(1), 105-150.
- Lališ, A. et al. (2019). Foundational ontological analysis of the FRAM. *Safety Science*, 117, 291-305.

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2025-02 | Initial release — core classes (Function, Aspect, Coupling, Variability) |
| 1.1.0 | 2025-02 | Added quantitative metadata classes (Constant, Variable, OutputMessage, InterpretationProfile, Passthrough) |
| 1.2.0 | 2025-03 | Added Distribution and Phenotype class hierarchies; FRAMScenario |
| 1.3.0 | 2025-03 | gUFO foundational alignment (11 axioms); full inverse properties; disjointness axioms; OOPS! validation |
| 1.4.0 | 2025-06 | Function taxonomy restructuring — orthogonal Nature (Human, Technological, Organisational) and Flow Role (Entry, Exit, Background, Foreground) dimensions |
| 1.5.0 | 2025-07 | Multi-dimensional variability — VariabilityDimension class with 7 subclasses (Timing, Duration, Sequence, Precision, Force, Distance, Direction); 5 new Phenotype subclasses; 10 new individuals; 12th gUFO axiom; expanded disjointness axioms |
| 1.6.0 | 2026-04 | Emergent phenotype classification — 4 new classes (PhenotypeMappingRule, WAIDeclaration, EmergentPhenotypeResult, WAIWADComparison); 6 new object properties; 7 new datatype properties; WAI/WAD comparison framework with discordance index Δ(WAI-WAD); 16 gUFO axioms |
| 1.7.0 | 2026-04 | Semantic purity refinement — 6 new datatype properties for TBox completeness: `targetAspectType` (OutputMessage routing), `input`, `precondition`, `resource`, `control`, `time` (InterpretationProfile aspect modes); context.jsonld expanded with `model:` prefix for ABox IRIs; examples updated to Li-Huang-2025 cross-domain model; SPARQL equivalence validated (9/9 PASS) between TTL and JSON-LD serializations |
| 1.8.0 | 2026-04 | ABox alignment and domain purity — 4 new classes (ModelSummary, QuantitativeMetadata, VariabilityPropagation, FRAMPrinciple), 9 new object properties, 11 new datatype properties; validation benchmark expanded from 5 to 8 steps with round-trip fidelity, gap analysis, and SPARQL equivalence; domain purity audit: platform-specific concepts (LLM prompts, AI insights) excluded from TBox by design; TBox: 59 classes, 129 properties (65 OP + 64 DP), 1309 triples |
| 1.8.1 | 2026-05 | Patch release — removed all Distribution-related elements (Distribution class and 4 subclasses, `hasDistribution` / `isDistributionOf` object properties, `distributionMean` / `distributionStdDev` / `distributionMin` / `distributionMax` datatype properties, `NormalDistShape`, gUFO alignment `Distribution rdfs:subClassOf gufo:AbstractIndividual`). The previous Monte-Carlo-bound design was inadequate to express the methodological pluralism of variability quantification in FRAM (analytical, fuzzy, Bayesian, agent-based) and is deferred to a future release. The TBox now represents variability strictly at the qualitative level: dimensions and classified phenotypes with associated probability. TBox: 54 classes, 123 properties (63 OP + 60 DP), 1235 triples; 7 SHACL shapes; 15 gUFO axioms |

## Background

The Functional Resonance Analysis Method was developed by Erik Hollnagel as a method for analyzing complex socio-technical systems. Unlike traditional methods that decompose systems into components, FRAM describes systems in terms of the functions that are performed and the couplings between them.

Key references:
- Hollnagel, E. (2012). *FRAM: The Functional Resonance Analysis Method*. Ashgate.
- Hollnagel, E. (2014). *Safety-I and Safety-II*. Ashgate.
- Hollnagel, E. (2017). *Safety-II in Practice*. Routledge.

## Design Principle: Domain Purity

The FRAM Ontology models **exclusively FRAM domain concepts** as defined in the methodology literature (Hollnagel, 2012; Hollnagel, 2014). Platform-specific concerns — such as LLM prompt templates, AI-generated insights, visual layout coordinates, and runtime execution state — are deliberately excluded from the TBox. This ensures the ontology is **technology-agnostic** and usable by any FRAM tool, researcher, or application without dependencies on any particular software platform.

This design follows the principle articulated by Gruber (1993): *"an ontology should specify only the most fundamental domain concepts, independent of any particular application or use case."* Tools that consume the ontology may extend it locally for their own purposes, but the published vocabulary remains a pure, reusable domain model.

## Platform

This ontology powers the [FlowFRAM](https://flowfram.com) platform, an open-source tool for creating, analyzing, and simulating FRAM models with:

- Visual model editor with hexagonal function representation
- FRAM Model Instantiation (FMI) with multi-cycle simulation
- Quantitative variability analysis with probability distributions
- JSON-LD export for Linked Data interoperability
- AI-assisted analysis via LLM integration

## Contributing

Contributions are welcome! Please:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/new-class`)
3. Make your changes to `fram.ttl` (the canonical source)
4. Update `context.jsonld` if adding new terms
5. Add examples if appropriate
6. Submit a pull request

### Development Guidelines

- The Turtle file (`fram.ttl`) is the **canonical source of truth**
- All terms must include `rdfs:label`, `rdfs:comment`, and `rdfs:isDefinedBy`
- Use English language tags (`@en`) for all labels and comments
- Follow the existing naming conventions (PascalCase for classes, camelCase for properties)
- Include `skos:definition` for core FRAM concepts that have formal definitions
- Update `fram-model.schema.json` when adding new classes or properties
- Validate examples against the JSON Schema after any structural changes

## License

This ontology is released under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/) (CC BY-SA 4.0).

## Citation

If you use this ontology in academic work, please cite:

```bibtex
@misc{framontology2025,
  title = {FRAM Ontology: An OWL 2 Vocabulary for the Functional Resonance Analysis Method},
  author = {Goudouris, César},
  year = {2025},
  url = {https://flowfram.com/ontology/fram/},
  note = {Available at: https://github.com/cgoudouris/fram-ontology}
}
```
