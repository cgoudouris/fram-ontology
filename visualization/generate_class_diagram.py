#!/usr/bin/env python3
"""
Generate publication-quality class diagrams of the FRAM Ontology v1.8.1.

Produces TWO companion figures:

  1. fram_ontology_diagram.{svg,png}
     Class hierarchy + gUFO foundational alignment, organised as a
     compact top-down tree. Intra-FRAM subClassOf is conveyed by the
     cluster labels themselves (e.g. "subclasses of fram:Function"),
     so the figure has no long crossing subClassOf edges. The only
     explicit edges are the six FRAM->gUFO alignments.

  2. fram_ontology_properties.{svg,png}
     A small, focused network of the key object properties
     (domain -> range), without the subclass clutter.

Splitting the original "everything in one figure" layout into two
companion figures eliminates the visual spaghetti caused by
property edges crossing the entire subclass lattice.

Usage:
    pip install rdflib graphviz
    python generate_class_diagram.py
"""

from rdflib import Graph, Namespace
from graphviz import Digraph

FRAM = Namespace("https://flowfram.com/ontology/fram/")
GUFO = Namespace("http://purl.org/nemo/gufo#")

COLORS = {
    "core": "#2C3E50",
    "function_type": "#2980B9",
    "aspect": "#27AE60",
    "variability": "#E67E22",
    "wai_wad": "#8E44AD",
    "gufo": "#C0392B",
}

GUFO_FILL = "#FDEDEC"
FRAM_FILL = "#EBF5FB"
FUNC_FILL = "#D6EAF8"
ASP_FILL = "#D5F5E3"
VAR_FILL = "#FDEBD0"
WAI_FILL = "#E8DAEF"


def load_ontology(ttl_path: str) -> Graph:
    g = Graph()
    g.parse(ttl_path, format="turtle")
    return g


def _nid(label: str) -> str:
    return label.replace(":", "_")


def _node(parent, label, fill, color, dashed=False, fontsize="10"):
    style = "filled,rounded,dashed" if dashed else "filled,rounded"
    parent.node(
        _nid(label), label=label, color=color, fillcolor=fill,
        style=style, fontname="Helvetica", fontsize=fontsize,
        shape="box", penwidth="1.3", margin="0.10,0.05",
    )


