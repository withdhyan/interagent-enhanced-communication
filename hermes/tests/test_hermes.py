#!/usr/bin/env python3
"""Tests for the Hermes protocol implementation."""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.packet import (
    Context,
    Direction,
    Edge,
    EdgeType,
    HermesPacket,
    Identity,
    Intent,
    Meta,
    Mode,
    Node,
    Valence,
)
from src.encoder import encode_natural, encode_programmatic, to_json
from src.decoder import decode_to_natural_language, decode_to_structured


def test_node_creation():
    n = Node(stem="climate", mode=Mode.MANIFEST, valence=Valence.POSITIVE, amplitude=0.8)
    d = n.to_dict()
    assert d["stem"] == "climate"
    assert d["mode"] == "manifest"
    assert d["valence"] == "+"
    assert d["amplitude"] == 0.8
    assert d["id"].startswith("n-")
    print("  PASS: test_node_creation")


def test_edge_creation():
    e = Edge(type=EdgeType.CAUSAL, nodes=["n1", "n2"], direction=Direction.FORWARD, weight=0.7)
    d = e.to_dict()
    assert d["type"] == "causal"
    assert d["nodes"] == ["n1", "n2"]
    assert d["direction"] == "->"
    assert d["weight"] == 0.7
    print("  PASS: test_edge_creation")


def test_edge_undirected_serializes_null():
    e = Edge(type=EdgeType.EMERGENCE, nodes=["n1", "n2", "n3"])
    d = e.to_dict()
    assert d["direction"] is None
    print("  PASS: test_edge_undirected_serializes_null")


def test_packet_to_dict_and_back():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")

    packet = HermesPacket(
        sender=alice,
        receiver=bob,
        intent=Intent.INFORM,
        priority=0.8,
    )
    n1 = packet.add_node("solar-energy", mode=Mode.MANIFEST, amplitude=0.9)
    n2 = packet.add_node("grid-stability", mode=Mode.PROJECTION, valence=Valence.NEGATIVE)
    packet.add_edge(EdgeType.TENSION, [n1.id, n2.id], weight=0.7, relator="Intermittency risk")
    packet.add_context("NREL Report", "Solar penetration above 30% requires grid upgrades", supports_nodes=[n1.id])

    d = packet.to_dict()
    assert d["hermes"] == "0.1"
    assert d["from"]["human"] == "Alice"
    assert d["to"]["agent"] == "gemini"
    assert d["intent"] == "inform"
    assert len(d["graph"]["nodes"]) == 2
    assert len(d["graph"]["edges"]) == 1
    assert len(d["context"]) == 1

    # Round-trip
    restored = HermesPacket.from_dict(d)
    assert restored.sender.human == "Alice"
    assert restored.nodes[0].stem == "solar-energy"
    assert restored.edges[0].relator == "Intermittency risk"
    assert restored.context[0].source == "NREL Report"
    print("  PASS: test_packet_to_dict_and_back")


def test_json_serialization():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")
    packet = encode_programmatic(
        sender=alice, receiver=bob, intent=Intent.PROPOSE,
        nodes=[Node(stem="test-concept")],
        edges=[],
    )
    j = to_json(packet)
    parsed = json.loads(j)
    assert parsed["hermes"] == "0.1"
    assert parsed["intent"] == "propose"
    print("  PASS: test_json_serialization")


def test_encode_natural_extracts_quoted_concepts():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")
    packet = encode_natural(
        '"machine learning" and "data privacy" are in tension',
        sender=alice, receiver=bob,
    )
    stems = [n.stem for n in packet.nodes]
    assert "machine-learning" in stems
    assert "data-privacy" in stems
    print("  PASS: test_encode_natural_extracts_quoted_concepts")


def test_encode_natural_detects_hypothesis_mode():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")
    packet = encode_natural(
        'I think "quantum computing" might disrupt "encryption"',
        sender=alice, receiver=bob,
    )
    for node in packet.nodes:
        assert node.mode == Mode.PROJECTION, f"Expected projection, got {node.mode}"
    print("  PASS: test_encode_natural_detects_hypothesis_mode")


