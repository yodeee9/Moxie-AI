from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.LLM.agent import llm_agent  
from services.optional_prompt.prompts import SYSTEM_PROMPT_AUGMENTED_JP
from services.search_data.manual_vector_search import create_vector_store, search_vector_store
from services.LLM.octo_llama_8b import generate_octo_llama_answer

app = FastAPI()
vector_store = create_vector_store()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            user_input = data.get('user_input', '')
            await llm_agent(user_input, websocket)
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