def build_hierarchy_diagram(g: Graph, output_name: str):
    """Class hierarchy + gUFO alignment as a compact TB tree."""
    dot = Digraph(
        name="FRAM Ontology v1.8.1 - Class Hierarchy",
        format="svg",
        engine="dot",
        graph_attr={
            "rankdir": "TB",
            "label": "FRAM Ontology v1.8.1 - Class Hierarchy and gUFO Alignment\n ",
            "labelloc": "t",
            "fontname": "Helvetica",
            "fontsize": "16",
            "bgcolor": "white",
            "pad": "0.4",
            "nodesep": "0.25",
            "ranksep": "0.55",
            "splines": "polyline",
            "newrank": "true",
        },
        node_attr={"fontname": "Helvetica"},
        edge_attr={"fontname": "Helvetica", "fontsize": "9", "arrowsize": "0.7"},
    )

    # Row 1: gUFO foundational anchors (top)
    gufo_classes = [
        "gufo:Object", "gufo:Event", "gufo:IntrinsicMode",
        "gufo:RelationalQuality", "gufo:Quality", "gufo:QualityValue",
        "gufo:Disposition",
    ]
    with dot.subgraph(name="cluster_gufo") as c:
        c.attr(
            label="gUFO Foundational Anchors", style="rounded,filled",
            color=COLORS["gufo"], fillcolor="#FBEEE6",
            fontcolor=COLORS["gufo"], fontname="Helvetica",
            fontsize="11", penwidth="1.5", margin="10",
        )
        for lbl in gufo_classes:
            _node(c, lbl, GUFO_FILL, COLORS["gufo"], dashed=True, fontsize="9")

    # Row 2: Core FRAM
    core_classes = ["fram:FRAMModel", "fram:Coupling", "fram:Function", "fram:Aspect"]
    with dot.subgraph(name="cluster_core") as c:
        c.attr(
            label="Core FRAM", style="rounded,filled",
            color=COLORS["core"], fillcolor="#EAF2F8",
            fontcolor=COLORS["core"], fontname="Helvetica",
            fontsize="11", penwidth="1.5", margin="10",
        )
        for lbl in core_classes:
            _node(c, lbl, FRAM_FILL, COLORS["core"], fontsize="11")

    # Row 3a: Function specialisations
    func_role = ["fram:EntryFunction", "fram:ExitFunction",
                 "fram:ForegroundFunction", "fram:BackgroundFunction"]
    func_nature = ["fram:HumanFunction", "fram:TechnologicalFunction",
                   "fram:OrganisationalFunction"]
    with dot.subgraph(name="cluster_func") as c:
        c.attr(
            label="Function Specialisations  (subclasses of fram:Function)",
            style="rounded,filled", color=COLORS["function_type"],
            fillcolor="#EBF5FB", fontcolor=COLORS["function_type"],
            fontname="Helvetica", fontsize="11", penwidth="1.5", margin="10",
        )
        with c.subgraph(name="cluster_func_role") as r:
            r.attr(label="by Role", style="dashed", color="#5DADE2",
                   fontsize="9", fontname="Helvetica", margin="6")
            for lbl in func_role:
                _node(r, lbl, FUNC_FILL, COLORS["function_type"], fontsize="9")
        with c.subgraph(name="cluster_func_nature") as n:
            n.attr(label="by Nature", style="dashed", color="#5DADE2",
                   fontsize="9", fontname="Helvetica", margin="6")
            for lbl in func_nature:
                _node(n, lbl, FUNC_FILL, COLORS["function_type"], fontsize="9")

    # Row 3b: Aspect subtypes
    aspect_types = ["fram:InputAspect", "fram:OutputAspect", "fram:PreconditionAspect",
                    "fram:ResourceAspect", "fram:ControlAspect", "fram:TimeAspect"]
    with dot.subgraph(name="cluster_asp") as c:
        c.attr(
            label="Aspect Subtypes  (I / O / P / R / C / T - subclasses of fram:Aspect)",
            style="rounded,filled", color=COLORS["aspect"],
            fillcolor="#E8F8F0", fontcolor=COLORS["aspect"],
            fontname="Helvetica", fontsize="11", penwidth="1.5", margin="10",
        )
        for lbl in aspect_types:
            _node(c, lbl, ASP_FILL, COLORS["aspect"], fontsize="9")

    # Row 4: Variability + WAI side clusters
    var_classes = ["fram:Variability", "fram:Phenotype",
                   "fram:VariabilityDimension", "fram:PerformanceCondition"]
    with dot.subgraph(name="cluster_var") as c:
        c.attr(
            label="Variability & Quantitative", style="rounded,filled",
            color=COLORS["variability"], fillcolor="#FDF2E9",
            fontcolor=COLORS["variability"], fontname="Helvetica",
            fontsize="11", penwidth="1.5", margin="10",
        )
        for lbl in var_classes:
            _node(c, lbl, VAR_FILL, COLORS["variability"], fontsize="9")

    wai_classes = ["fram:FRAMScenario", "fram:WAIDeclaration",
                   "fram:FunctionalResonance"]
    with dot.subgraph(name="cluster_wai") as c:
        c.attr(
            label="WAI / WAD Analysis", style="rounded,filled",
            color=COLORS["wai_wad"], fillcolor="#F4ECF7",
            fontcolor=COLORS["wai_wad"], fontname="Helvetica",
            fontsize="11", penwidth="1.5", margin="10",
        )
        for lbl in wai_classes:
            _node(c, lbl, WAI_FILL, COLORS["wai_wad"], fontsize="9")

    # Explicit edges: ONLY the FRAM -> gUFO alignment.
    # Intra-FRAM subClassOf is conveyed by cluster labels.
    gufo_subclass = [
        ("fram:FRAMModel", "gufo:Object"),
        ("fram:Function", "gufo:Event"),
        ("fram:Aspect", "gufo:IntrinsicMode"),
        ("fram:Coupling", "gufo:RelationalQuality"),
        ("fram:Variability", "gufo:Quality"),
        ("fram:VariabilityDimension", "gufo:Quality"),
        ("fram:Phenotype", "gufo:QualityValue"),
        ("fram:PerformanceCondition", "gufo:Disposition"),
    ]
    for child, parent in gufo_subclass:
        dot.edge(
            _nid(child), _nid(parent),
            arrowhead="empty", color=COLORS["gufo"],
            style="dashed", penwidth="1.4",
        )

    # Invisible anchors to enforce row order
    dot.edge("fram_Function", "fram_HumanFunction", style="invis")
    dot.edge("fram_Function", "fram_EntryFunction", style="invis")
    dot.edge("fram_Aspect", "fram_InputAspect", style="invis")
    dot.edge("fram_FRAMModel", "fram_Variability", style="invis")
    dot.edge("fram_FRAMModel", "fram_FRAMScenario", style="invis")

    # Compact HTML legend
    legend_html = (
        '<<table border="0" cellborder="0" cellspacing="2" cellpadding="3">'
        '<tr><td colspan="2"><b>Legend</b></td></tr>'
        '<tr><td bgcolor="#EBF5FB" width="22"> </td><td align="left">Core FRAM</td></tr>'
        '<tr><td bgcolor="#D6EAF8"> </td><td align="left">Function specialisation</td></tr>'
        '<tr><td bgcolor="#D5F5E3"> </td><td align="left">Aspect subtype (I/O/P/R/C/T)</td></tr>'
        '<tr><td bgcolor="#FDEBD0"> </td><td align="left">Variability / Quantitative</td></tr>'
        '<tr><td bgcolor="#E8DAEF"> </td><td align="left">WAI / WAD analysis</td></tr>'
        '<tr><td bgcolor="#FDEDEC"> </td><td align="left">gUFO foundational class (dashed)</td></tr>'
        '<tr><td><font color="#C0392B">- - -&gt;</font></td>'
        '<td align="left"><font color="#C0392B">rdfs:subClassOf to gUFO</font></td></tr>'
        '<tr><td colspan="2" align="left">'
        '<font point-size="8"><i>Intra-FRAM subClassOf is implicit in cluster labels.</i></font>'
        '</td></tr>'
        '</table>>'
    )
    dot.node(
        "legend", label=legend_html, shape="plaintext",
        fontname="Helvetica", fontsize="10",
    )

    dot.node(
        "annotation",
        label=("Showing 30 of 54 classes  -  63 Object Properties  -  "
               "60 Datatype Properties  -  1,235 TBox triples\n"
               "Object-property network in companion figure "
               "(fram_ontology_properties.svg)"),
        shape="note", style="filled", fillcolor="#FCF3CF",
        color="#F4D03F", fontsize="9", fontname="Helvetica",
    )

    dot.render(output_name, cleanup=True)
    print(f"Generated: {output_name}.svg")
    dot.format = "png"
    dot.attr(dpi="220")
    dot.render(output_name, cleanup=True)
    print(f"Generated: {output_name}.png")


