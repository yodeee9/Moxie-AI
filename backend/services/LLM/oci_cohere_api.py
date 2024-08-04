# import oci
# from oci.generative_ai_inference import GenerativeAiInferenceClient
# from oci.generative_ai_inference.models import (
#     GenerateTextDetails,
#     OnDemandServingMode,
#     CohereLlmInferenceRequest,
# )
# from config import COMPARTMENT_ID

# config = oci.config.from_file()
# config["region"] = "us-chicago-1"
# compartment_id = COMPARTMENT_ID


# def generate_oci_cohere_answer(prompt, model):
#     # model = model.replace("cohere-", "")

#     client = GenerativeAiInferenceClient(config=config)

#     response = client.generate_text(
#         GenerateTextDetails(
#             compartment_id=compartment_id,
#             inference_request=CohereLlmInferenceRequest(prompt=prompt, max_tokens=4096),
#             serving_mode=OnDemandServingMode(model_id="cohere.command"),
#         )
#     ).data

#     return response.inference_response.generated_texts[0].text
