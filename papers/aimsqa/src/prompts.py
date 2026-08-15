"""Criteria and QA prompt used in the paper pipeline."""

CRITERIA = {
    "approval": "Approval of the statement by the reporting entity's principal governing body.",
    "signature": "Signature by a responsible member, including name, position, and evidence of signature.",
    "c1 (reporting entity)": "Clear identification of the entity or entities required to report.",
    "c2 (structure)": "Legal or organisational structure, workforce, offices, brands, and owned or controlled entities.",
    "c2 (operations)": "The nature, types, and locations of activities undertaken by the entity.",
    "c2 (supply chains)": "Products, services, locations, categories, or other attributes of direct or indirect suppliers.",
    "c3 (risk description)": "Specific modern-slavery risks, incidents, regions, industries, commodities, or justified low-risk findings.",
    "c4 (risk mitigation)": "Concrete actions, policies, due diligence, training, reporting, or oversight used to mitigate risk.",
    "c4 (remediation)": "Concrete actions to remedy actual or hypothetical modern-slavery cases.",
    "c5 (effectiveness)": "Methods, metrics, reviews, audits, feedback, or KPIs used to assess effectiveness.",
    "c6 (consultation)": "Consultation with owned or controlled entities in preparing the statement.",
}

LABELS = list(CRITERIA)

QA_PROMPT = """You are analysing an Australian modern-slavery statement.
Answer the question using only the supplied excerpts and the criterion below. Do not guess.

Criterion:
{criterion}

Excerpts:
{context}

Question: {question}

Briefly explain the evidence, then finish with exactly one of:
FINAL ANSWER: YES
FINAL ANSWER: NO
FINAL ANSWER: NOT ENOUGH INFORMATION
"""
