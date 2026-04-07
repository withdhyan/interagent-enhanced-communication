#!/usr/bin/env python3
"""
Benchmark: Plain English vs Iris Protocol

Measures token efficiency, information density, and structural richness
across a set of realistic communication scenarios.

"Tokens" here are approximated as word count / 0.75 (average tokens per word
for English text with GPT/Claude tokenizers).
"""

import json
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.packet import (
    Context,
    Direction,
    Edge,
    EdgeType,
    IrisPacket,
    Identity,
    Intent,
    Mode,
    Node,
    Valence,
)
from src.encoder import encode_programmatic, to_json
from src.decoder import decode_to_natural_language


def approx_tokens(text: str) -> int:
    """Approximate token count (words / 0.75)."""
    return int(len(text.split()) / 0.75)


# ============================================================
# Test scenarios: each has a plain English version and a
# Iris packet encoding the same information
# ============================================================

SCENARIOS = []


def scenario(name, plain_english, build_packet_fn):
    SCENARIOS.append((name, plain_english, build_packet_fn))


# --- Scenario 1: Climate Policy ---
scenario(
    "Climate Policy Debate",
    """Hi Bob, I wanted to share some thoughts with you about the climate situation.
    I've been looking into this quite a bit and I think there's a real tension between
    pushing for aggressive climate reform and maintaining economic growth. The data from
    the IPCC AR6 report, specifically chapter 14 around pages 1402-1450, shows that we
    need a 43% CO2 reduction by 2030 to stay on track for 1.5 degrees. That's a huge
    number. However, I think carbon capture technology could potentially bridge both
    goals - it's still emerging but shows promise. I'd rate my confidence in the
    reform-growth tension as quite high, but the carbon capture bridge is more of a
    hypothesis at this point. What do you think? I'd love to hear your perspective on
    this. Looking forward to your response.""",
    lambda: _build_climate_packet(),
)


def _build_climate_packet():
    alice = Identity(agent="claude", human="Alice")
    bob = Identity(agent="gemini", human="Bob")
    n1 = Node(stem="climate-reform", mode=Mode.MANIFEST, valence=Valence.POSITIVE, amplitude=0.9,
              definition="Policy changes targeting carbon emission reduction")
    n2 = Node(stem="economic-growth", mode=Mode.PROJECTION, valence=Valence.EMERGENT, amplitude=0.7,
              definition="GDP trajectory under proposed reforms")
    n3 = Node(stem="carbon-capture", mode=Mode.PROJECTION, valence=Valence.POSITIVE, amplitude=0.5,
              definition="Emergent tech for atmospheric CO2 removal")
    e1 = Edge(type=EdgeType.TENSION, nodes=[n1.id, n2.id], direction=Direction.BIDIRECTIONAL,
              weight=0.8, relator="Reforms may slow growth short-term")
    e2 = Edge(type=EdgeType.EMERGENCE, nodes=[n1.id, n2.id, n3.id],
              weight=0.6, relator="Carbon capture could bridge both goals")
    ctx = Context(source="IPCC AR6 WG3", span="ch14:1402-1450",
                  summary="Mitigation pathways: 43% CO2 reduction by 2030 for 1.5C",
                  supports_nodes=[n1.id])
    return encode_programmatic(sender=alice, receiver=bob, intent=Intent.INFORM,
                               nodes=[n1, n2, n3], edges=[e1, e2], context=[ctx], priority=0.8)


# --- Scenario 2: Tech Architecture ---
scenario(
    "Distributed Systems Architecture",
    """Hey team, I've been thinking about our architecture choices and wanted to raise
    some concerns. Our current distributed system relies heavily on consensus protocols
    like Raft and Paxos, which are well-proven and reliable. However, these consensus
    mechanisms fundamentally conflict with our low-latency requirements for the real-time
    trading platform. Every write operation requires a quorum, which adds significant
    overhead. I'd like to propose that we explore CRDTs (Conflict-free Replicated Data
    Types) as a potential solution. They offer eventual consistency without the coordination
    overhead, which could give us both the distribution we need and the latency targets
    we're missing. This is still a hypothesis on my part - I haven't benchmarked it yet.
    But the theoretical properties are promising. Can we discuss this in the next arch
    review? Thanks!""",
    lambda: _build_arch_packet(),
)


