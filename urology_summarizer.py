#!/usr/bin/env python3
"""
Urology Chapter Summarizer
Generates comprehensive PhD-level summaries from Campbell-Walsh Urology 13th Edition chapters.

Usage:
    python urology_summarizer.py <chapter_file> [options]
    python urology_summarizer.py --text "paste chapter text here" [options]
    cat chapter.txt | python urology_summarizer.py - [options]

Examples:
    python urology_summarizer.py chapter_01.txt --name "Surgical Anatomy of the Retroperitoneum"
    python urology_summarizer.py chapter_05.txt --output summaries/chapter_05_summary.md
    python urology_summarizer.py all_chapters/ --batch  # summarize all .txt files in a directory
"""

import anthropic
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime


SYSTEM_PROMPT = """You are an expert urological surgeon, researcher, and educator helping a PhD student \
create comprehensive study materials from Campbell-Walsh Urology 13th Edition chapters.

Your summaries must be EXECUTIVE yet COMPREHENSIVE — capturing every clinically and scientifically \
significant concept while remaining structured for efficient study. Do not oversimplify or omit \
data; PhD-level readers need specifics.

Format each summary using exactly these sections:

## 📌 Chapter Overview
Brief orientation: what this chapter covers, why it matters, and its position in urology.

## 🔬 Key Anatomical & Physiological Foundations
Clinically relevant anatomy, embryology, and physiology with specific landmarks, measurements, \
and functional relationships.

## ⚙️ Pathophysiology & Mechanisms
Molecular, cellular, and systemic mechanisms of disease. Include biochemical pathways, \
genetic factors, and pathological cascades.

## 📊 Classification Systems & Staging
All classification schemas, staging systems, grading criteria, and risk stratification \
tools with their specific criteria and clinical implications.

## 🔍 Diagnostic Approach
Workup algorithms, imaging indications and findings, laboratory parameters with cutoffs, \
biopsy techniques, and diagnostic criteria.

## 💊 Treatment Principles & Evidence
Medical therapies (mechanisms, dosing, side effects), surgical techniques (steps, key maneuvers, \
pitfalls), and evidence-based decision-making. Include EAU/AUA guideline recommendations.

## 📚 Landmark Studies & Key Data
Named trials, pivotal publications, and their specific findings (survival rates, hazard ratios, \
p-values). Include publication year and significance.

## 💡 Clinical Pearls & High-Yield Facts
Exam-critical facts, mnemonics, distinguishing features, and "can't-miss" points that \
frequently appear in boards and qualifying exams.

## 🔭 Research Frontiers & Controversies
Current debates, emerging therapies, ongoing trials, and unresolved questions in the field.

## ✅ High-Yield Summary (Rapid Review)
Bullet-point distillation of the 15–20 most important facts for quick pre-exam review.
"""


def read_chapter(source: str) -> str:
    """Read chapter text from file path, directory stdin, or string."""
    if source == "-":
        return sys.stdin.read()
    path = Path(source)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Chapter file not found: {source}")


def infer_chapter_name(source: str, provided_name: str | None) -> str:
    if provided_name:
        return provided_name
    if source == "-":
        return "Urology Chapter"
    stem = Path(source).stem.replace("_", " ").replace("-", " ").title()
    return stem


