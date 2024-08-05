import json
from time import sleep

import requests
from openai import OpenAI
import os
import logging
import pandas as pd
from services.optional_prompt.prompts import SYSTEM_PROMPT_AUGMENTED_JP
from config import OPENAI_API_KEY
from tools.langsmith import langsmith_evaluator
from datetime import datetime
from langsmith.wrappers import wrap_openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

openai_client = OpenAI(
    api_key=OPENAI_API_KEY
)
client = wrap_openai(openai_client)


chat_history = []

tool_definitions = [
    {
        "name": "statement_for_user",
        "description": "The tool that you call when you're trying to speak to the user. Use it to keep them abreast of your plans, buy some time for long running operations, or to answer their query. It's so important things, you must make sure your reponse arguments are in the correct **object** format.",
        "parameters": {
            "type": "object",
            "properties": {
                "statement": {
                    "type": "string",
                    "description": "The statement that is spoken out loud to the user."
                }
            },
            "required": ["statement"]
        }
    },
    # {
    #     "name": "check_user_answered_all_items",
    #     "description": "The tool checks if the user has answered all the necessary items. If not, you should ask more questions to gather the required information.",
    #     "parameters": {
    #         "type": "object",
    #         "properties": {
    #             "isCityView": {"type": "boolean"},
    #             "schools": {"type": "boolean"},
    #             "bedsMax": {"type": "integer"},
    #             "maxPrice": {"type": "integer"},
    #             "location": {"type": "string"}
    #         },
    #         "required": ["isCityView", "schools", "bedsMax", "maxPrice", "location"]
    #     }
    # },
    {
        "name": "check_user_answered_items",
        "description": "The tool checks if the user has answered at least 3 necessary items. If not, you should ask more questions to gather the required information.",
        "parameters": {
            "type": "object",
            "properties": {
                "isAnswered": {
                    "type": "boolean",
                    "description": "Whether the user has answered at least 3 items."
                },
            },
            "required": ["isAnswered"]
        }
    },
    {
        "name": "search_apartments",
        "description": "This tool calls the Dummy API to search for apartments based on user-provided preferences. You can use this tool only after you have confirmed that the user has provided all the necessary parameters.",
        "parameters": {
            "type": "object",
            "properties": {
                "isCityView": {
                    "type": "boolean",
                    "description": "Whether the user wants a city view."
                    },
                "schools": {
                    "type": "string",
                    "description": "The user's preference for schools. elementary, middle, high, or all."
                    },
                "bedsMax": {
                    "type": "integer",
                    "description": "The maximum number of beds the user wants."
                    },
                "maxPrice": {
                    "type": "integer",
                    "description": "The maximum price the user is willing to pay."
                    },
                "location": {
                    "type": "string",
                    "description": "The location the user is interested in."
                    }
            },
            "required": []
        }
    },
    {
        "name": "all_tasks_completed", 
        "description": "The FINAL tool that you call when you feel you've fully answered the user's prompt AND called all other tools needed to complete it. You must have just spoken to the user confirming you completed their task before calling this.", 
        "parameters": {}
    },
]

def get_chat_history():
    return chat_history


async def llm_agent(user_input, websocket: WebSocket):
    messages = get_chat_history()
    if len(messages) == 0:
        messages.append({"role": "system", "content": SYSTEM_PROMPT_AUGMENTED_JP})
    messages.append({"role": "user", "content": user_input})
    print(f"messages: {messages}")
    final_response = None
    while not final_response:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            max_tokens=1000,
            messages=messages,
            functions=tool_definitions
        )
        response_message = response.choices[0].message
        tool_call = response_message.function_call

        if tool_call:
            function_response = await handle_tool_call(websocket, tool_call)
            messages.append({"role": "system", "name": tool_call.name, "content": json.dumps(function_response)})
        else:
            final_response = response_message.content
            # langsmith_evaluator(final_response)

    return final_response

async def handle_tool_call(websocket,tool_call):
    function_name = tool_call.name
    function_args = json.loads(tool_call.arguments)

    function_map = {
        "statement_for_user": handle_statement_for_user,
        "check_user_answered_items": handle_check_user_answered_items,
        "search_apartments": handle_search_apartments,
        "all_tasks_completed": handle_ws_disconnect,
    }

    print(f"Function name: {function_name}")
    print(f"Function args: {function_args}")

    if function_name in function_map:
        return await function_map[function_name](websocket, **function_args)
    else:
        logging.error(f"Unknown function name: {function_name}")
        return None

async def handle_statement_for_user(websocket,statement):
    await websocket.send_json({'sender': 'system', 'message': statement})
    return statement

async def handle_ws_disconnect(websocket):
    # await websocket.close()
    return

# async def handle_check_user_answered_all_items(websocket,isCityView, schools, bedsMax, maxPrice, location):
#     missing_items = []
#     if isCityView is None:
#         missing_items.append("isCityView")
#     if schools is None:
#         missing_items.append("schools")
#     if bedsMax is None:
#         missing_items.append("bedsMax")
#     if maxPrice is None:
#         missing_items.append("maxPrice")
#     if location is None:
#         missing_items.append("location")
    
#     if missing_items:
#         return {"missingItems": missing_items}
#     else:
#         return {"allItemsAnswered": True}
async def handle_check_user_answered_items(websocket, isAnswered):
    if isAnswered:
        return {"allItemsAnswered": True}
    else:
        return {"allItemsAnswered": False}

async def handle_search_apartments(websocket,isCityView, schools, bedsMax, maxPrice, location):
    params = {
        "isCityView": isCityView,
        "schools": schools,
        "bedsMax": bedsMax,
        "maxPrice": maxPrice,
        "location": location
    }
    # response = requests.get(DUMMY_API_URL, params=params)
    # return response.json()
    return 'dummy response'