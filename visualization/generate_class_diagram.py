#!/usr/bin/env python3
"""
Generate a publication-quality class diagram of the FRAM Ontology v1.8.0.
Produces an SVG/PNG showing main classes, key object properties, and gUFO alignment.

Usage:
    pip install rdflib graphviz
    python generate_class_diagram.py

Output:
    fram_ontology_diagram.svg
    fram_ontology_diagram.png
"""

from rdflib import Graph, Namespace, RDF, RDFS, OWL
from graphviz import Digraph

# Namespaces
FRAM = Namespace("https://flowfram.com/ontology/fram/")
GUFO = Namespace("http://purl.org/nemo/gufo#")

# Colors for visual grouping
COLORS = {
    "core": "#2C3E50",         # Dark blue - core FRAM classes
    "function_type": "#2980B9", # Blue - function type hierarchy
    "aspect": "#27AE60",        # Green - aspect-related
    "variability": "#E67E22",   # Orange - variability/quantitative
    "wai_wad": "#8E44AD",       # Purple - WAI/WAD analysis
    "gufo": "#E74C3C",          # Red - gUFO alignment
    "structural": "#7F8C8D",    # Gray - structural/metadata
}

GUFO_FILL = "#FDEDEC"   # Light red background for gUFO classes
FRAM_FILL = "#EBF5FB"   # Light blue background for FRAM classes
VAR_FILL = "#FEF9E7"    # Light yellow for variability
WAI_FILL = "#F4ECF7"    # Light purple for WAI/WAD


def load_ontology(ttl_path: str) -> Graph:
    """Load the FRAM ontology from Turtle file."""
    g = Graph()
    g.parse(ttl_path, format="turtle")
    return g


def get_subclass_relations(g: Graph) -> list[tuple[str, str, bool]]:
    """Extract rdfs:subClassOf relations. Returns (child, parent, is_gufo)."""
    relations = []
    for s, _, o in g.triples((None, RDFS.subClassOf, None)):
        child = str(s)
        parent = str(o)
        # Skip blank nodes (restrictions)
        if not child.startswith("http") or not parent.startswith("http"):
            continue
        is_gufo = parent.startswith(str(GUFO))
        relations.append((child, parent, is_gufo))
    return relations


def get_key_object_properties(g: Graph) -> list[tuple[str, str, str, str]]:
    """Extract key object properties with domain/range for the diagram."""
    props = []
    for s in g.subjects(RDF.type, OWL.ObjectProperty):
        prop_name = str(s)
        domains = list(g.objects(s, RDFS.domain))
        ranges = list(g.objects(s, RDFS.range))
        if domains and ranges:
            domain = str(domains[0])
            range_ = str(ranges[0])
            if domain.startswith("http") and range_.startswith("http"):
                props.append((prop_name, shorten(prop_name), domain, range_))
    return props


def shorten(uri: str) -> str:
    """Shorten a URI to its local name."""
    if "#" in uri:
        return uri.split("#")[-1]
    return uri.split("/")[-1]


def safe_id(uri: str) -> str:
    """Create a Graphviz-safe node ID (no colons or slashes)."""
    return uri.replace("https://", "").replace("http://", "").replace("/", "_").replace("#", "_").replace(".", "_").replace("-", "_")


def classify_class(uri: str) -> tuple[str, str]:
    """Classify a FRAM class into a visual group. Returns (color, fill)."""
    name = shorten(uri)

    if uri.startswith(str(GUFO)):
        return COLORS["gufo"], GUFO_FILL

    # Core FRAM classes
    if name in ("FRAMModel", "Function", "Aspect", "Coupling"):
        return COLORS["core"], FRAM_FILL

    # Function types by nature
    if name in ("HumanFunction", "TechnologicalFunction",
                "OrganisationalFunction", "SocialFunction"):
        return COLORS["function_type"], FRAM_FILL

    # Function types by role
    if name in ("EntryFunction", "ExitFunction",
                "ForegroundFunction", "BackgroundFunction"):
        return COLORS["function_type"], FRAM_FILL

    # Aspect subtypes
    if "Aspect" in name and name != "Aspect":
        return COLORS["aspect"], FRAM_FILL

    # Variability & quantitative
    if any(kw in name for kw in ("Variability", "Distribution", "Phenotype",
                                  "Quantitative", "Performance", "Mapping")):
        return COLORS["variability"], VAR_FILL

    # WAI/WAD
    if any(kw in name for kw in ("WAI", "WAD", "Resonance", "Propagation",
                                  "Emergent", "Scenario", "Summary")):
        return COLORS["wai_wad"], WAI_FILL

    return COLORS["structural"], FRAM_FILL


