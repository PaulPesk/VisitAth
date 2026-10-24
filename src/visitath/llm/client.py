"""Single place that talks to the LLM. Swap provider here only."""

import os

import ollama

MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

_client = ollama.Client(host=HOST)


def ask(prompt: str, system: str | None = None, json_mode: bool = False) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = _client.chat(
        model=MODEL,
        messages=messages,
        format="json" if json_mode else None,
        options={"temperature": 0},
    )
    return response["message"]["content"]