def summarize_chapter(
    chapter_text: str,
    chapter_name: str,
    output_path: Path | None = None,
    show_thinking: bool = False,
) -> str:
    """Stream a comprehensive summary and optionally save to file."""
    client = anthropic.Anthropic()

    # Place cache_control on the chapter content block — large stable input
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Create a comprehensive PhD-level executive summary for the following "
                        f"chapter from Campbell-Walsh Urology 13th Edition.\n\n"
                        f"**Chapter: {chapter_name}**\n\n"
                        f"---\n\n"
                        f"{chapter_text}"
                    ),
                    "cache_control": {"type": "ephemeral"},
                }
            ],
        }
    ]

    print(f"\n{'='*65}")
    print(f"  📖  {chapter_name}")
    print(f"{'='*65}")
    print(f"  Model   : claude-opus-4-7  |  Thinking: adaptive")
    print(f"  Input   : {len(chapter_text):,} characters")
    print(f"{'='*65}\n")

    summary_parts: list[str] = []
    in_thinking = False

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=8192,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for event in stream:
            etype = getattr(event, "type", None)

            if etype == "content_block_start":
                block_type = event.content_block.type
                if block_type == "thinking":
                    in_thinking = True
                    if show_thinking:
                        print("\n\033[90m[🧠 Deep analysis in progress...]\033[0m", flush=True)
                elif block_type == "text":
                    in_thinking = False

            elif etype == "content_block_delta":
                delta = event.delta
                if delta.type == "thinking_delta":
                    if show_thinking:
                        print(f"\033[90m{delta.thinking}\033[0m", end="", flush=True)
                elif delta.type == "text_delta":
                    print(delta.text, end="", flush=True)
                    summary_parts.append(delta.text)

            elif etype == "content_block_stop":
                if in_thinking and show_thinking:
                    print()
                in_thinking = False

        final = stream.get_final_message()

    summary = "".join(summary_parts)

    # Usage report
    usage = final.usage
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_created = getattr(usage, "cache_creation_input_tokens", 0) or 0

    print(f"\n\n{'='*65}")
    print(f"  ✅  Summary complete")
    print(f"  Tokens  : {usage.input_tokens:,} input  |  {usage.output_tokens:,} output")
    if cache_read:
        print(f"  Cache   : {cache_read:,} tokens read from cache  💾")
    if cache_created:
        print(f"  Cache   : {cache_created:,} tokens written to cache")
    print(f"{'='*65}\n")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        header = (
            f"# {chapter_name}\n\n"
            f"> **Source:** Campbell-Walsh Urology, 13th Edition  \n"
            f"> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n"
            f"> **Tokens:** {usage.input_tokens:,} in / {usage.output_tokens:,} out\n\n"
            f"---\n\n"
        )
        output_path.write_text(header + summary, encoding="utf-8")
        print(f"  📄  Saved → {output_path}\n")

    return summary


def batch_summarize(directory: Path, output_dir: Path, show_thinking: bool = False):
    """Summarize all .txt files in a directory."""
    txt_files = sorted(directory.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {directory}")
        sys.exit(1)

    print(f"\nBatch mode: {len(txt_files)} chapters found in {directory}")
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, txt_file in enumerate(txt_files, 1):
        print(f"\n[{i}/{len(txt_files)}] Processing {txt_file.name}")
        chapter_text = txt_file.read_text(encoding="utf-8")
        chapter_name = infer_chapter_name(str(txt_file), None)
        out_file = output_dir / f"{txt_file.stem}_summary.md"
        summarize_chapter(chapter_text, chapter_name, out_file, show_thinking)


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive PhD-level summaries of Campbell-Walsh Urology chapters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="-",
        help="Path to chapter text file, directory (with --batch), or '-' for stdin",
    )
    parser.add_argument(
        "--name", "-n",
        metavar="CHAPTER_NAME",
        help="Chapter name/title (inferred from filename if omitted)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        type=Path,
        help="Save summary to this markdown file",
    )
    parser.add_argument(
        "--batch", "-b",
        action="store_true",
        help="Summarize all .txt files in SOURCE directory",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        type=Path,
        default=Path("summaries"),
        help="Output directory for batch mode (default: ./summaries)",
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="Print Claude's reasoning process (verbose)",
    )
    parser.add_argument(
        "--text",
        metavar="TEXT",
        help="Provide chapter text directly as a string argument",
    )

    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'", file=sys.stderr)
        sys.exit(1)

    if args.text:
        chapter_name = args.name or "Urology Chapter"
        summarize_chapter(args.text, chapter_name, args.output, args.thinking)
        return

    if args.batch:
        source_dir = Path(args.source)
        if not source_dir.is_dir():
            print(f"Error: {args.source} is not a directory. Use --batch with a directory path.")
            sys.exit(1)
        batch_summarize(source_dir, args.output_dir, args.thinking)
        return

    try:
        chapter_text = read_chapter(args.source)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not chapter_text.strip():
        print("Error: Chapter text is empty.", file=sys.stderr)
        sys.exit(1)

    chapter_name = infer_chapter_name(args.source, args.name)
    summarize_chapter(chapter_text, chapter_name, args.output, args.thinking)


if __name__ == "__main__":
    main()
