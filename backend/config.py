import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

COMPARTMENT_ID = os.getenv("COMPARTMENT_ID")

OCTO_AI_API_KEY_LLAMA8B = os.getenv("OCTO_AI_API_KEY_LLAMA8B")
D_ID_API_KEY =  os.getenv("D-ID-API-KEY")

MODEL_OPTIONS = [
    "octo-llama-8b",
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo-preview",
    "cohere-command-nightly",
    "cohere-command-light-nightly",
    "cohere-command-r",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-2.1",
]

PROMPT_EXAMPLES = {
    "1": "Please analyze the most recent user activity logs",
    "2": "Please summarize the recent user's actions",
    "3": "What are the most viewed pages user visited?",
}
