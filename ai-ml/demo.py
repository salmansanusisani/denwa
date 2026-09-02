"""End-to-end AI/ML demo for the Denwa hackathon.

Seeds a sample company's FAQ/policy into the in-memory store, then verifies the
Definition-of-Done checks we can test locally:
  - chunk + embed with zero manual cleanup
  - retrieval returns relevant chunks for realistic questions
  - build_task produces a valid task string + resultSchema

Run (from ai-ml/):  python -m demo   (no API keys required — uses local fallback)
"""
from __future__ import annotations

import json

from app.embeddings.embedder import embedding_dim
from app.pipeline import build, ingest_documents
from app.retriever.retriever import retrieve_for_topic
from app.vector_store import store

COMPANY_ID = 1

SAMPLE_FAQ = """\
Q: Do you offer free shipping?
A: Yes. We offer free standard shipping on all US orders over $50. Orders below $50
are charged a flat $6.99. Express shipping is available for an additional $12.

Q: What is the return policy?
A: You can return any unused item within 30 days of delivery for a full refund.
Return shipping is free on all orders. Refunds are issued to the original payment
method within 5-7 business days after we receive the item.

Q: How long does delivery take?
A: Standard US delivery takes 3-5 business days after dispatch. Express delivery
takes 1-2 business days. International orders take 7-14 business days depending on
customs. We dispatch from our Cincinnati, Ohio warehouse within 24 hours.

Q: What is the 15-inch laptop price?
A: The 15-inch Pro Laptop currently sells for $1,249.99 including tax. It ships with
a one-year manufacturer warranty and a free laptop sleeve. Student discounts of 10%
apply with a valid student email.

Q: Do you ship internationally?
A: Yes, we ship to Canada, the UK, Australia and Singapore. International shipping
is a flat $24.99, and delivery takes 7-14 business days. Taxes and import duties are
calculated at checkout and are shown before you pay.

Q: What payment methods do you accept?
A: We accept Visa, Mastercard, American Express, Apple Pay, Google Pay and PayPal.
We also offer buy-now-pay-later through Klarna on orders between $100 and $2,000.
"""

TEST_QUESTIONS = [
    "I want to return a laptop I bought, how long do I have?",
    "What does shipping to international countries cost?",
    "How much is the 15 inch laptop and does it come with warranty?",
    "Do you offer free shipping and how fast is delivery?",
    "Can I pay with Apple Pay or split my payment?",
]


def main() -> None:
    store.clear()

    n_chunks = ingest_documents(COMPANY_ID, [(1, SAMPLE_FAQ)])
    print(f"Chunked + embedded {n_chunks} chunks (embedding dim={embedding_dim()})\n")

    for q in TEST_QUESTIONS:
        hits = retrieve_for_topic(COMPANY_ID, q, k=2)
        print(f"Q: {q}")
        for h in hits:
            prefix = h.replace("\n", " ")[:110]
            print(f"  -> {prefix}")
        print()

    task_payload = build(COMPANY_ID, "returns and refunds")
    print(f"TASK length: {len(task_payload['task'])} chars (limit ~3000)")
    print("--- task (first 350 chars) ---")
    print(task_payload["task"][:350])
    print("--- result_schema ---")
    print(json.dumps(task_payload["result_schema"], indent=2))

    req = task_payload["result_schema"].get("required", [])
    assert isinstance(task_payload["task"], str) and task_payload["task"].strip()
    assert set(["question_asked", "answer_given", "resolved", "needs_human_followup"]).issubset(req)
    print("\nOK: result_schema is valid and matches the CallResult contract.")


if __name__ == "__main__":
    main()