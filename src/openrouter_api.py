from openai import OpenAI


class OpenRouterAPI:
    def __init__(self, model_name: str, api_key_path: str) -> None:
        self.model_name = model_name

        api_key = open(api_key_path, encoding="utf-8").read().strip()

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def generate(self, prompt: str) -> str:
        content = [{"type": "input_text", "text": prompt}]

        input_items = [
            {
                "role": "user",
                "content": content,
            }
        ]

        response = self.client.responses.create(
            model=self.model_name,
            input=input_items,  # type: ignore
        )

        output = response.output_text

        return output
