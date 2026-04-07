"""Iris encoder: converts natural language intent into a Iris packet.

In production, this would use an LLM to extract the semantic graph from
free-form human input. This reference implementation provides both a
programmatic API and a simple rule-based extractor for demonstration.
"""

from __future__ import annotations

import json
import re

from .packet import (
    Context,
    Direction,
    Edge,
    EdgeType,
    IrisPacket,
    Identity,
    Intent,
    Meta,
    Mode,
    Node,
    Valence,
)

# Keywords that hint at epistemic mode
_MODE_SIGNALS = {
    Mode.PROJECTION: ["hypothesis", "might", "could", "maybe", "possibly", "think", "believe", "suspect"],
    Mode.MANIFEST: ["fact", "proven", "established", "data shows", "evidence"],
    Mode.COLLECTIVE: ["consensus", "widely accepted", "commonly", "everyone agrees"],
    Mode.SUBJECTIVE: ["I feel", "in my opinion", "personally", "I prefer"],
}

# Keywords that hint at edge types
_EDGE_SIGNALS = {
    EdgeType.TENSION: ["tension", "conflict", "versus", "vs", "but", "however", "contradicts"],
    EdgeType.CAUSAL: ["causes", "leads to", "results in", "because", "therefore"],
    EdgeType.SUPPORTS: ["supports", "reinforces", "aligns with", "confirms"],
    EdgeType.CONTRADICTS: ["contradicts", "disproves", "undermines", "refutes"],
    EdgeType.EMERGENCE: ["bridge", "emerges", "resolves", "synthesizes", "combines"],
}


def encode_programmatic(
    sender: Identity,
    receiver: Identity,
    intent: Intent,
    nodes: list[Node],
    edges: list[Edge],
    context: list[Context] | None = None,
    priority: float = 0.5,
    thread_id: str | None = None,
    in_reply_to: str | None = None,
) -> IrisPacket:
    """Build a Iris packet from structured inputs."""
    meta = Meta(
        thread_id=thread_id or Meta().thread_id,
        in_reply_to=in_reply_to,
    )
    return IrisPacket(
        sender=sender,
        receiver=receiver,
        intent=intent,
        nodes=nodes,
        edges=edges,
        context=context or [],
        priority=priority,
        meta=meta,
    )


def _detect_mode(text: str) -> Mode:
    """Detect epistemic mode from natural language cues."""
    text_lower = text.lower()
    for mode, signals in _MODE_SIGNALS.items():
        if any(s in text_lower for s in signals):
            return mode
    return Mode.MANIFEST


def _detect_edge_type(text: str) -> EdgeType:
    """Detect relationship type from natural language cues."""
    text_lower = text.lower()
    for edge_type, signals in _EDGE_SIGNALS.items():
        if any(s in text_lower for s in signals):
            return edge_type
    return EdgeType.SUPPORTS


def _extract_concepts(text: str) -> list[str]:
    """Extract key concepts from text using simple heuristics.

    In production, an LLM would do this extraction.
    """
    # Look for quoted terms first
    quoted = re.findall(r'"([^"]+)"', text)
    if quoted:
        return quoted

    # Look for capitalized multi-word phrases (proper nouns / key concepts)
    phrases = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', text)
    if phrases:
        return phrases

    # Fallback: extract nouns-ish words (rough heuristic)
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "shall", "can", "that",
        "this", "these", "those", "it", "its", "they", "them", "their",
        "we", "our", "you", "your", "he", "she", "him", "her", "his",
        "and", "or", "but", "if", "then", "than", "so", "for", "of",
        "in", "on", "at", "to", "from", "by", "with", "about", "into",
        "not", "no", "also", "very", "just", "both", "each", "all",
        "tell", "said", "think", "know", "see", "look", "like",
    }
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
    concepts = []
    seen = set()
    for w in words:
        w_lower = w.lower()
        if w_lower not in stop_words and w_lower not in seen:
            seen.add(w_lower)
            concepts.append(w_lower)
    return concepts[:5]  # Cap at 5 concepts


def encode_natural(
    text: str,
    sender: Identity,
    receiver: Identity,
) -> IrisPacket:
    """Encode natural language into a Iris packet.

    This is a simplified demonstration. In production, you would call an LLM
    to extract the semantic graph, epistemic modes, and relationships.
    """
    mode = _detect_mode(text)
    edge_type = _detect_edge_type(text)
    concepts = _extract_concepts(text)

    # Determine intent from text
    text_lower = text.lower()
    if any(w in text_lower for w in ["tell", "inform", "share", "let them know"]):
        intent = Intent.INFORM
    elif any(w in text_lower for w in ["ask", "request", "what", "how", "?"]):
        intent = Intent.REQUEST
    elif any(w in text_lower for w in ["propose", "suggest", "idea", "what if"]):
        intent = Intent.PROPOSE
    elif any(w in text_lower for w in ["disagree", "challenge", "wrong", "incorrect"]):
        intent = Intent.CHALLENGE
    else:
        intent = Intent.INFORM

    # Build nodes from extracted concepts
    nodes = []
    for concept in concepts:
        node = Node(
            stem=concept.replace(" ", "-").lower(),
            mode=mode,
            valence=Valence.POSITIVE,
            amplitude=0.5,
            definition=concept,
        )
        nodes.append(node)

    # Build edges between nodes
    edges = []
    if len(nodes) >= 2:
        # Connect first two nodes with detected edge type
        edges.append(Edge(
            type=edge_type,
            nodes=[nodes[0].id, nodes[1].id],
            direction=Direction.BIDIRECTIONAL if edge_type == EdgeType.TENSION else Direction.FORWARD,
            weight=0.7,
            relator=f"{nodes[0].stem} {edge_type.value} {nodes[1].stem}",
        ))

    if len(nodes) >= 3:
        # Create a hyperedge connecting all nodes
        edges.append(Edge(
            type=EdgeType.EMERGENCE,
            nodes=[n.id for n in nodes],
            direction=Direction.UNDIRECTED,
            weight=0.5,
            relator=f"Composite relationship across {', '.join(n.stem for n in nodes)}",
        ))

    return IrisPacket(
        sender=sender,
        receiver=receiver,
        intent=intent,
        nodes=nodes,
        edges=edges,
        priority=0.5,
    )


def to_json(packet: IrisPacket, indent: int = 2) -> str:
    """Serialize a packet to JSON."""
    return json.dumps(packet.to_dict(), indent=indent)
