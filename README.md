# FRAM Ontology

An OWL 2 ontology for the **Functional Resonance Analysis Method (FRAM)**, enabling formal representation of FRAM models as Linked Data.

<a href="https://oops.linkeddata.es"><img src="https://oops.linkeddata.es/images/conformance/oops_free.png" alt="OOPS! pitfall free" height="69" /></a>

This badge certifies that the FRAM ontology was scanned with OOPS! (OntOlogy Pitfall Scanner), a tool that detects structural and semantic pitfalls in OWL ontologies.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18880158.svg)](https://doi.org/10.5281/zenodo.18880158)

This badge links to the FRAM ontology — a formal OWL representation of the Functional Resonance Analysis Method — published as an open-access artifact on Zenodo with a persistent DOI.

## Overview

The FRAM Ontology provides a formal vocabulary for describing FRAM models, including:

- **Functions** — human, technological, organisational, and background activities
- **Aspects** — the six characterizing aspects of each function (Input, Output, Precondition, Resource, Control, Time)
- **Couplings** — directed connections between function outputs and other functions' aspects
- **Variability** — performance variability characterized by timing and precision phenotypes
- **Performance Conditions** — Common Performance Conditions (CPCs) that influence variability
- **Functional Resonance** — emergent phenomena arising from the interaction of everyday variability
- **Distributions** — probability distributions (Normal, Uniform, Triangular, LogNormal) for quantitative analysis

## Namespace

| Prefix | IRI |
|--------|-----|
| `fram:` | `https://flowfram.com/ontology/fram/` |

## Files

| File | Description |
|------|-------------|
| [`fram.ttl`](fram.ttl) | Canonical ontology definition in Turtle format |
| [`context.jsonld`](context.jsonld) | JSON-LD context file for use in `@context` references |
| [`fram-model.schema.json`](fram-model.schema.json) | JSON Schema (2020-12) for validating FRAM model documents |
| [`fram-shapes.ttl`](fram-shapes.ttl) | SHACL shapes for structural validation (6 shapes) |
| [`examples/`](examples/) | Example FRAM models serialized as JSON-LD |
| [`validation/`](validation/) | 5-step automated validation benchmark (Python) |

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
├── fram:FRAMModel
├── fram:Function
│   ├── fram:HumanFunction
│   ├── fram:TechnologicalFunction
│   ├── fram:OrganisationalFunction
│   ├── fram:BackgroundFunction
│   ├── fram:EntryFunction
│   └── fram:ExitFunction
├── fram:Aspect
│   ├── fram:InputAspect
│   ├── fram:OutputAspect
│   ├── fram:PreconditionAspect
│   ├── fram:ResourceAspect
│   ├── fram:ControlAspect
│   └── fram:TimeAspect
├── fram:Coupling
├── fram:Variability
│   ├── fram:InternalVariability
│   ├── fram:ExternalVariability
│   ├── fram:UpstreamVariability
│   └── fram:DownstreamVariability
├── fram:PerformanceCondition
├── fram:FunctionalResonance
├── fram:Distribution
│   ├── fram:NormalDistribution
│   ├── fram:UniformDistribution
│   ├── fram:TriangularDistribution
│   └── fram:LogNormalDistribution
└── fram:Phenotype
    ├── fram:TimingPhenotype
    └── fram:PrecisionPhenotype
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
| `hasDistribution` | Variability | Distribution | Quantitative distribution |
| `hasPhenotype` | Variability | Phenotype | Qualitative phenotype |
| `couplingStrength` | Coupling | xsd:decimal | Strength (0–1) |

### Phenotype Individuals

**Timing**: `TooEarly`, `OnTime`, `TooLate`, `NotAtAll`

**Precision**: `Precise`, `Acceptable`, `Imprecise`

## JSON Schema Validation

The `fram-model.schema.json` file provides a [JSON Schema (Draft 2020-12)](https://json-schema.org/draft/2020-12/json-schema-core) for validating FRAM model documents. While the OWL ontology (`fram.ttl`) defines the formal semantics and the JSON-LD context (`context.jsonld`) maps terms to IRIs, the JSON Schema enforces **structural constraints** — required fields, allowed values, data types, and cardinality — that are difficult to express in OWL alone.

### What the Schema Validates

- **Required properties**: every `Function` must have `name`, `@type`, and `functionType`
- **Enumerated values**: `functionType` ∈ {human, technological, organisational, background}, `aspectCode` ∈ {I, O, P, R, C, T}, phenotype values, etc.
- **Numeric constraints**: `couplingStrength` ∈ [0, 1], distribution parameters ≥ 0
- **Conditional rules**: `NormalDistribution` requires `mean` + `stddev`; `UniformDistribution` requires `min` + `max`
- **Structural integrity**: correct nesting of functions, aspects, couplings, variability, and scenarios

### Validating a Model

Using [ajv-cli](https://github.com/ajv-validator/ajv-cli):

```bash
npx -y ajv-cli validate -s ontology/fram-model.schema.json -d ontology/examples/boil-water-model.jsonld --spec=draft2020
```

Or programmatically with [ajv](https://ajv.js.org/):

```javascript
const fs = require('fs');
const Ajv2020 = require('ajv/dist/2020').default;
const addFormats = require('ajv-formats');

const ajv = new Ajv2020({ allErrors: true });
addFormats(ajv);

const schema = JSON.parse(fs.readFileSync('ontology/fram-model.schema.json', 'utf8'));
const data = JSON.parse(fs.readFileSync('ontology/examples/boil-water-model.jsonld', 'utf8'));

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

The [`validation/`](validation/) directory contains a **5-step automated benchmark** that verifies the ontology across multiple dimensions:

| Step | Technique | What it validates |
|------|-----------|-------------------|
| 1 | JSON-LD → Turtle | Context resolution, serialization integrity |
| 2 | OWL-RL Reasoning | Logical consistency, unsatisfiable classes |
| 3 | SHACL Shapes | Structural constraints (6 shapes in [`fram-shapes.ttl`](fram-shapes.ttl)) |
| 4 | SPARQL CQs | 6 competency questions against example model |
| 5 | OOPS! Scanner | Common ontology design anti-patterns |

```bash
pip install rdflib pyld owlrl pyshacl requests
cd validation
python step1_jsonld_to_ttl.py
python step2_reasoning_validation.py
python step3_shacl_validation.py
python step4_sparql_competency.py
python step5_oops_validation.py
```

See [`validation/README.md`](validation/README.md) for full instructions and expected results.

## Background

The Functional Resonance Analysis Method was developed by Erik Hollnagel as a method for analyzing complex socio-technical systems. Unlike traditional methods that decompose systems into components, FRAM describes systems in terms of the functions that are performed and the couplings between them.

Key references:
- Hollnagel, E. (2012). *FRAM: The Functional Resonance Analysis Method*. Ashgate.
- Hollnagel, E. (2014). *Safety-I and Safety-II*. Ashgate.
- Hollnagel, E. (2017). *Safety-II in Practice*. Routledge.

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
