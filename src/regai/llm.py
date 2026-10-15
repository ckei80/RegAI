from openai import OpenAI

from regai.config import load_ai_config


def ask_llm(prompt: str, response_format: dict | None = None) -> str:
    config = load_ai_config()

    client = OpenAI(
        base_url=config.base_url,
        api_key=config.api_key,
    )

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
        response_format=response_format,
    )

    return response.choices[0].message.content