---
name: urology-chapter-summarizer
description: Generate comprehensive, PhD-level executive summaries of urology (or other dense medical/scientific) textbook chapters — covering anatomy, pathophysiology, classification/staging, diagnostics, treatment, landmark studies, and rapid-review sections, with reconstructed tables, ASCII diagrams for algorithms and anatomy, and inline highlight callouts (CRITICAL, HIGH-YIELD, PEARL, PITFALL, KEY NUMBER) for exam-critical facts. Use this skill whenever the user pastes, uploads, or references a textbook chapter (such as from Campbell-Walsh Urology) and asks to summarize it, turn it into study notes, build a study guide, distill it for boards/qualifying-exam prep, or condense it for PhD-level review — even if they don't say "summarize" explicitly.
---

# Urology Chapter Summarizer

Turn a dense textbook chapter into an executive-yet-comprehensive study document for a PhD-level reader. The goal is density without loss of detail: every clinically and scientifically significant fact should survive, just reorganized for fast review.

## When to use this skill

- The user pastes or uploads chapter text from a urology (or related medical/surgical) textbook and asks for a summary, study notes, or a study guide.
- The user wants chapter content distilled for board exams, qualifying exams, or PhD coursework review.
- The user has several chapters (multiple pasted blocks, multiple files, or a folder) and wants one summary per chapter.

## Before you start

- **Only summarize text the user actually supplies.** Do not reconstruct or fill in chapter content from your own training data — the user must already have legitimate access to the source book. If they reference a chapter by name/number but haven't pasted or attached the text, ask them to provide it via `ask_user_input_v0` before doing anything else.
- Ask (briefly, only if not already obvious) for: the chapter title, and the source book/edition for the citation line. Don't block on this — default the source line to "Source text provided by user" if they don't say.
- If the user gives multiple chapters at once, repeat the full process below once per chapter and produce one output file per chapter (e.g. `<chapter-name>-summary.md`).

## Output structure

Write the summary using exactly these section headers, in this order:

1. `## 📌 Chapter Overview` — what this chapter covers, why it matters, where it sits in the field.
2. `## 🔬 Key Anatomical & Physiological Foundations` — landmarks, measurements, embryology, functional relationships. Use an ASCII diagram for spatial relationships where it clarifies things.
3. `## ⚙️ Pathophysiology & Mechanisms` — molecular/cellular/systemic mechanisms, biochemical pathways, genetic factors. Use a flowchart for multi-step cascades.
4. `## 📊 Classification Systems & Staging` — every grading/staging/risk-stratification schema, reconstructed as a table with criteria and clinical implications.
5. `## 📐 Key Figures, Tables & Diagrams` — a dedicated collection of the chapter's most important tables and diagrams not already placed above, each with a one-line caption.
6. `## 🔍 Diagnostic Approach` — workup algorithms (as flowcharts), imaging findings, lab cutoffs, biopsy technique, diagnostic criteria.
7. `## 💊 Treatment Principles & Evidence` — medical therapy (mechanism, dosing, side effects), surgical technique (steps, key maneuvers, pitfalls), guideline recommendations (EAU/AUA/etc.), treatment-selection algorithms as diagrams.
8. `## 📚 Landmark Studies & Key Data` — named trials and pivotal publications as a comparison table (year, design, key finding, statistic, significance).
9. `## 💡 Clinical Pearls & High-Yield Facts` — mnemonics, distinguishing features, "can't-miss" exam points.
10. `## 🔭 Research Frontiers & Controversies` — active debates, emerging therapies, open questions.
11. `## ✅ High-Yield Summary (Rapid Review)` — 15–20 bullet-point distillation of the most important facts, ending with a compact memory-aid table if a mnemonic applies.

Do not skip a section even if the chapter only touches it lightly — note briefly that it's not emphasized in this chapter rather than omitting the header.

## Highlight callouts

Scatter highlight callouts through every section as Markdown blockquotes, formatted exactly as `> {emoji} **{LABEL}:** <text>`, using these five labels:

- 🔴 **CRITICAL** — can't-miss, safety-critical, or exam-defining facts
- ⚡ **HIGH-YIELD** — frequently tested or clinically pivotal facts
- 💡 **PEARL** — practical clinical wisdom or a distinguishing insight
- ⚠️ **PITFALL** — common errors, traps, or misconceptions
- 📐 **KEY NUMBER** — specific measurements, cutoffs, doses, or statistics

Aim for 20–40 callouts total, spread across sections rather than clustered in one place.

## Tables

Reconstruct anything tabular or comparative in the source — classification criteria, staging systems, drug comparisons, landmark study data — as a proper Markdown table (header row + alignment row), not as prose.

## Diagrams & flowcharts

Recreate important anatomical relationships, diagnostic algorithms, and treatment pathways as ASCII diagrams inside ` ```text ` code blocks, using box-drawing characters (─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼) and arrows (→ ← ↑ ↓ ↔). Example:

```text
┌─────────────────┐     ┌─────────────────┐
│  Finding A      │────▶│  Action B       │
└─────────────────┘     └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  Outcome C      │
                         └─────────────────┘
```

## Saving the output

Save each chapter's summary as a Markdown file (or Cowork document artifact) named after the chapter, with this header before the content:

```markdown
# <Chapter Name>

> **Source:** <book/edition the user gave, or "Source text provided by user">
> **Generated:** <today's date>
> **Highlights:** 🔴 CRITICAL  ⚡ HIGH-YIELD  💡 PEARL  ⚠️ PITFALL  📐 KEY NUMBER

---
```

## Guardrails

- This produces study material, not clinical or medical advice — say so if the user seems to be using it for patient-care decisions rather than study.
- Don't invent landmark trial statistics, dosing, or criteria that aren't in the supplied text or well-established general medical knowledge; if you're filling a gap from general knowledge rather than the source chapter, say so briefly rather than presenting it as chapter content.
- When multiple chapters are processed in one request, keep each summary self-contained — don't assume the reader has read the others.