def _build_arch_packet():
    alice = Identity(agent="claude", human="Alice")
    team = Identity(agent="any", human="engineering-team")
    n1 = Node(stem="consensus-protocols", mode=Mode.MANIFEST, amplitude=0.8,
              definition="Raft/Paxos distributed agreement")
    n2 = Node(stem="low-latency", mode=Mode.MANIFEST, valence=Valence.POSITIVE, amplitude=0.9,
              definition="Sub-millisecond response requirement")
    n3 = Node(stem="crdts", mode=Mode.PROJECTION, valence=Valence.EMERGENT, amplitude=0.6,
              definition="Conflict-free replicated data types")
    e1 = Edge(type=EdgeType.TENSION, nodes=[n1.id, n2.id], direction=Direction.BIDIRECTIONAL,
              weight=0.8, relator="Quorum overhead conflicts with latency targets")
    e2 = Edge(type=EdgeType.EMERGENCE, nodes=[n1.id, n2.id, n3.id],
              weight=0.5, relator="CRDTs may resolve consensus-latency tradeoff")
    return encode_programmatic(sender=alice, receiver=team, intent=Intent.PROPOSE,
                               nodes=[n1, n2, n3], edges=[e1, e2], priority=0.7)


# --- Scenario 3: Research Disagreement ---
scenario(
    "Research Methodology Challenge",
    """Dr. Chen, I appreciate your recent paper on transformer scaling laws, but I have
    to respectfully disagree with your main conclusion. You argue that model performance
    scales predictably with parameter count, citing the Chinchilla results. However, the
    recent work by Hoffmann et al. (2024) on data-constrained scaling shows that the
    relationship breaks down when training data quality varies significantly. Specifically,
    their Table 3 demonstrates a 15% performance gap between high-quality and low-quality
    data at the same parameter count. I believe the scaling relationship is actually
    mediated by data quality, not purely by parameter count. This isn't just a minor
    caveat - it fundamentally changes the investment calculus for large model training.
    I look forward to your response.""",
    lambda: _build_research_packet(),
)


def _build_research_packet():
    reviewer = Identity(agent="claude", human="Dr. Smith")
    author = Identity(agent="gemini", human="Dr. Chen")
    n1 = Node(stem="parameter-scaling", mode=Mode.COLLECTIVE, amplitude=0.7,
              definition="Model performance scales with parameter count")
    n2 = Node(stem="data-quality-mediation", mode=Mode.PROJECTION, valence=Valence.EMERGENT, amplitude=0.8,
              definition="Data quality mediates the scaling relationship")
    n3 = Node(stem="training-investment", mode=Mode.MANIFEST, valence=Valence.NEGATIVE, amplitude=0.7,
              definition="ROI calculus for large model training")
    e1 = Edge(type=EdgeType.CONTRADICTS, nodes=[n2.id, n1.id], direction=Direction.FORWARD,
              weight=0.8, relator="Data quality variance breaks predictable scaling")
    e2 = Edge(type=EdgeType.CAUSAL, nodes=[n2.id, n3.id], direction=Direction.FORWARD,
              weight=0.7, relator="If scaling is data-mediated, training ROI changes fundamentally")
    ctx = Context(source="Hoffmann et al. 2024", span="Table 3",
                  summary="15% performance gap between high/low quality data at same param count",
                  supports_nodes=[n2.id])
    return encode_programmatic(sender=reviewer, receiver=author, intent=Intent.CHALLENGE,
                               nodes=[n1, n2, n3], edges=[e1, e2], context=[ctx], priority=0.9)


