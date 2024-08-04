from flask import Flask, request, jsonify
# from services.LLM.oci_cohere_api import generate_oci_cohere_answer
from services.optional_prompt.prompts import SYSTEM_PROMPT_AUGMENTED_JP
from services.search_data.manual_vector_search import create_vector_store, search_vector_store
from services.LLM.octo_llama_8b import generate_octo_llama_answer
from services.LLM.claude_api import generate_claude_answer
from services.LLM.gpt_api import generate_gpt_answer
from services.LLM.cohere_api import generate_cohere_answer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
vector_store = create_vector_store()

@app.route('/generate_answer', methods=['POST'])
def generate_answer():
    user_input = request.json.get('user_input', '')
    prompt = user_input
    retreived_context = search_vector_store(
        user_input, vector_store
    )
    print(retreived_context)
    prompt = SYSTEM_PROMPT_AUGMENTED_JP.format(
        question=user_input,
        retreived_context=retreived_context,
    )
    print("generating answer")
    answer = generate_octo_llama_answer(prompt,"octo-llama-8b")
    print(answer)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)