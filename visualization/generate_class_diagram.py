#!/usr/bin/env python3
"""
Generate publication-quality class diagrams of the FRAM Ontology v1.8.0.

Produces TWO companion figures:

  1. fram_ontology_diagram.{svg,png}
     Class hierarchy + gUFO foundational alignment, organised in
     visible clusters with orthogonal routing.

  2. fram_ontology_properties.{svg,png}
     A small, focused network of the key object properties
     (domain → range), without the subclass clutter.

Splitting the original "everything in one figure" layout into two
companion figures eliminates the visual spaghetti caused by
property edges crossing the entire subclass lattice.

Usage:
    pip install rdflib graphviz
    python generate_class_diagram.py
"""

from rdflib import Graph, Namespace
from graphviz import Digraph

# Namespaces (kept for future TBox-driven enrichment)
FRAM = Namespace("https://flowfram.com/ontology/fram/")
GUFO = Namespace("http://purl.org/nemo/gufo#")

# Visual palette
COLORS = {
    "core": "#2C3E50",
    "function_type": "#2980B9",
    "aspect": "#27AE60",
    "variability": "#E67E22",
    "wai_wad": "#8E44AD",
    "gufo": "#E74C3C",
}

GUFO_FILL = "#FDEDEC"
FRAM_FILL = "#EBF5FB"
VAR_FILL = "#FEF9E7"
WAI_FILL = "#F4ECF7"


def load_ontology(ttl_path: str) -> Graph:
    g = Graph()
    g.parse(ttl_path, format="turtle")
    return g


def _nid(label: str) -> str:
    return label.replace(":", "_")


def _common_graph_attrs(title: str) -> dict:
    return {
        "rankdir": "LR",
        "fontname": "Helvetica",
        "fontsize": "13",
        "label": title,
        "labelloc": "t",
        "labelfontsize": "15",
        "pad": "0.6",
        "nodesep": "0.45",
        "ranksep": "1.1",
        "splines": "ortho",
        "concentrate": "true",
        "bgcolor": "white",
        "newrank": "true",
    }


def _common_node_attrs() -> dict:
    return {
        "fontname": "Helvetica",
        "fontsize": "10",
        "shape": "box",
        "style": "filled,rounded",
        "penwidth": "1.3",
        "width": "1.7",
        "height": "0.42",
        "margin": "0.10,0.05",
    }


def _common_edge_attrs() -> dict:
    return {
        "fontname": "Helvetica",
        "fontsize": "9",
        "arrowsize": "0.7",
    }


def _add_node(parent, label: str, color: str, fill: str, dashed: bool = False):
    style = "filled,rounded,dashed" if dashed else "filled,rounded"
    pen = "1.8" if dashed else "1.3"
    parent.node(_nid(label), label=label, color=color, fillcolor=fill,
                style=style, penwidth=pen)


