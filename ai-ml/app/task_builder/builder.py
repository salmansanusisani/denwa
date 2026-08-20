"""Turns retrieved chunks into (a) condensed answer content and (b) a CALL-E task string + resultSchema.

This is the contract Backend's worker calls — see ai-ml/README.md "Contract with Backend".

TODO(ai/ml):
1. Condense the retrieved chunks into a compact, accurate answer-content block (an LLM summarization
   pass, or careful concatenation if chunks are already short).
2. Build the task string per docs/ARCHITECTURE.md Section 6's template:
   "Call back this customer, greet them, ask what they needed help with, and answer using ONLY
   the following verified info: {answer_content}. If you can't answer confidently, offer a human
   follow-up."
   Keep it within whatever length limit CALL-E's task field has (check docs).
3. Build result_schema as valid JSON Schema matching CallResult:
   { question_asked: str, answer_given: str, resolved: bool, needs_human_followup: bool }
4. PROMPT SAFETY: the task must explicitly forbid answering outside the provided content.
"""

RESULT_SCHEMA = {
    "type": "object",
    "required": ["question_asked", "resolved"],
    "properties": {
        "question_asked": {"type": "string"},
        "answer_given": {"type": "string"},
        "resolved": {"type": "boolean"},
        "needs_human_followup": {"type": "boolean"},
    },
}


def build_task(company_id: int, likely_topic: str) -> dict:
    """TODO(ai/ml): retrieve -> condense -> build task string. Return {"task": ..., "result_schema": ...}."""
    raise NotImplementedError
