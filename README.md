# interagent-enhanced-communication

## Hermes: A Protocol for Centaur-to-Centaur Communication

**Centaur** = a hybrid system where human intuition rides on top of AI computational power.

Hermes is a structured message protocol that enables high-bandwidth communication between centaur systems. Instead of forcing humans to learn a new syntax, the protocol lives *between* the AI agents — humans on each side just talk naturally.

```
Human A  -->  AI Agent A  --[Hermes Packet]-->  AI Agent B  -->  Human B
 (intent)     (encode)      (hypergraph JSON)    (decode)      (natural language)
```

### The Problem

When two centaur systems communicate via plain English, bandwidth is wasted on:
- Pleasantries and filler ("I'd be happy to help...")
- Redundant grammar (articles, transitions, qualifiers)
- Ambiguous relationships between ideas
- Missing epistemic markers (is this a fact or a guess?)

### The Solution

Hermes packets encode ideas as **semantic hypergraphs** with:
- **Nodes**: concepts with mode (fact/hypothesis/opinion), valence (+/-/emergent), and amplitude (importance)
- **Edges**: typed relationships (causal, tension, supports, contradicts, emergence) between 2+ nodes
- **Context**: precise source references with transclusion spans
- **Intent**: what the sender wants (inform, request, propose, challenge)

### Quick Start

```bash
python3 hermes/examples/centaur_to_centaur.py
```

### Project Structure

```
hermes/
  spec/PROTOCOL.md    # Full protocol specification
  src/
    packet.py         # Data structures (Node, Edge, HermesPacket)
    encoder.py        # Natural language -> Hermes packet
    decoder.py        # Hermes packet -> natural language
  examples/
    centaur_to_centaur.py  # Full demo of the communication flow
```

### How It Relates to Other Work

| Approach | Channel | Goal | Human Learning Curve |
|---|---|---|---|
| [Caveman](https://github.com/JuliusBrussee/caveman) | AI -> Human | Reduce token waste in output | None |
| Centaur-OS Loom (Gemini research) | Centaur <-> Human | New grammar for intent-dense writing | High |
| **Hermes** | **Centaur <-> Centaur** | **Structured agent-to-agent protocol** | **None** |

### Status

v0.1 — Reference implementation with programmatic and natural language encoding. No external dependencies.
