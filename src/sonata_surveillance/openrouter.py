"""Thin OpenRouter client.

Kept deliberately small: one method, one prompt in, one string out. Every model
under test is reached through the same interface so that the only difference
between runs is the model id and the prompt.

Note for anyone comparing runs: this client uses the OpenAI *Responses* API and
leaves sampling parameters at the provider default. The browser app in
``webapp/`` calls ``/chat/completions`` instead and pins temperature (0.7 for
generation, 0.0 for evaluation). Results produced by the two paths are therefore
not strictly comparable -- see ``docs/methodology.md``.
"""

from __future__ import annotations

from openai import OpenAI

from . import config

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterAPI:
    """Single-model client against OpenRouter."""

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        temperature: float | None = None,
    ) -> None:
        """
        Args:
            model_name: OpenRouter model id, e.g. ``openai/gpt-5.5``.
            api_key: Key to use. Resolved from the environment when omitted.
            temperature: Left unset by default, which means the provider's own
                default applies. Pin it if a run needs to be reproducible.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key if api_key is not None else config.read_api_key(),
        )

    def generate(self, prompt: str) -> str:
        """Send ``prompt`` as a single user turn and return the text response."""
        kwargs = {}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature

        response = self.client.responses.create(
            model=self.model_name,
            input=[
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }
            ],  # type: ignore[arg-type]
            **kwargs,
        )
        return response.output_text