def build_diagram(g: Graph, output_name: str = "fram_ontology_diagram"):
    """Build a focused, publication-quality class diagram with curated layout."""
    dot = Digraph(
        name="FRAM Ontology v1.8.0",
        format="svg",
        engine="dot",
        graph_attr={
            "rankdir": "BT",
            "fontname": "Helvetica",
            "fontsize": "12",
            "label": "FRAM Ontology v1.8.0 — Main Classes, Properties, and gUFO Alignment\n ",
            "labelloc": "t",
            "labelfontsize": "14",
            "pad": "0.5",
            "nodesep": "0.35",
            "ranksep": "0.7",
            "splines": "spline",
            "bgcolor": "white",
            "size": "12,16!",
            "ratio": "compress",
        },
        node_attr={
            "fontname": "Helvetica",
            "fontsize": "9",
            "shape": "box",
            "style": "filled,rounded",
            "penwidth": "1.2",
            "width": "1.4",
            "height": "0.35",
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "7",
        },
    )

    # ========================================================
    # CURATED class selection for publication diagram
    # (showing ~30 key classes instead of all 59)
    # ========================================================

    # --- gUFO classes (external, shown for alignment) ---
    gufo_classes = [
        ("gufo:Event", COLORS["gufo"], GUFO_FILL, "dashed"),
        ("gufo:Object", COLORS["gufo"], GUFO_FILL, "dashed"),
        ("gufo:Disposition", COLORS["gufo"], GUFO_FILL, "dashed"),
        ("gufo:ExternallyDependentMode", COLORS["gufo"], GUFO_FILL, "dashed"),
        ("gufo:Quality", COLORS["gufo"], GUFO_FILL, "dashed"),
        ("gufo:Collection", COLORS["gufo"], GUFO_FILL, "dashed"),
    ]

    # --- Core FRAM classes ---
    core_classes = [
        ("fram:FRAMModel", COLORS["core"], FRAM_FILL),
        ("fram:Function", COLORS["core"], FRAM_FILL),
        ("fram:Aspect", COLORS["core"], FRAM_FILL),
        ("fram:Coupling", COLORS["core"], FRAM_FILL),
    ]

    # --- Function types by nature ---
    func_nature = [
        ("fram:HumanFunction", COLORS["function_type"], FRAM_FILL),
        ("fram:TechnologicalFunction", COLORS["function_type"], FRAM_FILL),
        ("fram:OrganisationalFunction", COLORS["function_type"], FRAM_FILL),
    ]

    # --- Function types by role ---
    func_role = [
        ("fram:EntryFunction", COLORS["function_type"], FRAM_FILL),
        ("fram:ExitFunction", COLORS["function_type"], FRAM_FILL),
        ("fram:ForegroundFunction", COLORS["function_type"], FRAM_FILL),
        ("fram:BackgroundFunction", COLORS["function_type"], FRAM_FILL),
    ]

    # --- Aspect subtypes ---
    aspect_types = [
        ("fram:InputAspect", COLORS["aspect"], FRAM_FILL),
        ("fram:OutputAspect", COLORS["aspect"], FRAM_FILL),
        ("fram:PreconditionAspect", COLORS["aspect"], FRAM_FILL),
        ("fram:ResourceAspect", COLORS["aspect"], FRAM_FILL),
        ("fram:ControlAspect", COLORS["aspect"], FRAM_FILL),
        ("fram:TimeAspect", COLORS["aspect"], FRAM_FILL),
    ]

    # --- Variability & quantitative ---
    var_classes = [
        ("fram:Variability", COLORS["variability"], VAR_FILL),
        ("fram:NormalDistribution", COLORS["variability"], VAR_FILL),
        ("fram:Phenotype", COLORS["variability"], VAR_FILL),
        ("fram:PerformanceCondition", COLORS["variability"], VAR_FILL),
    ]

    # --- WAI/WAD ---
    wai_classes = [
        ("fram:WAIDeclaration", COLORS["wai_wad"], WAI_FILL),
        ("fram:FunctionalResonance", COLORS["wai_wad"], WAI_FILL),
        ("fram:FRAMScenario", COLORS["wai_wad"], WAI_FILL),
    ]

    # --- Create nodes ---
    for label, color, fill, *extra in gufo_classes:
        dot.node(label.replace(":", "_"), label=label, color=color,
                 fillcolor=fill, style="filled,rounded,dashed", penwidth="2.0")

    for group in [core_classes, func_nature, func_role, aspect_types, var_classes, wai_classes]:
        for label, color, fill in group:
            dot.node(label.replace(":", "_"), label=label, color=color,
                     fillcolor=fill)

    # ========================================================
    # RANK constraints to control vertical layout
    # ========================================================

    # Top rank: gUFO
    with dot.subgraph() as s:
        s.attr(rank="max")
        for label, *_ in gufo_classes:
            s.node(label.replace(":", "_"))

    # Second rank: Core FRAM
    with dot.subgraph() as s:
        s.attr(rank="same")
        for label, *_ in core_classes:
            s.node(label.replace(":", "_"))

    # Third rank: Function subtypes
    with dot.subgraph() as s:
        s.attr(rank="same")
        for label, *_ in func_nature + func_role:
            s.node(label.replace(":", "_"))

    # Fourth rank: Aspect subtypes
    with dot.subgraph() as s:
        s.attr(rank="same")
        for label, *_ in aspect_types:
            s.node(label.replace(":", "_"))

    # ========================================================
    # Subclass edges (rdfs:subClassOf)
    # ========================================================
    subclass_edges = [
        # gUFO alignment (dashed red)
        ("fram:Function", "gufo:Event", True),
        ("fram:FRAMModel", "gufo:Collection", True),
        ("fram:Aspect", "gufo:ExternallyDependentMode", True),
        ("fram:Coupling", "gufo:Object", True),
        ("fram:Variability", "gufo:Quality", True),
        ("fram:PerformanceCondition", "gufo:Disposition", True),
        # Function types by nature
        ("fram:HumanFunction", "fram:Function", False),
        ("fram:TechnologicalFunction", "fram:Function", False),
        ("fram:OrganisationalFunction", "fram:Function", False),
        # Function types by role
        ("fram:EntryFunction", "fram:Function", False),
        ("fram:ExitFunction", "fram:Function", False),
        ("fram:ForegroundFunction", "fram:Function", False),
        ("fram:BackgroundFunction", "fram:Function", False),
        # Aspect subtypes
        ("fram:InputAspect", "fram:Aspect", False),
        ("fram:OutputAspect", "fram:Aspect", False),
        ("fram:PreconditionAspect", "fram:Aspect", False),
        ("fram:ResourceAspect", "fram:Aspect", False),
        ("fram:ControlAspect", "fram:Aspect", False),
        ("fram:TimeAspect", "fram:Aspect", False),
    ]

    for child, parent, is_gufo in subclass_edges:
        dot.edge(
            child.replace(":", "_"), parent.replace(":", "_"),
            label="",
            arrowhead="empty",
            color=COLORS["gufo"] if is_gufo else "#555555",
            style="dashed" if is_gufo else "solid",
            penwidth="1.5" if is_gufo else "1.0",
        )

    # ========================================================
    # Key object property edges (blue arrows)
    # ========================================================
    property_edges = [
        ("fram:FRAMModel", "fram:Function", "hasFunction"),
        ("fram:FRAMModel", "fram:Coupling", "hasCoupling"),
        ("fram:Function", "fram:Aspect", "hasAspect"),
        ("fram:Coupling", "fram:Function", "sourceFunction"),
        ("fram:Coupling", "fram:Aspect", "sourceAspect"),
        ("fram:Function", "fram:Variability", "hasVariabilityPotential"),
        ("fram:Variability", "fram:NormalDistribution", "hasDistribution"),
        ("fram:Variability", "fram:Phenotype", "hasPhenotype"),
        ("fram:Function", "fram:PerformanceCondition", "hasPerformanceCondition"),
        ("fram:Function", "fram:WAIDeclaration", "hasWAIDeclaration"),
        ("fram:FRAMScenario", "fram:FRAMModel", "hasModel"),
    ]

    for domain, range_, prop_name in property_edges:
        dot.edge(
            domain.replace(":", "_"), range_.replace(":", "_"),
            label=f"  {prop_name}  ",
            arrowhead="vee",
            color="#3498DB",
            fontcolor="#2471A3",
            style="solid",
            penwidth="0.8",
            constraint="false",
        )

    # ========================================================
    # Legend
    # ========================================================
    with dot.subgraph(name="cluster_legend") as legend:
        legend.attr(
            label="Legend",
            style="rounded",
            color="#BDC3C7",
            fontsize="9",
            fontname="Helvetica",
            labeljust="l",
        )
        legend.node("leg_core", "Core FRAM class", fillcolor=FRAM_FILL,
                     color=COLORS["core"], shape="box", style="filled,rounded",
                     fontsize="8", width="1.3", height="0.25")
        legend.node("leg_gufo", "gUFO alignment\n(rdfs:subClassOf)",
                     fillcolor=GUFO_FILL, color=COLORS["gufo"], shape="box",
                     style="filled,rounded,dashed", fontsize="8", width="1.3",
                     height="0.25")
        legend.node("leg_var", "Variability /\nQuantitative", fillcolor=VAR_FILL,
                     color=COLORS["variability"], shape="box",
                     style="filled,rounded", fontsize="8", width="1.3",
                     height="0.25")
        legend.node("leg_wai", "WAI/WAD\nAnalysis", fillcolor=WAI_FILL,
                     color=COLORS["wai_wad"], shape="box",
                     style="filled,rounded", fontsize="8", width="1.3",
                     height="0.25")
        legend.node("leg_arr", "Object Property",
                     color="#3498DB", shape="plaintext",
                     fontsize="8", fontcolor="#3498DB", width="1.3",
                     height="0.25")
        # Invisible edges to stack legend items
        legend.edge("leg_core", "leg_gufo", style="invis")
        legend.edge("leg_gufo", "leg_var", style="invis")
        legend.edge("leg_var", "leg_wai", style="invis")
        legend.edge("leg_wai", "leg_arr", style="invis")

    # ========================================================
    # Annotation: class count
    # ========================================================
    dot.node("annotation", label="Showing 30 of 59 classes\n65 Object Properties · 64 Datatype Properties\n1,309 TBox triples",
             shape="note", style="filled", fillcolor="#F9E79F",
             color="#F4D03F", fontsize="8", fontname="Helvetica")

    # --- Render ---
    dot.render(output_name, cleanup=True)
    print(f"Generated: {output_name}.svg")

    dot.format = "png"
    dot.attr(dpi="300")
    dot.render(output_name, cleanup=True)
    print(f"Generated: {output_name}.png")


def main():
    import os

    # Find the TTL file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ttl_path = os.path.join(script_dir, "..", "fram.ttl")

    if not os.path.exists(ttl_path):
        # Try the FRAM workspace ontology folder
        ttl_path = os.path.join(script_dir, "..", "..", "fram", "ontology", "fram.ttl")

    if not os.path.exists(ttl_path):
        print("ERROR: Could not find fram.ttl")
        print(f"  Tried: {ttl_path}")
        return

    print(f"Loading ontology from: {ttl_path}")
    g = load_ontology(ttl_path)
    print(f"Loaded {len(g)} triples")

    output = os.path.join(script_dir, "fram_ontology_diagram")
    build_diagram(g, output)


if __name__ == "__main__":
    main()
