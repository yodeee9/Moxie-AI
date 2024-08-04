import anthropic
from config import ANTHROPIC_API_KEY


def generate_claude_answer(prompt, model):
    client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
