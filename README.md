# FRAM Ontology

An OWL 2 ontology for the **Functional Resonance Analysis Method (FRAM)**, enabling formal representation of FRAM models as Linked Data.

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
| [`examples/`](examples/) | Example FRAM models serialized as JSON-LD |

## Quick Start

### Using the JSON-LD Context

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
