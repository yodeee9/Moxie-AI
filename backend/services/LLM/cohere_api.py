import cohere

from config import COHERE_API_KEY


def generate_cohere_answer(prompt, model):
    model = model.replace("cohere-", "")
    co = cohere.Client(COHERE_API_KEY)

    chat = co.chat(message=prompt, model=model)

    return chat.text
