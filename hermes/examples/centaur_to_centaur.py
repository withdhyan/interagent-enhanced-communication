#!/usr/bin/env python3
"""
Example: Centaur-to-Centaur communication via Hermes.

This demonstrates the full flow:
  1. Alice tells her AI what she wants to communicate (natural language)
  2. Alice's AI encodes it into a Hermes packet (structured hypergraph)
  3. The packet is transmitted (JSON over any transport)
  4. Bob's AI decodes the packet back into natural language for Bob

Neither Alice nor Bob ever sees the wire format.
"""

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

SEPARATOR = "=" * 60


def demo_programmatic():
    """Build a packet using the programmatic API (full control)."""
    print(f"\n{SEPARATOR}")
    print("DEMO 1: Programmatic Encoding (Full Control)")
    print(SEPARATOR)

    alice = Identity(agent="claude-opus-4-6", human="Alice")
    bob = Identity(agent="gemini-2.5-pro", human="Bob")

    # Alice's AI builds the packet with precise semantic structure
    n1 = Node(
        stem="climate-reform",
        mode=Mode.MANIFEST,
        valence=Valence.POSITIVE,
        amplitude=0.9,
        definition="Policy changes targeting carbon emission reduction",
    )
    n2 = Node(
        stem="economic-growth",
        mode=Mode.PROJECTION,
        valence=Valence.EMERGENT,
        amplitude=0.7,
        definition="GDP trajectory under proposed reforms",
    )
    n3 = Node(
        stem="carbon-capture",
        mode=Mode.PROJECTION,
        valence=Valence.POSITIVE,
        amplitude=0.5,
        definition="Emergent tech for atmospheric CO2 removal",
    )

    e1 = Edge(
        type=EdgeType.TENSION,
        nodes=[n1.id, n2.id],
        direction=Direction.BIDIRECTIONAL,
        weight=0.8,
        relator="Reforms may slow growth short-term",
    )
    e2 = Edge(
        type=EdgeType.EMERGENCE,
        nodes=[n1.id, n2.id, n3.id],
        direction=Direction.UNDIRECTED,
        weight=0.6,
        relator="Carbon capture could bridge both goals",
    )

    ctx = Context(
        source="IPCC AR6 WG3",
        span="chapter-14:1402-1450",
        summary="Mitigation pathways compatible with 1.5C require 43% CO2 reduction by 2030",
        supports_nodes=[n1.id],
    )

    packet = encode_programmatic(
        sender=alice,
        receiver=bob,
        intent=Intent.INFORM,
        nodes=[n1, n2, n3],
        edges=[e1, e2],
        context=[ctx],
        priority=0.8,
    )

    # === THE WIRE ===
    wire_json = to_json(packet)

    print("\n--- Alice says to her AI ---")
    print('"Tell Bob that climate reform and economic growth are in tension,')
    print(' but carbon capture might bridge both. Reference the IPCC data."')

    print(f"\n--- On the wire ({len(wire_json)} bytes) ---")
    print(wire_json[:300] + "..." if len(wire_json) > 300 else wire_json)

    # === BOB'S SIDE ===
    received = HermesPacket.from_dict(packet.to_dict())
    human_output = decode_to_natural_language(received)

    print("\n--- Bob's AI tells Bob ---")
    print(human_output)

    return packet


def demo_natural_language():
    """Build a packet from free-form natural language input."""
    print(f"\n{SEPARATOR}")
    print("DEMO 2: Natural Language Encoding (AI extracts structure)")
    print(SEPARATOR)

    alice = Identity(agent="claude-opus-4-6", human="Alice")
    bob = Identity(agent="gemini-2.5-pro", human="Bob")

    # Alice just talks naturally
    alice_says = (
        'Tell Bob I think "distributed systems" and "consensus protocols" '
        'are in tension with "low latency" requirements. '
        'But "CRDTs" might bridge the gap. This is my hypothesis.'
    )

    print(f"\n--- Alice says ---")
    print(f'"{alice_says}"')

    packet = encode_natural(alice_says, sender=alice, receiver=bob)

    wire_json = to_json(packet)
    print(f"\n--- On the wire ({len(wire_json)} bytes) ---")
    print(wire_json[:300] + "..." if len(wire_json) > 300 else wire_json)

    received = HermesPacket.from_dict(packet.to_dict())
    human_output = decode_to_natural_language(received)

    print("\n--- Bob's AI tells Bob ---")
    print(human_output)


def demo_challenge_response():
    """Show a multi-turn exchange: inform -> challenge -> inform."""
    print(f"\n{SEPARATOR}")
    print("DEMO 3: Multi-Turn Exchange (Inform -> Challenge -> Respond)")
    print(SEPARATOR)

    alice = Identity(agent="claude-opus-4-6", human="Alice")
    bob = Identity(agent="gemini-2.5-pro", human="Bob")
    thread_id = "thread-climate-debate-001"

    # Turn 1: Alice informs
    n1 = Node(stem="renewable-energy", mode=Mode.MANIFEST, amplitude=0.8,
              definition="Solar and wind power generation")
    n2 = Node(stem="grid-stability", mode=Mode.PROJECTION, valence=Valence.NEGATIVE, amplitude=0.6,
              definition="Power grid reliability under high renewable load")

    packet1 = encode_programmatic(
        sender=alice, receiver=bob, intent=Intent.INFORM,
        nodes=[n1, n2],
        edges=[Edge(type=EdgeType.TENSION, nodes=[n1.id, n2.id],
                    direction=Direction.FORWARD, weight=0.7,
                    relator="High renewable penetration may destabilize the grid")],
        thread_id=thread_id,
    )

    print("\n--- Turn 1: Alice informs ---")
    print(decode_to_natural_language(packet1))

    # Turn 2: Bob challenges
    n3 = Node(stem="battery-storage", mode=Mode.MANIFEST, amplitude=0.9,
              definition="Grid-scale battery technology")

    packet2 = encode_programmatic(
        sender=bob, receiver=alice, intent=Intent.CHALLENGE,
        nodes=[n3],
        edges=[Edge(type=EdgeType.CONTRADICTS, nodes=[n3.id, n2.id],
                    direction=Direction.FORWARD, weight=0.8,
                    relator="Battery storage solves grid stability concerns")],
        thread_id=thread_id,
        in_reply_to=packet1.id,
    )

    print("\n--- Turn 2: Bob challenges ---")
    print(decode_to_natural_language(packet2))

    # Turn 3: Alice acknowledges and extends
    n4 = Node(stem="rare-earth-supply", mode=Mode.MANIFEST, valence=Valence.NEGATIVE, amplitude=0.7,
              definition="Limited supply of minerals needed for batteries")

    packet3 = encode_programmatic(
        sender=alice, receiver=bob, intent=Intent.PROPOSE,
        nodes=[n4],
        edges=[Edge(type=EdgeType.TENSION, nodes=[n3.id, n4.id],
                    direction=Direction.BACKWARD, weight=0.6,
                    relator="Battery scaling constrained by rare earth supply chains")],
        thread_id=thread_id,
        in_reply_to=packet2.id,
    )

    print("\n--- Turn 3: Alice proposes ---")
    print(decode_to_natural_language(packet3))


if __name__ == "__main__":
    demo_programmatic()
    demo_natural_language()
    demo_challenge_response()
