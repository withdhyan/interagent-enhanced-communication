# interagent-enhanced-communication

## Iris: A Protocol for Centaur-to-Centaur Communication

**Centaur** = a hybrid system where human intuition rides on top of AI computational power.

Iris (named after the Greek messenger goddess who bridged realms) is a structured message protocol that enables high-bandwidth communication between centaur systems. Instead of forcing humans to learn a new syntax, the protocol lives *between* the AI agents — humans on each side just talk naturally.

```
Human A  -->  AI Agent A  --[Iris Packet]-->  AI Agent B  -->  Human B
 (intent)     (encode)      (hypergraph JSON)    (decode)      (natural language)
```

### The Problem

When two centaur systems communicate via plain English, bandwidth is wasted on:
- Pleasantries and filler ("I'd be happy to help...")
- Redundant grammar (articles, transitions, qualifiers)
- Ambiguous relationships between ideas
- Missing epistemic markers (is this a fact or a guess?)

### The Solution

Iris packets encode ideas as **semantic hypergraphs** with:
- **Nodes**: concepts with mode (fact/hypothesis/opinion), valence (+/-/emergent), and amplitude (importance)
- **Edges**: typed relationships (causal, tension, supports, contradicts, emergence) between 2+ nodes
- **Context**: precise source references with transclusion spans
- **Intent**: what the sender wants (inform, request, propose, challenge)

### Quick Start

```bash
python3 iris/examples/centaur_to_centaur.py
python3 iris/tests/test_iris.py
python3 iris/benchmarks/benchmark.py
python3 iris/benchmarks/benchmark_vs_nous.py
```

### Project Structure

```
iris/
  spec/PROTOCOL.md    # Full protocol specification
  src/
    packet.py         # Data structures (Node, Edge, IrisPacket)
    encoder.py        # Natural language -> Iris packet
    decoder.py        # Iris packet -> natural language
  examples/
    centaur_to_centaur.py  # Full demo of the communication flow
  tests/
    test_iris.py      # Unit tests (13/13 passing)
  benchmarks/
    benchmark.py          # Plain English vs Iris comparison
    benchmark_vs_nous.py  # Head-to-head vs NousResearch Hermes Agent
```

### How It Relates to Other Work

| Approach | Channel | Goal | Human Learning Curve |
|---|---|---|---|
| [Caveman](https://github.com/JuliusBrussee/caveman) | AI -> Human | Reduce token waste in output | None |
| [NousResearch Hermes Agent](https://github.com/NousResearch/hermes-agent) | Agent runtime | Self-improving multi-platform agent | None |
| Centaur-OS Loom (Gemini research) | Centaur <-> Human | New grammar for intent-dense writing | High |
| **Iris Protocol** | **Centaur <-> Centaur** | **Structured semantic wire format** | **None** |

**Note on naming:** We renamed from "Hermes Protocol" to "Iris Protocol" to avoid confusion with NousResearch's Hermes Agent framework. They solve different problems (Nous = agent runtime + tool calling; Iris = semantic message format) and can be combined.

### Benchmarks

Head-to-head vs NousResearch Hermes Agent format across 4 scenarios:
- **Token overhead**: Nous +170%, Iris -32% vs plain English (decoded)
- **Structural features**: Nous 0, Iris 50 (epistemic markers, typed relationships, confidence scores, source transclusions, hyperedges, thread tracking)

### Status

v0.1 — Reference implementation with programmatic and natural language encoding, 13 passing tests, 2 benchmark suites, and a `/iris` Claude Code skill.