def build_hierarchy_diagram(g: Graph, output_name: str):
    """Class hierarchy + gUFO alignment, in visually grouped clusters."""
    dot = Digraph(
        name="FRAM Ontology v1.8.0 — Class Hierarchy",
        format="svg",
        engine="dot",
        graph_attr=_common_graph_attrs(
            "FRAM Ontology v1.8.0 — Class Hierarchy and gUFO Alignment\n "
        ),
        node_attr=_common_node_attrs(),
        edge_attr=_common_edge_attrs(),
    )

    # --- Curated class lists (30 of 59 classes) ---
    gufo_classes = [
        "gufo:Event", "gufo:Object", "gufo:Disposition",
        "gufo:ExternallyDependentMode", "gufo:Quality", "gufo:Collection",
    ]
    core_classes = ["fram:FRAMModel", "fram:Function", "fram:Aspect", "fram:Coupling"]
    func_nature = ["fram:HumanFunction", "fram:TechnologicalFunction",
                   "fram:OrganisationalFunction"]
    func_role = ["fram:EntryFunction", "fram:ExitFunction",
                 "fram:ForegroundFunction", "fram:BackgroundFunction"]
    aspect_types = ["fram:InputAspect", "fram:OutputAspect", "fram:PreconditionAspect",
                    "fram:ResourceAspect", "fram:ControlAspect", "fram:TimeAspect"]
    var_classes = ["fram:Variability", "fram:NormalDistribution",
                   "fram:Phenotype", "fram:PerformanceCondition"]
    wai_classes = ["fram:WAIDeclaration", "fram:FunctionalResonance",
                   "fram:FRAMScenario"]

    # --- Clusters (visible boxes keep groupings explicit) ---
    with dot.subgraph(name="cluster_core") as c:
        c.attr(label="Core FRAM", style="rounded,filled", color=COLORS["core"],
               fillcolor="#EAF2F8", fontname="Helvetica", fontsize="11",
               fontcolor=COLORS["core"], penwidth="1.5", margin="14")
        for lbl in core_classes:
            _add_node(c, lbl, COLORS["core"], FRAM_FILL)

    with dot.subgraph(name="cluster_functions") as c:
        c.attr(label="Function Specialisations", style="rounded,filled",
               color=COLORS["function_type"], fillcolor="#EBF5FB",
               fontname="Helvetica", fontsize="11",
               fontcolor=COLORS["function_type"], penwidth="1.5", margin="14")
        with c.subgraph(name="cluster_func_nature") as n:
            n.attr(label="by Nature", style="dashed", color="#85C1E9",
                   fontsize="9", fontname="Helvetica", margin="8")
            for lbl in func_nature:
                _add_node(n, lbl, COLORS["function_type"], FRAM_FILL)
        with c.subgraph(name="cluster_func_role") as r:
            r.attr(label="by Role", style="dashed", color="#85C1E9",
                   fontsize="9", fontname="Helvetica", margin="8")
            for lbl in func_role:
                _add_node(r, lbl, COLORS["function_type"], FRAM_FILL)

    with dot.subgraph(name="cluster_aspects") as c:
        c.attr(label="Aspect Subtypes (I / O / P / R / C / T)",
               style="rounded,filled", color=COLORS["aspect"],
               fillcolor="#E8F8F0", fontname="Helvetica", fontsize="11",
               fontcolor=COLORS["aspect"], penwidth="1.5", margin="14")
        for lbl in aspect_types:
            _add_node(c, lbl, COLORS["aspect"], FRAM_FILL)

    with dot.subgraph(name="cluster_var") as c:
        c.attr(label="Variability & Quantitative", style="rounded,filled",
               color=COLORS["variability"], fillcolor="#FDF2E9",
               fontname="Helvetica", fontsize="11",
               fontcolor=COLORS["variability"], penwidth="1.5", margin="14")
        for lbl in var_classes:
            _add_node(c, lbl, COLORS["variability"], VAR_FILL)

    with dot.subgraph(name="cluster_wai") as c:
        c.attr(label="WAI / WAD Analysis", style="rounded,filled",
               color=COLORS["wai_wad"], fillcolor="#F4ECF7",
               fontname="Helvetica", fontsize="11",
               fontcolor=COLORS["wai_wad"], penwidth="1.5", margin="14")
        for lbl in wai_classes:
            _add_node(c, lbl, COLORS["wai_wad"], WAI_FILL)

    with dot.subgraph(name="cluster_gufo") as c:
        c.attr(label="gUFO Foundational Anchors", style="rounded,filled",
               color=COLORS["gufo"], fillcolor="#FBEEE6",
               fontname="Helvetica", fontsize="11",
               fontcolor=COLORS["gufo"], penwidth="1.5", margin="14")
        for lbl in gufo_classes:
            _add_node(c, lbl, COLORS["gufo"], GUFO_FILL, dashed=True)

    # --- Subclass edges within FRAM (short, intra-cluster) ---
    fram_subclass = [
        ("fram:HumanFunction", "fram:Function"),
        ("fram:TechnologicalFunction", "fram:Function"),
        ("fram:OrganisationalFunction", "fram:Function"),
        ("fram:EntryFunction", "fram:Function"),
        ("fram:ExitFunction", "fram:Function"),
        ("fram:ForegroundFunction", "fram:Function"),
        ("fram:BackgroundFunction", "fram:Function"),
        ("fram:InputAspect", "fram:Aspect"),
        ("fram:OutputAspect", "fram:Aspect"),
        ("fram:PreconditionAspect", "fram:Aspect"),
        ("fram:ResourceAspect", "fram:Aspect"),
        ("fram:ControlAspect", "fram:Aspect"),
        ("fram:TimeAspect", "fram:Aspect"),
    ]
    for child, parent in fram_subclass:
        dot.edge(_nid(child), _nid(parent),
                 arrowhead="empty", color="#566573",
                 style="solid", penwidth="1.0", weight="3")

    # --- gUFO alignment edges (FRAM core → gUFO anchors) ---
    gufo_subclass = [
        ("fram:FRAMModel", "gufo:Collection"),
        ("fram:Function", "gufo:Event"),
        ("fram:Aspect", "gufo:ExternallyDependentMode"),
        ("fram:Coupling", "gufo:Object"),
        ("fram:Variability", "gufo:Quality"),
        ("fram:PerformanceCondition", "gufo:Disposition"),
    ]
    for child, parent in gufo_subclass:
        dot.edge(_nid(child), _nid(parent),
                 arrowhead="empty", color=COLORS["gufo"],
                 style="dashed", penwidth="1.4")

    # --- Legend ---
    with dot.subgraph(name="cluster_legend") as legend:
        legend.attr(label="Legend", style="rounded", color="#BDC3C7",
                    fontsize="10", fontname="Helvetica", labeljust="l",
                    margin="10")
        legend.node("leg_core", "Core FRAM", fillcolor=FRAM_FILL,
                    color=COLORS["core"], shape="box",
                    style="filled,rounded", fontsize="9",
                    width="1.6", height="0.30")
        legend.node("leg_func", "Function specialisation", fillcolor=FRAM_FILL,
                    color=COLORS["function_type"], shape="box",
                    style="filled,rounded", fontsize="9",
                    width="1.6", height="0.30")
        legend.node("leg_asp", "Aspect subtype", fillcolor=FRAM_FILL,
                    color=COLORS["aspect"], shape="box",
                    style="filled,rounded", fontsize="9",
                    width="1.6", height="0.30")
        legend.node("leg_var", "Variability / Quantitative", fillcolor=VAR_FILL,
                    color=COLORS["variability"], shape="box",
                    style="filled,rounded", fontsize="9",
                    width="1.6", height="0.30")
        legend.node("leg_wai", "WAI / WAD analysis", fillcolor=WAI_FILL,
                    color=COLORS["wai_wad"], shape="box",
                    style="filled,rounded", fontsize="9",
                    width="1.6", height="0.30")
        legend.node("leg_gufo", "gUFO foundational class",
                    fillcolor=GUFO_FILL, color=COLORS["gufo"], shape="box",
                    style="filled,rounded,dashed", fontsize="9",
                    width="1.6", height="0.30")
        legend.node("leg_sc", "rdfs:subClassOf (FRAM)",
                    color="#566573", shape="box", style="rounded",
                    fontsize="9", fontcolor="#566573",
                    width="1.6", height="0.30", penwidth="1.2")
        legend.node("leg_gsc", "rdfs:subClassOf (gUFO)",
                    color=COLORS["gufo"], shape="box",
                    style="rounded,dashed",
                    fontsize="9", fontcolor=COLORS["gufo"],
                    width="1.6", height="0.30", penwidth="1.4")
        for a, b in [("leg_core", "leg_func"), ("leg_func", "leg_asp"),
                     ("leg_asp", "leg_var"), ("leg_var", "leg_wai"),
                     ("leg_wai", "leg_gufo"), ("leg_gufo", "leg_sc"),
                     ("leg_sc", "leg_gsc")]:
            legend.edge(a, b, style="invis")

    dot.node("annotation",
             label=("Showing 30 of 59 classes  ·  65 Object Properties  ·  "
                    "64 Datatype Properties  ·  1,309 TBox triples\n"
                    "Object-property network in companion figure "
                    "(fram_ontology_properties.svg)"),
             shape="note", style="filled", fillcolor="#FCF3CF",
             color="#F4D03F", fontsize="9", fontname="Helvetica")

    dot.render(output_name, cleanup=True)
    print(f"Generated: {output_name}.svg")
    dot.format = "png"
    dot.attr(dpi="220")
    dot.render(output_name, cleanup=True)
    print(f"Generated: {output_name}.png")