# --- Scenario 4: Simple Status Update ---
scenario(
    "Simple Status Update",
    """Hey, just wanted to let you know that the deployment went smoothly. All services
    are green, latency is within normal bounds, and we haven't seen any errors in the
    last hour. The new caching layer seems to be working as expected. No action needed
    from your side.""",
    lambda: _build_status_packet(),
)


def _build_status_packet():
    ops = Identity(agent="claude", human="DevOps")
    lead = Identity(agent="gemini", human="Tech Lead")
    n1 = Node(stem="deployment", mode=Mode.MANIFEST, valence=Valence.POSITIVE, amplitude=0.8,
              definition="Production deployment completed")
    n2 = Node(stem="caching-layer", mode=Mode.MANIFEST, valence=Valence.POSITIVE, amplitude=0.6,
              definition="New cache performing as expected")
    e1 = Edge(type=EdgeType.SUPPORTS, nodes=[n2.id, n1.id], direction=Direction.FORWARD,
              weight=0.7, relator="Cache functioning correctly supports deployment success")
    return encode_programmatic(sender=ops, receiver=lead, intent=Intent.INFORM,
                               nodes=[n1, n2], edges=[e1],
                               priority=0.3)


# --- Scenario 5: Multi-party Brainstorm ---
scenario(
    "Multi-party Product Brainstorm",
    """So I've been thinking about the product direction and I want to throw out a few
    ideas for discussion. First, I think our user onboarding flow is causing significant
    churn - the data shows a 40% drop-off at step 3. Second, I believe gamification
    could help, specifically achievement badges and progress bars. Third, we should
    consider a freemium model instead of our current trial-based approach, because the
    conversion data from competitors suggests it performs better for our market segment.
    These three ideas are interconnected - the onboarding problem is the root cause,
    gamification addresses engagement, and freemium addresses the conversion funnel.
    I think together they could form a coherent growth strategy, but I'm not sure about
    the engineering cost. Would love everyone's thoughts.""",
    lambda: _build_brainstorm_packet(),
)


def _build_brainstorm_packet():
    pm = Identity(agent="claude", human="PM")
    team = Identity(agent="any", human="product-team")
    n1 = Node(stem="onboarding-churn", mode=Mode.MANIFEST, valence=Valence.NEGATIVE, amplitude=0.9,
              definition="40% user drop-off at onboarding step 3")
    n2 = Node(stem="gamification", mode=Mode.PROJECTION, valence=Valence.POSITIVE, amplitude=0.6,
              definition="Badges and progress bars for engagement")
    n3 = Node(stem="freemium-model", mode=Mode.PROJECTION, valence=Valence.EMERGENT, amplitude=0.7,
              definition="Replace trial with freemium based on competitor data")
    n4 = Node(stem="engineering-cost", mode=Mode.SUBJECTIVE, valence=Valence.UNCERTAIN, amplitude=0.5,
              definition="Unknown implementation effort")
    e1 = Edge(type=EdgeType.CAUSAL, nodes=[n1.id, n2.id], direction=Direction.FORWARD,
              weight=0.6, relator="Churn problem motivates gamification solution")
    e2 = Edge(type=EdgeType.CAUSAL, nodes=[n1.id, n3.id], direction=Direction.FORWARD,
              weight=0.7, relator="Churn problem motivates conversion model change")
    e3 = Edge(type=EdgeType.EMERGENCE, nodes=[n1.id, n2.id, n3.id],
              weight=0.5, relator="Together these form a coherent growth strategy")
    e4 = Edge(type=EdgeType.TENSION, nodes=[n3.id, n4.id], direction=Direction.BIDIRECTIONAL,
              weight=0.4, relator="Freemium benefits vs unknown engineering cost")
    return encode_programmatic(sender=pm, receiver=team, intent=Intent.PROPOSE,
                               nodes=[n1, n2, n3, n4], edges=[e1, e2, e3, e4], priority=0.7)


