---
name: short-video-pro
description: Generate shot-ready short-form video scripts with structured JSON output for TikTok, Reels, and Xiaohongshu. Use when you need to create video scripts, account positioning, content selection, or production guidance. Outputs include titles, hooks, value points, CTAs, and shooting/editing tips.
---

# Short Video Professional Skill

Generate production-ready short-form video scripts based on platform-specific strategies and business objectives.

## Quick Start

**Inputs (minimal):**
- Topic or product
- Goal: traffic / education / trust / conversion / brand
- Target audience (age, occupation, pain points)
- Available materials (before/after, expert, user-generated, screenshots)
- Hook type (question, contrast, empathy, numbers)
- CTA action (follow, save, comment, message, purchase)

**Outputs:**
- Title + Hook (0–5s) + Value (≤3 points) + CTA
- Structured JSON with segments (camera, dialog, visuals)
- Shooting/editing recommendations per platform

**Process:**
1. Read user input (or run Q&A Flow in `references/examples.md`)
2. Check recent trends if applicable
3. Select structure template from `references/positioning.md`
4. Write script with core rules from `references/rules.md`
5. Output both human-readable format and JSON

## Core Rules

**Structure First:** Hook → Value → CTA (all scripts use this foundation)

**0–5 Second Hook:** Deliver conclusion immediately + visual card + quick cuts. No setup.

**Value Segment:** Maximum 3 points, 8–12 characters each. Spoken naturally.

**Single CTA:** One clear action only (follow, save, comment, message, purchase).

**Language:** Spoken vernacular, short sentences, fast rhythm. No filler words or verbal tics.

**Platform Variance:**
- **Reels:** Natural, lifestyle-driven, high emotional impact
- **TikTok:** Faster pace, trend-savvy humor, snappier cuts
- **Xiaohongshu:** Clean visuals, refined subtitles, longer titles

## JSON Output Schema

```json
{
  "segments": [
    {
      "type": "hook",
      "start_sec": 0,
      "end_sec": 5,
      "camera": "CU",
      "dialog": "...",
      "visual": "...",
      "cta": ""
    },
    {
      "type": "value",
      "start_sec": 5,
      "end_sec": 25,
      "camera": "MS",
      "dialog": "...",
      "visual": "...",
      "cta": ""
    },
    {
      "type": "cta",
      "start_sec": 25,
      "end_sec": 30,
      "camera": "WS",
      "dialog": "...",
      "visual": "...",
      "cta": "..."
    }
  ]
}
```

Camera abbreviations: **CU** (close-up), **MCU** (medium close-up), **MS** (medium shot), **WS** (wide shot).

## References

- **`references/rules.md`** — Core output rules, structure templates, editing principles, posting strategy
- **`references/positioning.md`** — Account positioning template, content selection matrix, script template library, Q&A Flow
- **`references/examples.md`** — Real examples + learning checklist

Consult references for detailed guidance on specific tasks.
