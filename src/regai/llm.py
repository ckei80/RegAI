from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
)


def ask_llm(
    prompt: str,
    response_format: dict | None = None,
) -> str:
    response = client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
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