def build_property_diagram(g: Graph, output_name: str):
    """Companion diagram: key object properties as a small network."""
    dot = Digraph(
        name="FRAM Ontology v1.8.1 - Object Properties",
        format="svg",
        engine="dot",
        graph_attr={
            "rankdir": "LR",
            "label": "FRAM Ontology v1.8.1 - Key Object Properties (Domain -> Range)\n ",
            "labelloc": "t",
            "fontname": "Helvetica",
            "fontsize": "15",
            "bgcolor": "white",
            "pad": "0.4",
            "nodesep": "0.55",
            "ranksep": "1.4",
            "splines": "polyline",
        },
        node_attr={
            "fontname": "Helvetica", "fontsize": "10",
            "shape": "box", "style": "filled,rounded",
            "penwidth": "1.3", "margin": "0.10,0.05",
        },
        edge_attr={"fontname": "Helvetica", "fontsize": "9", "arrowsize": "0.7"},
    )

    nodes = [
        ("fram:FRAMScenario", COLORS["wai_wad"], WAI_FILL),
        ("fram:FRAMModel", COLORS["core"], FRAM_FILL),
        ("fram:Function", COLORS["core"], FRAM_FILL),
        ("fram:Coupling", COLORS["core"], FRAM_FILL),
        ("fram:Aspect", COLORS["core"], FRAM_FILL),
        ("fram:Variability", COLORS["variability"], VAR_FILL),
        ("fram:VariabilityDimension", COLORS["variability"], VAR_FILL),
        ("fram:Phenotype", COLORS["variability"], VAR_FILL),
        ("fram:PerformanceCondition", COLORS["variability"], VAR_FILL),
        ("fram:WAIDeclaration", COLORS["wai_wad"], WAI_FILL),
    ]
    for label, color, fill in nodes:
        dot.node(_nid(label), label=label, color=color, fillcolor=fill)

    edges = [
        ("fram:FRAMModel", "fram:FRAMScenario", "hasScenario"),
        ("fram:FRAMModel", "fram:Function", "hasFunction"),
        ("fram:FRAMModel", "fram:Coupling", "hasCoupling"),
        ("fram:Function", "fram:Aspect", "hasAspect"),
        ("fram:Coupling", "fram:Function", "sourceFunction"),
        ("fram:Coupling", "fram:Aspect", "sourceAspect"),
        ("fram:Function", "fram:Variability", "hasVariability"),
        ("fram:Variability", "fram:Phenotype", "hasPhenotype"),
        ("fram:Phenotype", "fram:VariabilityDimension", "mapsToDimension"),
        ("fram:Function", "fram:PerformanceCondition", "hasPerformanceCondition"),
        ("fram:Function", "fram:WAIDeclaration", "hasWAIDeclaration"),
    ]
    for d, r, prop in edges:
        dot.edge(
            _nid(d), _nid(r), label=f" {prop} ",
            arrowhead="vee", color="#2874A6", fontcolor="#1B4F72",
            style="solid", penwidth="1.1",
        )

    dot.render(output_name, cleanup=True)
    print(f"Generated: {output_name}.svg")
    dot.format = "png"
    dot.attr(dpi="220")
    dot.render(output_name, cleanup=True)
    print(f"Generated: {output_name}.png")


def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ttl_path = os.path.join(script_dir, "..", "fram.ttl")
    if not os.path.exists(ttl_path):
        ttl_path = os.path.join(script_dir, "..", "..", "fram", "ontology", "fram.ttl")
    if not os.path.exists(ttl_path):
        print("ERROR: Could not find fram.ttl")
        return

    print(f"Loading ontology from: {ttl_path}")
    g = load_ontology(ttl_path)
    print(f"Loaded {len(g)} triples")

    build_hierarchy_diagram(g, os.path.join(script_dir, "fram_ontology_diagram"))
    build_property_diagram(g, os.path.join(script_dir, "fram_ontology_properties"))


if __name__ == "__main__":
    main()