# ============================================================
# Benchmark runner
# ============================================================

def count_structural_elements(packet: IrisPacket) -> dict:
    """Count the structural richness of a packet."""
    return {
        "concepts": len(packet.nodes),
        "relationships": len(packet.edges),
        "hyperedges": sum(1 for e in packet.edges if len(e.nodes) > 2),
        "sources": len(packet.context),
        "epistemic_modes": len(set(n.mode for n in packet.nodes)),
        "edge_types": len(set(e.type for e in packet.edges)),
    }


def run_benchmark():
    print("=" * 70)
    print("HERMES PROTOCOL BENCHMARK: Plain English vs Structured Packets")
    print("=" * 70)

    total_plain_tokens = 0
    total_hermes_tokens = 0
    total_decoded_tokens = 0

    results = []

    for name, plain_english, build_fn in SCENARIOS:
        packet = build_fn()
        wire_json = to_json(packet)
        decoded = decode_to_natural_language(packet)

        plain_tokens = approx_tokens(plain_english)
        hermes_tokens = approx_tokens(wire_json)
        decoded_tokens = approx_tokens(decoded)
        structure = count_structural_elements(packet)

        # Information density = structural elements per 100 tokens
        total_elements = sum(structure.values())
        density_plain = (total_elements / plain_tokens) * 100 if plain_tokens else 0
        density_hermes = (total_elements / hermes_tokens) * 100 if hermes_tokens else 0

        total_plain_tokens += plain_tokens
        total_hermes_tokens += hermes_tokens
        total_decoded_tokens += decoded_tokens

        results.append({
            "name": name,
            "plain_tokens": plain_tokens,
            "hermes_tokens": hermes_tokens,
            "decoded_tokens": decoded_tokens,
            "wire_bytes": len(wire_json),
            "structure": structure,
            "density_plain": density_plain,
            "density_hermes": density_hermes,
        })

    # Print results
    for r in results:
        print(f"\n--- {r['name']} ---")
        print(f"  Plain English:    ~{r['plain_tokens']} tokens")
        print(f"  Iris wire:      ~{r['hermes_tokens']} tokens ({r['wire_bytes']} bytes JSON)")
        print(f"  Decoded output:   ~{r['decoded_tokens']} tokens")
        print(f"  Decoded savings:  {(1 - r['decoded_tokens'] / r['plain_tokens']) * 100:.0f}% fewer tokens than plain English")
        print(f"  Structure:        {r['structure']['concepts']} concepts, "
              f"{r['structure']['relationships']} relationships "
              f"({r['structure']['hyperedges']} hyperedges), "
              f"{r['structure']['sources']} sources")
        print(f"  Epistemic modes:  {r['structure']['epistemic_modes']} distinct modes")
        print(f"  Info density:     {r['density_plain']:.1f} elements/100tok (plain) vs "
              f"{r['density_hermes']:.1f} elements/100tok (hermes)")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Scenarios tested:          {len(SCENARIOS)}")
    print(f"  Total plain English:       ~{total_plain_tokens} tokens")
    print(f"  Total Iris decoded:      ~{total_decoded_tokens} tokens")
    print(f"  Overall token savings:     {(1 - total_decoded_tokens / total_plain_tokens) * 100:.0f}%")
    print()

    # What Iris adds that plain English doesn't
    print("STRUCTURAL ADVANTAGES (what Iris encodes that plain English doesn't):")
    print(f"  {'Scenario':<35} {'Modes':<8} {'Edge Types':<12} {'Hyperedges':<12} {'Sources'}")
    for r in results:
        s = r['structure']
        print(f"  {r['name']:<35} {s['epistemic_modes']:<8} {s['edge_types']:<12} {s['hyperedges']:<12} {s['sources']}")

    print(f"\n  Key insight: Iris packets carry typed relationships, epistemic markers,")
    print(f"  and source transclusions that plain English buries in prose or omits entirely.")


if __name__ == "__main__":
    run_benchmark()