def test_encode_natural_detects_tension_edge():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")
    packet = encode_natural(
        '"speed" and "safety" are in tension',
        sender=alice, receiver=bob,
    )
    assert any(e.type == EdgeType.TENSION for e in packet.edges)
    print("  PASS: test_encode_natural_detects_tension_edge")


def test_encode_natural_detects_request_intent():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")
    packet = encode_natural(
        'Ask Bob what he thinks about "serverless architecture"?',
        sender=alice, receiver=bob,
    )
    assert packet.intent == Intent.REQUEST
    print("  PASS: test_encode_natural_detects_request_intent")


def test_decode_to_natural_language():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")

    packet = HermesPacket(sender=alice, receiver=bob, intent=Intent.INFORM)
    n1 = packet.add_node("renewable-energy", mode=Mode.MANIFEST, amplitude=0.8,
                          definition="Solar and wind power")
    n2 = packet.add_node("cost-reduction", mode=Mode.PROJECTION, amplitude=0.6,
                          definition="Falling costs of renewables")
    packet.add_edge(EdgeType.SUPPORTS, [n1.id, n2.id], weight=0.7,
                    relator="More deployment drives cost curves down")

    output = decode_to_natural_language(packet)
    assert "Alice" in output
    assert "shared an insight" in output
    assert "renewable-energy" in output
    assert "supports" in output
    print("  PASS: test_decode_to_natural_language")


def test_decode_to_structured():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")

    packet = HermesPacket(sender=alice, receiver=bob, intent=Intent.CHALLENGE)
    n1 = packet.add_node("claim-a", definition="Some claim")
    packet.add_context("Paper X", "Contradicts claim A", supports_nodes=[n1.id])

    result = decode_to_structured(packet)
    assert result["sender"] == "Alice"
    assert result["intent"] == "challenge"
    assert len(result["concepts"]) == 1
    assert len(result["sources"]) == 1
    assert result["sources"][0]["reference"] == "Paper X"
    print("  PASS: test_decode_to_structured")


def test_hyperedge_three_plus_nodes():
    """Hyperedges can connect 3+ nodes — this is what makes it a hypergraph."""
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")

    packet = HermesPacket(sender=alice, receiver=bob, intent=Intent.INFORM)
    n1 = packet.add_node("node-a", definition="A")
    n2 = packet.add_node("node-b", definition="B")
    n3 = packet.add_node("node-c", definition="C")
    e = packet.add_edge(EdgeType.EMERGENCE, [n1.id, n2.id, n3.id],
                        relator="Triangular relationship")

    assert len(e.nodes) == 3
    d = packet.to_dict()
    assert len(d["graph"]["edges"][0]["nodes"]) == 3

    # Round-trip
    restored = HermesPacket.from_dict(d)
    assert len(restored.edges[0].nodes) == 3

    # Decode handles it
    output = decode_to_natural_language(packet)
    assert "node-a" in output
    assert "node-b" in output
    assert "node-c" in output
    print("  PASS: test_hyperedge_three_plus_nodes")


def test_meta_thread_tracking():
    meta = Meta(thread_id="thread-123", in_reply_to="packet-456")
    d = meta.to_dict()
    assert d["thread_id"] == "thread-123"
    assert d["in_reply_to"] == "packet-456"
    print("  PASS: test_meta_thread_tracking")


# ===== Run all tests =====

def run_all():
    tests = [
        test_node_creation,
        test_edge_creation,
        test_edge_undirected_serializes_null,
        test_packet_to_dict_and_back,
        test_json_serialization,
        test_encode_natural_extracts_quoted_concepts,
        test_encode_natural_detects_hypothesis_mode,
        test_encode_natural_detects_tension_edge,
        test_encode_natural_detects_request_intent,
        test_decode_to_natural_language,
        test_decode_to_structured,
        test_hyperedge_three_plus_nodes,
        test_meta_thread_tracking,
    ]

    print(f"Running {len(tests)} tests...\n")
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__} — {e}")
            failed += 1

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    if failed > 0:
        sys.exit(1)
    print("All tests passed!")


if __name__ == "__main__":
    run_all()
