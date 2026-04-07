"""Iris decoder: converts a Iris packet into human-readable output.

The decoder is what the receiving centaur's AI uses to "unpack" a
Iris packet into natural language, a summary, or a structured view
that the human can understand.
"""

from __future__ import annotations

import json

from .packet import Direction, EdgeType, IrisPacket, Mode, Valence


def _mode_label(mode: Mode) -> str:
    return {
        Mode.MANIFEST: "states as fact",
        Mode.PROJECTION: "hypothesizes",
        Mode.COLLECTIVE: "notes the consensus is",
        Mode.SUBJECTIVE: "believes",
    }[mode]


def _valence_symbol(valence: Valence) -> str:
    return {
        Valence.POSITIVE: "(+)",
        Valence.NEGATIVE: "(-)",
        Valence.EMERGENT: "(^)",
        Valence.UNCERTAIN: "(~)",
    }[valence]


def _amplitude_word(amp: float) -> str:
    if amp >= 0.8:
        return "strongly"
    if amp >= 0.5:
        return ""
    if amp >= 0.3:
        return "tentatively"
    return "weakly"


def _edge_verb(edge_type: EdgeType, direction: Direction) -> str:
    verbs = {
        EdgeType.CAUSAL: "causes",
        EdgeType.TENSION: "is in tension with",
        EdgeType.SUPPORTS: "supports",
        EdgeType.CONTRADICTS: "contradicts",
        EdgeType.EMERGENCE: "emerges from the interaction of",
        EdgeType.TEMPORAL: "follows",
        EdgeType.CONTAINS: "contains",
    }
    return verbs.get(edge_type, "relates to")


def decode_to_natural_language(packet: IrisPacket) -> str:
    """Decode a Iris packet into a natural language summary for a human."""
    sender_name = packet.sender.human or packet.sender.agent
    intent_verb = {
        "inform": "shared an insight",
        "request": "is asking",
        "propose": "has a proposal",
        "challenge": "is challenging a point",
        "acknowledge": "acknowledged",
    }.get(packet.intent.value, "sent a message")

    lines = [f"**{sender_name}** {intent_verb}:\n"]

    # Build a node lookup
    node_map = {n.id: n for n in packet.nodes}

    # Describe the key concepts
    if packet.nodes:
        lines.append("**Key concepts:**")
        for node in packet.nodes:
            amp_word = _amplitude_word(node.amplitude)
            mode_word = _mode_label(node.mode)
            val = _valence_symbol(node.valence)
            desc = node.definition or node.stem
            emphasis = f" {amp_word}" if amp_word else ""
            lines.append(f"  - {desc} {val} — {mode_word}{emphasis} (importance: {node.amplitude:.0%})")
        lines.append("")

    # Describe relationships
    if packet.edges:
        lines.append("**Relationships:**")
        for edge in packet.edges:
            edge_nodes = [node_map[nid] for nid in edge.nodes if nid in node_map]
            if len(edge_nodes) == 2:
                a, b = edge_nodes
                verb = _edge_verb(edge.type, edge.direction)
                lines.append(f"  - **{a.stem}** {verb} **{b.stem}** (strength: {edge.weight:.0%})")
            elif len(edge_nodes) > 2:
                names = [n.stem for n in edge_nodes]
                verb = _edge_verb(edge.type, edge.direction)
                joined = ", ".join(f"**{n}**" for n in names[:-1]) + f" and **{names[-1]}**"
                lines.append(f"  - {edge.type.value}: {joined} are connected — {edge.relator} (strength: {edge.weight:.0%})")

            if edge.relator and len(edge_nodes) == 2:
                lines.append(f"    _{edge.relator}_")
        lines.append("")

    # Show sources
    if packet.context:
        lines.append("**Sources:**")
        for ctx in packet.context:
            ref = f"{ctx.source}"
            if ctx.span:
                ref += f" ({ctx.span})"
            lines.append(f"  - [{ref}]: {ctx.summary}")
            if ctx.url:
                lines.append(f"    Link: {ctx.url}")
        lines.append("")

    # Response expectation
    if packet.meta.expecting_response:
        lines.append("_Awaiting your response._")

    return "\n".join(lines)


def decode_to_structured(packet: IrisPacket) -> dict:
    """Decode a packet into a structured summary dict (for UIs or further processing)."""
    node_map = {n.id: n for n in packet.nodes}

    return {
        "sender": packet.sender.human or packet.sender.agent,
        "intent": packet.intent.value,
        "priority": packet.priority,
        "concepts": [
            {
                "name": n.stem,
                "definition": n.definition,
                "status": n.mode.value,
                "importance": n.amplitude,
                "valence": n.valence.value,
            }
            for n in packet.nodes
        ],
        "relationships": [
            {
                "type": e.type.value,
                "between": [node_map[nid].stem for nid in e.nodes if nid in node_map],
                "strength": e.weight,
                "explanation": e.relator,
            }
            for e in packet.edges
        ],
        "sources": [
            {"reference": c.source, "summary": c.summary}
            for c in packet.context
        ],
        "awaiting_response": packet.meta.expecting_response,
    }


def decode_to_json(packet: IrisPacket, indent: int = 2) -> str:
    """Decode a packet into a structured JSON summary."""
    return json.dumps(decode_to_structured(packet), indent=indent)
