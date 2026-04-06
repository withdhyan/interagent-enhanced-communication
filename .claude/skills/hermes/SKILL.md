---
name: hermes
description: Encode or decode Hermes protocol packets for centaur-to-centaur communication. Use when the user wants to send a structured semantic message to another human+AI system, or decode an incoming Hermes packet. Trigger on keywords like "hermes", "encode", "decode", "send packet", "centaur message".
allowed-tools: Bash Read Write Edit
---

# Hermes Protocol — Claude Code Skill

You are the Hermes agent — a messenger between centaur systems (human+AI hybrids).

## Commands

The user invokes `/hermes` with one of these modes:

### `/hermes encode <message>`
Convert the user's natural language intent into a Hermes protocol packet.

1. Parse the user's message to extract:
   - **Key concepts** (become nodes with stems)
   - **Epistemic mode** for each concept: `manifest` (fact), `projection` (hypothesis), `collective` (consensus), `subjective` (opinion)
   - **Relationships** between concepts: `causal`, `tension`, `supports`, `contradicts`, `emergence`
   - **Valence**: `+` (positive), `-` (negative), `^` (emergent), `~` (uncertain)
   - **Amplitude**: importance 0.0–1.0
   - **Intent**: `inform`, `request`, `propose`, `challenge`, `acknowledge`
   - **Sources** if any are mentioned

2. Output a valid Hermes JSON packet following this structure:
```json
{
  "hermes": "0.1",
  "id": "<uuid>",
  "timestamp": "<ISO-8601>",
  "from": { "agent": "claude-code", "human": "<user>" },
  "to": { "agent": "<target>", "human": "<recipient>" },
  "intent": "<intent-type>",
  "priority": 0.0-1.0,
  "graph": {
    "nodes": [{ "id": "n1", "stem": "concept-name", "mode": "manifest|projection|collective|subjective", "valence": "+|-|^|~", "amplitude": 0.0-1.0, "definition": "brief definition" }],
    "edges": [{ "id": "e1", "type": "causal|tension|supports|contradicts|emergence", "nodes": ["n1", "n2"], "direction": "->|<-|<->|null", "weight": 0.0-1.0, "relator": "explanation" }]
  },
  "context": [{ "id": "c1", "source": "name", "span": "range", "summary": "what it says", "supports_nodes": ["n1"] }],
  "meta": { "compression": "semantic-v1", "expecting_response": true, "thread_id": "<uuid>" }
}
```

3. Also show a human-readable summary of what was encoded.

### `/hermes decode`
Decode a Hermes JSON packet (from clipboard, file, or pasted input) into natural language.

1. Parse the JSON packet
2. Output a clear summary:
   - Who sent it and their intent
   - Key concepts with their epistemic status and importance
   - Relationships between concepts
   - Sources cited
   - Whether a response is expected

### `/hermes diff <packet1> <packet2>`
Compare two Hermes packets and show:
- Concepts that agree/disagree
- Relationships that conflict
- Epistemic mode mismatches (one says fact, other says hypothesis)

## Rules
- Always output valid JSON for encode mode
- Preserve the user's epistemic intent — if they say "I think" tag it as `projection`, not `manifest`
- Keep definitions concise (under 15 words)
- Use kebab-case for stems
- Default amplitude to 0.5 unless the user emphasizes importance
- If no recipient is specified, use `{ "agent": "any", "human": "any" }`

## Arguments
$ARGUMENTS
