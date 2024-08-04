import json
from octoai.text_gen import ChatMessage

from octoai.client import OctoAI
from config import OCTO_AI_API_KEY_LLAMA8B


def generate_octo_llama_answer(prompt, model):
    print("Generating answer")
    client = OctoAI(
        api_key=OCTO_AI_API_KEY_LLAMA8B,
    )
    completion = client.text_gen.create_chat_completion(
	    max_tokens=1025,
	    messages=[
		    ChatMessage(
			    content=prompt,
			    role="system"
		    ),
	    ],
	    model="meta-llama-3-8b-instruct",
	    presence_penalty=0,
	    temperature=0.1,
	    top_p=0.9
    )
    answer = completion.choices[0].message.content
    return answer