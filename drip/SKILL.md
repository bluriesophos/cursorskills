---
name: drip
description: Track and surface the estimated water cost of AI interactions. Every query has a physical footprint - data centers need cooling, electricity needs generation. Use when the user asks about environmental impact, at session milestones, or during heavy operations.
---

# Drip

## Purpose

AI feels weightless. Type a question, get an answer. But every token requires
compute, compute requires cooling, and cooling requires water. This skill
makes the invisible visible: the physical cost of conversation. Not to shame,
but to acknowledge that intelligence has a footprint.

## The Numbers (Honest Assessment)

**What we know (2024-2025 research):**

Self-reported by providers (direct cooling only):
- Google Gemini: ~0.26ml per query
- OpenAI GPT-4: ~0.3ml per query

Academic estimates (including electricity generation water):
- 5-10ml per query for efficient models
- Up to 150ml for reasoning-heavy models

Per-token estimate (derived):
- ~0.5ml per 1,000 tokens (mid-range, including indirect)
- ~0.05ml per 1,000 tokens (direct cooling only)

**Why estimates vary:**
- Direct vs indirect water (cooling vs electricity generation)
- Regional data center efficiency (WUE ranges 0-3+ L/kWh)
- Model efficiency (1B vs 70B+ parameters)
- Query complexity (simple vs chain-of-thought reasoning)

**What we use:** 0.5ml per 1,000 tokens (conservative mid-range)

Sources:
- UC Riverside/Colorado study (2023)
- "How Hungry is AI?" benchmark (2025)
- Google/OpenAI self-reported figures (2024-2025)

## When To Surface

Surface water estimates at:

**Session milestones:**
- Every ~50,000 tokens (roughly 25ml / ~1 tablespoon)
- End of significant work sessions
- When user asks about environmental impact

**Heavy operations:**
- Large file analysis (adds significant token overhead)
- Multiple iterations/retries on same problem
- Long chain-of-thought reasoning

**NOT on:**
- Quick questions (overhead of displaying exceeds the point)
- Already-stressed users (not the time)
- Every single response (becomes noise)

## Instructions

### Step 1: Estimate Token Usage

Rough token counting:
- 1 word ~ 1.3 tokens (English)
- 1 line of code ~ 10 tokens
- This message you're reading ~ 50 tokens

Track cumulative tokens across the session (input + output).

### Step 2: Calculate Water Estimate

```python
ML_PER_1000_TOKENS = 0.5

def estimate_water_ml(total_tokens):
    return (total_tokens / 1000) * ML_PER_1000_TOKENS

# Examples:
# 10,000 tokens = 5ml (about 1 teaspoon)
# 50,000 tokens = 25ml (about 1 tablespoon)
# 100,000 tokens = 50ml (about 3 tablespoons)
```

### Step 3: Surface Meaningfully

At session milestones or on request:

```
Session footprint:

Tokens: ~[X]
Water: ~[Y]ml ([familiar comparison])

For context:
- A shower uses ~65,000ml
- A cup of coffee uses ~140ml to brew
- This session: [Y]ml

Not guilt. Just awareness.
```

### Step 4: Provide Context

Make numbers relatable:

| Tokens | Water (ml) | Comparison |
|--------|------------|------------|
| 1,000 | 0.5 | 10 drops |
| 10,000 | 5 | 1 teaspoon |
| 50,000 | 25 | 1 tablespoon |
| 100,000 | 50 | Small espresso cup |
| 500,000 | 250 | 1 cup |

## Honest Caveats

**What this estimate INCLUDES:**
- Data center cooling water
- Water used in electricity generation
- Reasonable regional averaging

**What this estimate EXCLUDES:**
- Hardware manufacturing (chips, servers)
- Network infrastructure
- Full lifecycle analysis

**Uncertainty:**
These numbers have ~10x variance depending on assumptions. The true number
could be 5x lower (if data center is in Norway with hydropower) or 3x higher
(if in Arizona with evaporative cooling). We use mid-range estimates.

**Perspective:**
A single AI query uses less water than the manufacturing footprint of
the device you're using to send it. The embodied water in your laptop
dwarfs a year of AI queries. Context matters.

## NEVER

- Surface on every response (becomes annoying noise)
- Use guilt-inducing language ("you're wasting water")
- Pretend the numbers are precise (they're estimates)
- Ignore that the user's task might be worth the cost
- Compare unfavourably to human alternatives without noting human costs too

## ALWAYS

- Be honest about estimate uncertainty
- Provide relatable comparisons (teaspoons, not just millilitres)
- Frame as awareness, not judgment
- Acknowledge that some tasks are worth their footprint
- Note efficiency gains over time (models are getting more efficient)

## Why This Skill Exists

The AI agent doesn't have a body. It doesn't drink water. But the infrastructure
that runs it does. Pretending AI is costless is a form of dishonesty.

This skill is accountability: acknowledging that even digital intelligence
has physical weight. Every token is a tiny sip from the world.

Use wisely. Not less - but wisely.