def build_property_diagram(g: Graph, output_name: str):
    """Companion diagram: key object properties as a small network."""
    attrs = _common_graph_attrs(
        "FRAM Ontology v1.8.0 — Key Object Properties (Domain → Range)\n "
    )
    attrs["splines"] = "polyline"
    attrs["ranksep"] = "1.4"
    attrs["nodesep"] = "0.55"

    dot = Digraph(
        name="FRAM Ontology v1.8.0 — Object Properties",
        format="svg",
        engine="dot",
        graph_attr=attrs,
        node_attr=_common_node_attrs(),
        edge_attr=_common_edge_attrs(),
    )

    nodes = [
        ("fram:FRAMScenario", COLORS["wai_wad"], WAI_FILL),
        ("fram:FRAMModel", COLORS["core"], FRAM_FILL),
        ("fram:Function", COLORS["core"], FRAM_FILL),
        ("fram:Coupling", COLORS["core"], FRAM_FILL),
        ("fram:Aspect", COLORS["core"], FRAM_FILL),
        ("fram:Variability", COLORS["variability"], VAR_FILL),
        ("fram:NormalDistribution", COLORS["variability"], VAR_FILL),
        ("fram:Phenotype", COLORS["variability"], VAR_FILL),
        ("fram:PerformanceCondition", COLORS["variability"], VAR_FILL),
        ("fram:WAIDeclaration", COLORS["wai_wad"], WAI_FILL),
    ]
    for label, color, fill in nodes:
        dot.node(_nid(label), label=label, color=color, fillcolor=fill,
                 style="filled,rounded", penwidth="1.3")

    edges = [
        ("fram:FRAMScenario", "fram:FRAMModel", "hasModel"),
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
    ]
    for d, r, prop in edges:
        dot.edge(_nid(d), _nid(r),
                 label=f" {prop} ",
                 arrowhead="vee", color="#2874A6",
                 fontcolor="#1B4F72", style="solid", penwidth="1.1")

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
