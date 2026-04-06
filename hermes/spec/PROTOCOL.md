# Hermes Protocol Specification v0.1

## What is Hermes?

Hermes is a structured message protocol for **centaur-to-centaur communication** — where each centaur is a human+AI hybrid system.

The core insight: when two centaurs communicate, the AI on each side can handle compression and decompression. The human never needs to learn a new syntax. They speak naturally to their own AI, and Hermes handles the high-bandwidth transfer between agents.

```
Human A  -->  AI Agent A  --[Hermes Packet]-->  AI Agent B  -->  Human B
 (intent)     (encode)        (structured)       (decode)      (natural language)
```

## Design Principles

1. **Humans never touch the wire format.** The protocol is agent-to-agent. Humans interact with their own AI naturally.
2. **Semantic density over syntactic beauty.** Pack maximum meaning into minimum tokens.
3. **Mode-aware.** Every claim is tagged with its epistemic status (fact, hypothesis, opinion, consensus).
4. **Polyadic relationships.** Ideas can relate to N other ideas simultaneously, not just pairwise.
5. **Transcludable.** Every reference points to a specific source span, not a vague citation.

## Packet Structure

A Hermes packet is a JSON object with these top-level fields:

```json
{
  "hermes": "0.1",
  "id": "uuid-v4",
  "timestamp": "ISO-8601",
  "from": { "agent": "claude-3", "human": "alice" },
  "to": { "agent": "gemini-2", "human": "bob" },
  "intent": "inform | request | propose | challenge | acknowledge",
  "priority": 0.0-1.0,
  "graph": { ... },
  "context": [ ... ],
  "meta": { ... }
}
```

### Intent Types

| Intent | Meaning | Expected Response |
|---|---|---|
| `inform` | Sharing knowledge or a conclusion | `acknowledge` or `challenge` |
| `request` | Asking for information or action | `inform` or `propose` |
| `propose` | Suggesting a plan or idea | `acknowledge`, `challenge`, or `propose` |
| `challenge` | Disputing a prior claim | `inform` (with evidence) or `acknowledge` |
| `acknowledge` | Confirming receipt/agreement | None required |

### The Graph (Core Payload)

The `graph` field contains a **hypergraph** — the actual semantic content of the message.

```json
{
  "graph": {
    "nodes": [
      {
        "id": "n1",
        "stem": "climate-reform",
        "mode": "manifest",
        "valence": "+",
        "amplitude": 0.9,
        "definition": "Policy changes targeting carbon emission reduction"
      },
      {
        "id": "n2",
        "stem": "economic-growth",
        "mode": "projection",
        "valence": "^",
        "amplitude": 0.7,
        "definition": "GDP trajectory under proposed reforms"
      },
      {
        "id": "n3",
        "stem": "carbon-capture",
        "mode": "projection",
        "valence": "+",
        "amplitude": 0.5,
        "definition": "Emergent tech for atmospheric CO2 removal"
      }
    ],
    "edges": [
      {
        "id": "e1",
        "type": "tension",
        "nodes": ["n1", "n2"],
        "direction": "<->",
        "weight": 0.8,
        "relator": "System-Tension: reforms may slow growth short-term"
      },
      {
        "id": "e2",
        "type": "emergence",
        "nodes": ["n1", "n2", "n3"],
        "direction": null,
        "weight": 0.6,
        "relator": "Potential resolution: carbon capture bridges both goals"
      }
    ]
  }
}
```

### Node Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique node identifier within this packet |
| `stem` | string | Core concept label (kebab-case) |
| `mode` | enum | Epistemic status: `manifest` (fact), `projection` (hypothesis), `collective` (consensus), `subjective` (opinion) |
| `valence` | enum | `+` (positive/constructive), `-` (negative/destructive), `^` (emergent/novel), `~` (uncertain) |
| `amplitude` | float | Importance weight 0.0-1.0. Replaces adverbs. |
| `definition` | string | Brief natural-language definition for disambiguation |

### Edge Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique edge identifier |
| `type` | enum | Relationship kind: `causal`, `tension`, `supports`, `contradicts`, `emergence`, `temporal`, `contains` |
| `nodes` | array | List of node IDs (2+ for hyperedges) |
| `direction` | enum | `->` (A causes B), `<-` (B causes A), `<->` (bidirectional), `null` (undirected) |
| `weight` | float | Strength of relationship 0.0-1.0 |
| `relator` | string | Natural-language explanation of the relationship |

### Context (Transclusion)

The `context` array provides source references using precise spans:

```json
{
  "context": [
    {
      "id": "c1",
      "source": "ipcc-ar6-wg3",
      "span": "chapter-14:1402-1450",
      "url": "https://...",
      "summary": "Mitigation pathways compatible with 1.5C require 43% CO2 reduction by 2030",
      "supports_nodes": ["n1"]
    }
  ]
}
```

### Meta (Communication Control)

```json
{
  "meta": {
    "compression": "semantic-v1",
    "expecting_response": true,
    "thread_id": "uuid-of-conversation-thread",
    "in_reply_to": "uuid-of-previous-packet",
    "human_override": false,
    "ttl": 3600
  }
}
```

## Communication Modes

### Mode 1: Centaur-to-Centaur (Full Protocol)

Both sides have AI agents. Full hypergraph packets are exchanged. The receiving AI unpacks the graph into whatever format its human prefers — natural language summary, visual map, structured outline, etc.

**This is the primary use case.**

### Mode 2: Centaur-to-Human (Downgraded)

The receiving side has no AI agent. The sending AI must "render" the packet into readable natural language before transmission. Information density drops but the protocol still structures the sender's thinking.

### Mode 3: Agent-to-Agent (Headless)

No humans in the loop on either side. Agents exchange packets autonomously. The `human_override` flag in meta is `false`. Used for automated research, monitoring, or multi-agent workflows.

## How a Human Actually Uses This

### Sending (Alice's side)

```
Alice: "Tell Bob that climate reform and economic growth are in tension,
        but carbon capture might bridge both. Link the IPCC AR6 data.
        This is my hypothesis, not settled fact."

Alice's AI (Hermes encoder):
  - Extracts 3 nodes: climate-reform, economic-growth, carbon-capture
  - Tags mode: projection (hypothesis)
  - Creates tension edge between n1-n2, emergence hyperedge across n1-n2-n3
  - Attaches IPCC transclusion
  - Sends Hermes packet to Bob's AI
```

### Receiving (Bob's side)

```
Bob's AI (Hermes decoder):
  "Alice shared a hypothesis: climate reform and economic growth
   are in tension (high confidence), but she sees carbon capture
   as a potential bridge (moderate confidence). She's referencing
   IPCC AR6 Ch.14 lines 1402-1450 on mitigation pathways.
   Want me to show the relationship map or dig into the source?"

Bob: "Show me the map."

Bob's AI: [renders a simple node-edge visualization]
```

### The key insight

Alice didn't learn any new syntax. Bob didn't either. The protocol lives between their AIs. The humans just... talk.

## Comparison to Alternatives

| Approach | Human Learning Curve | Bandwidth | Adoption Friction |
|---|---|---|---|
| Plain English | None | Low | None |
| Caveman (compressed English) | None | Medium | None |
| Centaur-OS Loom notation | High | High | Very High |
| **Hermes Protocol** | **None** | **High** | **Low (requires AI on both sides)** |

## Next Steps

- [ ] Reference implementation (Python encoder/decoder)
- [ ] Agent integration (Claude Code skill / MCP tool)
- [ ] Visual packet inspector
- [ ] Multi-agent thread management
- [ ] Semantic diff (compare two packets for agreement/disagreement)
