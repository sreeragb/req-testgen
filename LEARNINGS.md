# What I Learned Building req-testgen

Notes for myself — and for anyone reading this on GitHub.
These map directly to the DeepLearning.AI "Generative AI with LLMs" course concepts.

---

## Week 1 Concepts Used

### Transformer basics → why temperature=0 works here
The pipeline sets `temperature=0` on every step. This is deliberate:
structured output (JSON) needs determinism. Higher temperature increases creativity
but also increases the chance the model outputs something that breaks `json.loads()`.
For a *test case generator*, correctness beats creativity.

### Prompt structure matters
Every prompt in this project follows a pattern:
1. Role priming (`"You are an expert..."`)
2. Task description
3. Output schema (shown as JSON)
4. Negative constraint (`"No markdown fences"`)

Removing any one of these increases the error rate noticeably.

---

## Week 2 Concepts Used

### Prompt chaining
The pipeline is a 5-step chain. Each step receives the *structured output* of the previous step,
not the raw text. This is the key insight:

```
parse_requirement() → dict
    ↓
partition_equivalence_classes(dict) → list
    ↓
analyze_boundary_values(dict, list) → list
    ↓
generate_test_cases(dict, list, list) → list
    ↓
evaluate_output(str, list) → dict
```

A single mega-prompt trying to do all five things at once produces worse output
and is much harder to debug when something goes wrong.

### Context window management
Requirements engineering documents can be large. This project keeps each call small:
pass only the structured data needed for that step, not the full raw document.
This is the first step toward RAG thinking — be selective about what goes into context.

### Instruction following vs. in-context learning
The prompts use **instruction-following** style, not few-shot examples.
Adding 1–2 example (input, output) pairs to Steps 3 and 4 would likely improve
boundary value accuracy — a natural next iteration.

---

## Week 3 Concepts Used

### LLM self-evaluation
Step 5 uses the same model to evaluate its own output. Key findings:
- The model is consistently **optimistic** (scores tend to be 0.3–0.5 points high)
- It reliably finds *structural* gaps (missing test cases for a class)
- It poorly catches *semantic* gaps (wrong expected result for a given input)
- The `confidence` field helps — "low" confidence scores should trigger human review

**Lesson**: LLM self-evaluation is a fast, cheap first filter. Not a substitute for
domain expert review. Treat it like CI — it catches the obvious bugs.

### Rubric design matters
First version had vague rubric items like "is the output good?". This produced
uniformly high scores with no actionable gaps. The final rubric uses:
- Concrete, binary-ish criteria ("are ALL EP classes covered?")
- Domain-specific dimensions (traceability, export_readiness)
- A `confidence` field to flag when the evaluator itself is uncertain

---

## What I'd do differently next time

1. **Few-shot examples in Steps 3–4** — BVA generation is the weakest step.
   Two or three worked examples in the prompt would improve accuracy significantly.

2. **Separate evaluation model** — Using the same model to evaluate its own output
   introduces optimism bias. A second call with a slightly different system prompt
   ("you are a critical reviewer, find flaws") produces more balanced scores.

3. **Async batch processing** — The five steps run sequentially. For a file with
   20 requirements, that's 100 API calls in serial. `asyncio` + `gather()` would
   give a ~5x speedup with no change to logic.

4. **Streaming for UX** — The CLI shows nothing until each step completes.
   Streaming would make the tool feel much faster for long requirements.

---

## Connection to ASPICE

For colleagues from the automotive world:

| req-testgen output | ASPICE work product |
|---|---|
| Parsed requirement | SWE.1: Software Requirements |
| Equivalence classes + BVA | SWE.4: Software Unit Test Specification |
| Test cases | SWE.4: Software Unit Test Cases |
| Evaluation gaps | SWE.1: Requirement quality review notes |
| DOORS CSV export | SWE.1/SWE.4 traceability matrix |

The `aspice_work_product` field in the parsed output maps requirements
to the correct ASPICE process area automatically.
