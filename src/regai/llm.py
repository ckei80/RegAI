from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
)


def ask_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="qwen/qwen3.6-35b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content