# Prompts

Every prompt used in the [AIMS.au](../papers/aims-au/) and [AIMSCheck](../papers/aimscheck/)
experiments, as plain text — one file per criterion per variant, so they can be diffed, reviewed,
and reused without opening a Word document.

Each file contains the prompt exactly as sent to the model. `{}` marks where the target sentence is
substituted; where a second `{}` appears, it takes the surrounding context block.

← [Back to Project AIMS](../README.md)

---

## AIMS.au — [`aims-au/`](aims-au/)

Zero-shot classification prompts, 11 criteria × 2 input settings. The *no-context* variant sees only
the target sentence; the *with-context* variant also receives ±100 words of surrounding text.

| Criterion | No context | With context |
|---|---|---|
| Approval | [`approval.no-context.txt`](aims-au/approval.no-context.txt) | [`approval.with-context.txt`](aims-au/approval.with-context.txt) |
| Signature | [`signature.no-context.txt`](aims-au/signature.no-context.txt) | [`signature.with-context.txt`](aims-au/signature.with-context.txt) |
| C1 — Reporting entity | [`criteria-1.no-context.txt`](aims-au/criteria-1.no-context.txt) | [`criteria-1.with-context.txt`](aims-au/criteria-1.with-context.txt) |
| C2 — Structure | [`structure.no-context.txt`](aims-au/structure.no-context.txt) | [`structure.with-context.txt`](aims-au/structure.with-context.txt) |
| C2 — Operations | [`operations.no-context.txt`](aims-au/operations.no-context.txt) | [`operations.with-context.txt`](aims-au/operations.with-context.txt) |
| C2 — Supply chains | [`supply-chains.no-context.txt`](aims-au/supply-chains.no-context.txt) | [`supply-chains.with-context.txt`](aims-au/supply-chains.with-context.txt) |
| C3 — Risk description | [`risk-description.no-context.txt`](aims-au/risk-description.no-context.txt) | [`risk-description.with-context.txt`](aims-au/risk-description.with-context.txt) |
| C4 — Risk mitigation | [`risk-mitigation.no-context.txt`](aims-au/risk-mitigation.no-context.txt) | [`risk-mitigation.with-context.txt`](aims-au/risk-mitigation.with-context.txt) |
| C4 — Remediation | [`risk-remediation.no-context.txt`](aims-au/risk-remediation.no-context.txt) | [`risk-remediation.with-context.txt`](aims-au/risk-remediation.with-context.txt) |
| C5 — Effectiveness | [`assessment-of-effectiveness.no-context.txt`](aims-au/assessment-of-effectiveness.no-context.txt) | [`assessment-of-effectiveness.with-context.txt`](aims-au/assessment-of-effectiveness.with-context.txt) |
| C6 — Consultation | [`consultation.no-context.txt`](aims-au/consultation.no-context.txt) | [`consultation.with-context.txt`](aims-au/consultation.with-context.txt) |

These prompts encode the annotation guidelines in prose. The Approval prompt, for instance, spells
out that the Act forbids delegating approval to an executive committee, and that "considered by the
board" does not satisfy the criterion — the same distinctions the human annotators applied. Reading
them is the fastest way to understand what each label actually means.

## AIMSCheck — [`aimscheck/`](aimscheck/)

Chain-of-thought prompts across nine shared criteria, in zero-shot and few-shot variants. These
target UK statements under the UK Modern Slavery Act.

| Criterion | Zero-shot CoT | Few-shot CoT |
|---|---|---|
| Approval | [`approval.zero-shots-cot.txt`](aimscheck/approval.zero-shots-cot.txt) | [`approval.few-shots-cot.txt`](aimscheck/approval.few-shots-cot.txt) |
| Signature | [`signature.zero-shots-cot.txt`](aimscheck/signature.zero-shots-cot.txt) | [`signature.few-shots-cot.txt`](aimscheck/signature.few-shots-cot.txt) |
| C2 — Structure | [`c2-structure.zero-shots-cot.txt`](aimscheck/c2-structure.zero-shots-cot.txt) | [`c2-structure.few-shots-cot.txt`](aimscheck/c2-structure.few-shots-cot.txt) |
| C2 — Operations | [`c2-operations.zero-shots-cot.txt`](aimscheck/c2-operations.zero-shots-cot.txt) | [`c2-operations.few-shots-cot.txt`](aimscheck/c2-operations.few-shots-cot.txt) |
| C2 — Supply chains | [`c2-supply-chains.zero-shots-cot.txt`](aimscheck/c2-supply-chains.zero-shots-cot.txt) | [`c2-supply-chains.few-shots-cot.txt`](aimscheck/c2-supply-chains.few-shots-cot.txt) |
| C3 — Risks | [`c3-risks.zero-shots-cot.txt`](aimscheck/c3-risks.zero-shots-cot.txt) | [`c3-risks.few-shots-cot.txt`](aimscheck/c3-risks.few-shots-cot.txt) |
| C4 — Mitigation | [`c4-mitigation.zero-shots-cot.txt`](aimscheck/c4-mitigation.zero-shots-cot.txt) | [`c4-mitigation.few-shots-cot.txt`](aimscheck/c4-mitigation.few-shots-cot.txt) |
| C4 — Remediation | [`c4-remediation.zero-shots-cot.txt`](aimscheck/c4-remediation.zero-shots-cot.txt) | [`c4-remediation.few-shots-cot.txt`](aimscheck/c4-remediation.few-shots-cot.txt) |
| C5 — Assessment | [`c5-assessment.zero-shots-cot.txt`](aimscheck/c5-assessment.zero-shots-cot.txt) | [`c5-assessment.few-shots-cot.txt`](aimscheck/c5-assessment.few-shots-cot.txt) |

The few-shot files carry worked examples with reasoning. Worth noting alongside the
[AIMSCheck results](../papers/aimscheck/#results): chain-of-thought on its own *reduced* GPT-4o's
macro F1 (0.601 → 0.559), and only overtook plain prompting once these examples were added (0.617).
Both variants are here so that result can be reproduced.

## Source

Extracted from `AIMSPrompts.docx`, kept in this folder as the original record. If you edit a prompt,
edit the `.txt` — it is the version of record for reproduction.

## License and citation

[CC-BY-4.0](../LICENSE). If you reuse or adapt these prompts, cite the paper they come from —
[AIMS.au](../papers/aims-au/#citation) (ICLR 2025) or
[AIMSCheck](../papers/aimscheck/#citation) (ACL 2025).
