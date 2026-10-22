"""Single place that talks to the LLM. Swap provider here only."""

import ollama

MODEL = "llama3.1:8b"


def ask(prompt: str, system: str | None = None, json_mode: bool = False) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model=MODEL,
        messages=messages,
        format="json" if json_mode else None,
        options={"temperature": 0},
    )
    return response["message"]["content"]