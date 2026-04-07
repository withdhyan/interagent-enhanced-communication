"""Iris packet data structures."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class Intent(str, Enum):
    INFORM = "inform"
    REQUEST = "request"
    PROPOSE = "propose"
    CHALLENGE = "challenge"
    ACKNOWLEDGE = "acknowledge"


class Mode(str, Enum):
    MANIFEST = "manifest"        # Hard fact / physical reality
    PROJECTION = "projection"    # Hypothesis / mental model
    COLLECTIVE = "collective"    # Consensus / cultural norm
    SUBJECTIVE = "subjective"    # Personal opinion


class Valence(str, Enum):
    POSITIVE = "+"       # Constructive
    NEGATIVE = "-"       # Destructive
    EMERGENT = "^"       # Novel / emergent
    UNCERTAIN = "~"      # Uncertain


class EdgeType(str, Enum):
    CAUSAL = "causal"
    TENSION = "tension"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EMERGENCE = "emergence"
    TEMPORAL = "temporal"
    CONTAINS = "contains"


class Direction(str, Enum):
    FORWARD = "->"
    BACKWARD = "<-"
    BIDIRECTIONAL = "<->"
    UNDIRECTED = "none"


@dataclass
class Node:
    stem: str
    mode: Mode = Mode.MANIFEST
    valence: Valence = Valence.POSITIVE
    amplitude: float = 0.5
    definition: str = ""
    id: str = field(default_factory=lambda: f"n-{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "stem": self.stem,
            "mode": self.mode.value,
            "valence": self.valence.value,
            "amplitude": self.amplitude,
            "definition": self.definition,
        }


@dataclass
class Edge:
    type: EdgeType
    nodes: list[str]  # node IDs
    direction: Direction = Direction.UNDIRECTED
    weight: float = 0.5
    relator: str = ""
    id: str = field(default_factory=lambda: f"e-{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "nodes": self.nodes,
            "direction": self.direction.value if self.direction != Direction.UNDIRECTED else None,
            "weight": self.weight,
            "relator": self.relator,
        }


@dataclass
class Context:
    source: str
    summary: str
    supports_nodes: list[str] = field(default_factory=list)
    span: str = ""
    url: str = ""
    id: str = field(default_factory=lambda: f"c-{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "span": self.span,
            "url": self.url,
            "summary": self.summary,
            "supports_nodes": self.supports_nodes,
        }


@dataclass
class Identity:
    agent: str
    human: str = ""

    def to_dict(self) -> dict:
        return {"agent": self.agent, "human": self.human}


@dataclass
class Meta:
    expecting_response: bool = True
    thread_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    in_reply_to: Optional[str] = None
    human_override: bool = False
    ttl: int = 3600

    def to_dict(self) -> dict:
        d = {
            "compression": "semantic-v1",
            "expecting_response": self.expecting_response,
            "thread_id": self.thread_id,
            "human_override": self.human_override,
            "ttl": self.ttl,
        }
        if self.in_reply_to:
            d["in_reply_to"] = self.in_reply_to
        return d


@dataclass
class IrisPacket:
    """A single Iris protocol message."""

    sender: Identity
    receiver: Identity
    intent: Intent
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    context: list[Context] = field(default_factory=list)
    priority: float = 0.5
    meta: Meta = field(default_factory=Meta)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_node(self, stem: str, **kwargs) -> Node:
        node = Node(stem=stem, **kwargs)
        self.nodes.append(node)
        return node

    def add_edge(self, edge_type: EdgeType, node_ids: list[str], **kwargs) -> Edge:
        edge = Edge(type=edge_type, nodes=node_ids, **kwargs)
        self.edges.append(edge)
        return edge

    def add_context(self, source: str, summary: str, **kwargs) -> Context:
        ctx = Context(source=source, summary=summary, **kwargs)
        self.context.append(ctx)
        return ctx

    def to_dict(self) -> dict:
        return {
            "iris": "0.1",
            "id": self.id,
            "timestamp": self.timestamp,
            "from": self.sender.to_dict(),
            "to": self.receiver.to_dict(),
            "intent": self.intent.value,
            "priority": self.priority,
            "graph": {
                "nodes": [n.to_dict() for n in self.nodes],
                "edges": [e.to_dict() for e in self.edges],
            },
            "context": [c.to_dict() for c in self.context],
            "meta": self.meta.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> IrisPacket:
        """Reconstruct a packet from its dict representation."""
        nodes = [
            Node(
                id=n["id"],
                stem=n["stem"],
                mode=Mode(n["mode"]),
                valence=Valence(n["valence"]),
                amplitude=n["amplitude"],
                definition=n.get("definition", ""),
            )
            for n in data["graph"]["nodes"]
        ]
        edges = [
            Edge(
                id=e["id"],
                type=EdgeType(e["type"]),
                nodes=e["nodes"],
                direction=Direction(e["direction"]) if e.get("direction") else Direction.UNDIRECTED,
                weight=e["weight"],
                relator=e.get("relator", ""),
            )
            for e in data["graph"]["edges"]
        ]
        context = [
            Context(
                id=c["id"],
                source=c["source"],
                span=c.get("span", ""),
                url=c.get("url", ""),
                summary=c["summary"],
                supports_nodes=c.get("supports_nodes", []),
            )
            for c in data.get("context", [])
        ]

        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            sender=Identity(**data["from"]),
            receiver=Identity(**data["to"]),
            intent=Intent(data["intent"]),
            priority=data.get("priority", 0.5),
            nodes=nodes,
            edges=edges,
            context=context,
            meta=Meta(
                expecting_response=data["meta"].get("expecting_response", True),
                thread_id=data["meta"].get("thread_id", ""),
                in_reply_to=data["meta"].get("in_reply_to"),
                human_override=data["meta"].get("human_override", False),
                ttl=data["meta"].get("ttl", 3600),
            ),
        )
