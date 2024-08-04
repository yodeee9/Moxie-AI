import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def generate_gpt_answer(prompt, model):
    completion = openai.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content
