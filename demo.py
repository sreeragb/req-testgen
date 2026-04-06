"""
demo.py
Offline demo — uses the bundled sample output to show the tool's output
without needing an API key. Good for LinkedIn screenshots and README GIFs.

Usage:
    python demo.py
    python demo.py --format doors
    python demo.py --format codebeamer
"""

import json
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from format_export import export

SAMPLE_PATH = Path(__file__).parent / "examples" / "sample_output.json"

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          req-testgen  ·  AI Test Case Generator              ║
║          Automotive Requirements → ISTQB Test Cases          ║
╚══════════════════════════════════════════════════════════════╝
  [offline demo — using bundled sample output]
"""

SCORE_LABELS = {
    "coverage":             "Coverage           ",
    "boundary_correctness": "Boundary Correctness",
    "test_completeness":    "Test Completeness  ",
    "traceability":         "Traceability       ",
    "export_readiness":     "Export Readiness   ",
}


def bar(score: int, total: int = 5) -> str:
    return "█" * score + "░" * (total - score)


def print_pipeline_steps(data: dict):
    req = data["requirement_text"]
    parsed = data["parsed_requirement"]
    eq = data["equivalence_classes"]
    bva = data["boundary_values"]
    tcs = data["test_cases"]
    ev = data["evaluation"]

    print(BANNER)
    print("─" * 64)
    print(f"  REQUIREMENT")
    print(f"  {req}")
    print("─" * 64)

    print("\n  [Step 1] PARSED REQUIREMENT")
    print(f"    Type    : {parsed['requirement_type']}")
    print(f"    Subject : {parsed['subject']}")
    print(f"    Action  : {parsed['action']}")
    for p in parsed.get("parameters", []):
        print(f"    Param   : {p['name']} = {p['value']} {p['unit']}  [{p['type']}]")
    for a in parsed.get("ambiguities", []):
        print(f"    ⚠ AMBIGUITY: {a}")

    print("\n  [Step 2] EQUIVALENCE CLASSES")
    for param_ep in eq:
        print(f"    Parameter: {param_ep['parameter']}")
        for vc in param_ep.get("valid_classes", []):
            print(f"      ✓ [{vc['id']}] {vc['description']}  (rep: {vc['representative_value']})")
        for ic in param_ep.get("invalid_classes", []):
            print(f"      ✗ [{ic['id']}] {ic['description']}  (rep: {ic['representative_value']})")

    print("\n  [Step 3] BOUNDARY VALUES")
    for b in bva:
        print(f"    {b['parameter']}:")
        print(f"      min-1={b['min_minus_1']}  min={b['min']}  min+1={b['min_plus_1']}")
        print(f"      nominal={b['nominal']}")
        print(f"      max-1={b['max_minus_1']}  max={b['max']}  max+1={b['max_plus_1']}")

    print(f"\n  [Step 4] TEST CASES  ({len(tcs)} generated)")
    for tc in tcs:
        tag = "✓" if tc["test_type"] == "positive" else "✗"
        print(f"    {tag} {tc['test_case_id']}  [{tc['test_technique']}]  {tc['title']}")
        print(f"       Input: {tc['test_input']}  →  {tc['expected_result'][:60]}")

    print("\n  [Step 5] EVALUATION")
    scores = ev.get("scores", {})
    for key, label in SCORE_LABELS.items():
        s = scores.get(key, 0)
        print(f"    {label}  {bar(s)}  {s}/5")
    overall = ev.get("overall_score", 0)
    print(f"\n    Overall score: {overall:.1f}/5.0  (confidence: {ev.get('confidence')})")

    if ev.get("gaps"):
        print("\n  Gaps identified:")
        for g in ev["gaps"]:
            print(f"    • {g}")
    if ev.get("suggestions"):
        print("\n  Suggestions:")
        for s in ev["suggestions"]:
            print(f"    • {s}")


def main():
    parser = argparse.ArgumentParser(description="req-testgen offline demo")
    parser.add_argument("--format", choices=["markdown", "doors", "codebeamer"], default="markdown")
    args = parser.parse_args()

    with open(SAMPLE_PATH) as f:
        data = json.load(f)

    print_pipeline_steps(data)

    print("\n" + "─" * 64)
    print(f"  EXPORT PREVIEW  [{args.format.upper()}]")
    print("─" * 64)
    output = export(data["test_cases"], args.format, data["requirement_text"])

    # Show just the first portion so it fits on screen
    lines = output.splitlines()
    preview = lines[:30]
    print("\n".join(f"  {l}" for l in preview))
    if len(lines) > 30:
        print(f"\n  ... ({len(lines) - 30} more lines)")

    print("\n  To run live against the real LLM:")
    print("    export ANTHROPIC_API_KEY=sk-ant-...")
    print('    python src/pipeline.py --req "Your requirement here"')
    print()


if __name__ == "__main__":
    main()
