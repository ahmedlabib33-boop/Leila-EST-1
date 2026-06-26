import os


DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "25"))


def _fallback_lesson(prompt, reason):
    topic = "this lesson"
    for marker in ("TOPIC:", "TOPIC", "lesson for:"):
        if marker in prompt:
            topic = prompt.split(marker, 1)[1].strip().splitlines()[0].strip() or topic
            break

    return f"""
AI status: local AI is not available right now ({reason}).

Here is a built-in expert explanation for {topic}:

TOPIC OVERVIEW:
This lesson is important because EST questions often test whether you can notice the exact rule, avoid common traps, and choose the most precise answer.

CORE RULE:
Read the rule carefully, identify the tested grammar or math idea, and apply it step by step instead of guessing from how the answer sounds.

SIMPLE EXPLANATION:
Start with the basic meaning. Then check the structure, formula, or sentence pattern. The correct answer must match both meaning and grammar.

STEP-BY-STEP METHOD:
1. Identify what the question is testing.
2. Underline the key words, numbers, or grammar signal.
3. Remove answer choices that break the rule.
4. Choose the answer that is correct, clear, and complete.

COMMON MISTAKES:
Students often choose an answer that sounds familiar but does not fully match the rule. Always check the exact structure.

TRAP PATTERNS:
Watch for extra words, misleading phrases, wrong agreement, wrong tense, unclear reference, and answers that are partly correct but incomplete.

SMART TIP:
If two answers look close, pick the one that is more specific, more grammatical, and more directly supported by the rule.

MINI SUMMARY:
Understand the rule first, apply it slowly, and use the explanation to learn why the right answer is right.
""".strip()


def generate_text(prompt):
    try:
        import ollama
    except Exception as exc:
        return _fallback_lesson(prompt, f"ollama package is not installed: {exc}")

    try:
        client = ollama.Client(timeout=OLLAMA_TIMEOUT_SECONDS)
        response = client.chat(
            model=DEFAULT_OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return response["message"]["content"]
    except Exception as exc:
        return _fallback_lesson(prompt, f"Ollama/{DEFAULT_OLLAMA_MODEL} failed: {exc}")
