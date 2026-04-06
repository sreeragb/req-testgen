# req-testgen — Claude Code Project Context

This file is read by Claude Code automatically when the project folder is opened.
It provides the project map, entry points, and conventions so Claude Code can
navigate and use the project without being told the structure every time.

---

## What this project does

Generates ASPICE SWE.4 / ISO 26262 Part 6 compliant test cases from automotive
software requirements. Accepts any input format: PDF, DOCX, XLSX, CSV, TXT,
Codebeamer CR text, IBM Synergy CR text, DOORS CSV export.

Two skills are available — use the right one:

| Skill | Use for |
|---|---|
| `auto-req-testgen` | Automotive projects — ASPICE, ISO 26262, ASIL |
| `req-testgen` | General software projects — no automotive standards |

---

## Entry points

```
src/read_document.py        Extract requirements from a document file
src/normalize_requirements.py  Clean CR text / architect notes into "shall" statements
src/pipeline_auto.py        Full 6-step automotive pipeline (MAIN ENTRY POINT)
src/pipeline.py             Generic pipeline (no automotive standards)
```

Run from the project root:
```bash
python src/pipeline_auto.py --req "The BSW shall..." --asil C
python src/pipeline_auto.py --file normalized.txt --format doors
```

---

## Project layout

```
req-testgen/
├── CLAUDE.md                   ← you are here
├── src/
│   ├── pipeline_auto.py        Main automotive pipeline (6 steps)
│   ├── pipeline.py             Generic pipeline (5 steps)
│   ├── prompt_steps_auto.py    6 LLM prompt chain functions (automotive)
│   ├── prompt_steps.py         5 LLM prompt chain functions (generic)
│   ├── llm_client.py           Anthropic/OpenAI abstraction
│   ├── format_export_auto.py   DOORS CSV + Codebeamer JSON (automotive)
│   ├── format_export.py        DOORS CSV + Codebeamer JSON (generic)
│   ├── normalize_requirements.py  CR/architect note → clean requirements
│   └── read_document.py        PDF/DOCX/XLSX/CSV reader
│
├── skill/
│   ├── auto-req-testgen/       Claude Code skill — automotive
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── aspice_swe4.md
│   │       ├── iso26262_part6.md
│   │       ├── prompt_design.md
│   │       └── export_formats.md
│   └── req-testgen/            Claude Code skill — generic
│       ├── SKILL.md
│       └── references/
│
├── tests/
│   ├── conftest.py             Shared fixtures
│   ├── test_pipeline.py        Generic pipeline tests (16 tests)
│   └── test_pipeline_auto.py   Automotive pipeline tests (43 tests)
│
├── examples/
│   ├── automotive_requirements.txt   12 real-pattern automotive requirements
│   ├── sample_codebeamer_cr.txt      Example Codebeamer CR for normalizer
│   ├── sample_synergy_cr.txt         Example Synergy CR for normalizer
│   └── sample_output.json            Full pipeline output example
│
└── outputs/                    Generated test cases land here (git-ignored)
```

---

## API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # required for pipeline runs
```

To use OpenAI instead: `--provider openai` + `export OPENAI_API_KEY=...`

---

## Running tests

```bash
pytest                          # all unit tests (no API key needed) — 59 tests
pytest tests/test_pipeline_auto.py -v   # automotive only
pytest -m slow                  # integration tests (needs API key)
```

---

## Installing the skills in Claude Code

**Personal (available across all your projects):**
```bash
cp -r skill/auto-req-testgen ~/.claude/skills/
cp -r skill/req-testgen ~/.claude/skills/
```

**Project-level (shared via git with your team):**
```bash
mkdir -p .claude/skills
cp -r skill/auto-req-testgen .claude/skills/
```

After copying, Claude Code discovers skills automatically — no restart needed.
Verify: ask Claude Code "What skills are available?"

---

## Renaming the skill

Three things must match — change all three together:

1. The folder name: `skill/auto-req-testgen/` → `skill/your-new-name/`
2. The `name:` field in `SKILL.md` frontmatter
3. The install path: `~/.claude/skills/your-new-name/`

Nothing in the Python source files references the skill name.

---

## Adding a local LLM provider

Edit `src/llm_client.py` — the `call_llm()` function. Add a new branch:

```python
elif provider == "ollama":
    return _call_ollama(system_prompt, user_prompt, model, max_tokens)
```

See `src/llm_client.py` for the existing Anthropic and OpenAI implementations.
The rest of the pipeline is provider-agnostic.
