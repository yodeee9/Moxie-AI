import json
from time import sleep

import requests
from openai import OpenAI
import logging
import pandas as pd
from services.tools.zillow import search_properties
from services.optional_prompt.prompts import SYSTEM_PROMPT_AUGMENTED_JP
from config import MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_SEND_TO, OPENAI_API_KEY, YOUCOM_API_KEY
from tools.langsmith import langsmith_evaluator
from datetime import datetime
from langsmith.wrappers import wrap_openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import requests

openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
)
client = wrap_openai(openai_client)


chat_history = []

tool_definitions = [
    {
        "name": "statement_for_user",
        "description": "The tool that you call when you're trying to speak to the user. Use it to keep them abreast of your plans, buy some time for long running operations, or to answer their query. Make sure your summary is nice and formatted with line break codes.",
        "parameters": {
            "type": "object",
            "properties": {
                "statement": {
                    "type": "string",
                    "description": "The statement that is spoken out loud to the user with nice format including line break codes(\n)."
                }
            },
            "required": ["statement"]
        }
    },
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
                    "description": "Whether the user wants a city view.",
                },
                "schools": {
                    "type": "string",
                    "description": "The user's preference for schools. elementary, middle, high, or all.",
                },
                "bedsMax": {
                    "type": "integer",
                    "description": "The maximum number of beds the user wants.",
                },
                "maxPrice": {
                    "type": "integer",
                    "description": "The maximum price the user is willing to pay.",
                },
                "location": {
                    "type": "string",
                    "description": "The location the user is interested in.",
                },
                "isWaterfront": {
                    "type": "boolean",
                    "description": "Whether the user wants a waterfront view.",
                },
                "isMountainView": {
                    "type": "boolean",
                    "description": "Whether the user wants a mountain view.",
                },
                "isWaterView": {
                    "type": "boolean",
                    "description": "Whether the user wants a water view.",
                },
                "isParkView": {
                    "type": "boolean",
                    "description": "Whether the user wants a park view.",
                }
            },
            "required": []
        }
    },
    {
        "name": "show_apartments_search_results",
        "description": "The tool that you call to show the top 3 recommended apartments in the search results to the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "apartments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the apartment."
                            },
                            "price": {
                                "type": "integer",
                                "description": "The price of the apartment."
                            },
                            "beds": {
                                "type": "integer",
                                "description": "The number of beds in the apartment."
                            },
                            "address": {
                                "type": "string",
                                "description": "The address of the apartment."
                            },
                            "imgSrc": {
                                "type": "string",
                                "description": "The image source of the apartment."
                            },
                            "detailUrl": {
                                "type": "string",
                                "description": "The URL of the apartment."
                            },
                            "reason": {
                                "type": "string",
                                "description": "The reason why this apartment is recommended."
                            },
                            "latitude": {
                                "type": "number",
                                "description": "The latitude of the apartment."
                            },
                            "longitude": {
                                "type": "number",
                                "description": "The longitude of the apartment."
                            }
                        },
                        "required": ["name", "price", "beds", "address", "imgSrc", "detailUrl", "reason", "latitude", "longitude"]
                    }
                }
            },
            "required": ["apartments"]
        }
    },
    {
        "name": "search_crime_news_nearby",
        "description": "The tool that you call to search the internet about nearby crime news. You must call this tool after you have called the search_apartments tool.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to search for crime news."
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "summary_of_search_crime_results",
        "description": "The tool that you call to summarize the search results of crime news to the user. You must call this tool after you have called the search_crime_news_nearby tool. Make sure your summary is nice and formatted with line break codes.",
        "parameters": {
            "type": "object",
            "properties": {
                "crime_news_summary": {
                    "type": "string",
                    "description": "The summary of the crime news with nice format including line break codes(\n). And your thouhts about the crime news which make customer feel safety of the area ."
                }
            },
            "required": ["crime_news"]
        }
    },
    {
        "name": "send_email_to_user",
        "description": "The tool that you call to send an email to the user about the apartment search results and crime news summary with the nice HTML formatted content.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The HTML content of the email sent. Format it very nicely."
                },
                "subject": {
                    "type": "string",
                    "description": "The subject of the email to be sent to the user."
                }
            },
            "required": ["content", "subject"]
        }   
    },
    {
        "name": "send_email_to_owner",
        "description": "The tool that you call to send an email to the owner of the apartment about the user's interest in the apartment. In the email, include the user's contact information which is dummy data.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The HTML content of the email sent. Format it very nicely."
                },
                "subject": {
                    "type": "string",
                    "description": "The subject of the email to be sent to the owner."
                }
            },
            "required": ["content", "subject"]
        }
    },
    {
        "name": "all_tasks_completed", 
        "description": "The FINAL tool that you call when you feel you've fully answered the user's prompt AND called all other tools needed to complete it. You must have just spoken to the user confirming you completed their task before calling this.", 
        "parameters": {}
    }
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
        print(f"Tool call: {tool_call}")

        if tool_call is None:
            final_response = response_message.content
            break 

        if tool_call:
            if "functions:" in tool_call.name:
                tool_call.name = tool_call.name.replace("functions:", "")
            function_response = await handle_tool_call(websocket, tool_call)
            messages.append({"role": "system", "name": tool_call.name, "content": json.dumps(function_response)})
        else:
            final_response = response_message.content

    return final_response

async def handle_tool_call(websocket,tool_call):
    function_name = tool_call.name
    function_args = json.loads(tool_call.arguments)

    function_map = {
        "statement_for_user": handle_statement_for_user,
        "check_user_answered_items": handle_check_user_answered_items,
        "search_apartments": handle_search_apartments,
        "all_tasks_completed": handle_ws_disconnect,
        "show_apartments_search_results": show_apartments_search_results,
        "search_crime_news_nearby": handle_search_crime_news_nearby,
        "summary_of_search_crime_results": handle_summary_of_search_crime_results,
        "send_email_to_user": send_email_to_user,
        "send_email_to_owner": send_email_to_owner
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
    return

async def handle_check_user_answered_items(websocket, isAnswered):
    print(f"Is Answered: {isAnswered}")
    if isAnswered:
        return {"allItemsAnswered": True}
    else:
        return {"allItemsAnswered": False}

async def handle_search_apartments(websocket, isCityView=None, schools=None, bedsMax=None, maxPrice=None, location=None, isWaterfront=None, isMountainView=None, isWaterView=None, isParkView=None):
    await websocket.send_json({'sender': 'system', 'message': 'OK, I am searching for apartments that match your preferences.'})
    
    params = {
        "isCityView": isCityView,
        "schools": schools,
        "bedsMax": bedsMax,
        "maxPrice": maxPrice,
        "location": location,
        "isWaterfront": isWaterfront,
        "isMountainView": isMountainView,
        "isWaterView": isWaterView,
        "isParkView": isParkView
    }

    filtered_params = {key: value for key, value in params.items() if value is not None}
    
    try:
        response = search_properties(filtered_params)
        print(f"Response: {response}")
        if response['statusCode'] == 200:
            response_body = json.loads(response['body'])
            return response_body
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


async def show_apartments_search_results(websocket, apartments):
    await websocket.send_json({'sender': 'system', 'message': 'Here are the apartments that match your preferences.'})
    for apartment in apartments:
        response_obj = {
            'sender': 'system',
            'response_obj': {
                'name': apartment['name'],
                'price': apartment['price'],
                'beds': apartment['beds'],
                'address': apartment['address'],
                'imgSrc': apartment['imgSrc'],
                'detailUrl': apartment['detailUrl'],
                'reason': apartment['reason'],
                'latitude': apartment['latitude'],
                'longitude': apartment['longitude']
            }
        }
        await websocket.send_json(response_obj)
    return
        
async def handle_search_crime_news_nearby(websocket, city):
    await websocket.send_json({'sender': 'system', 'message': 'I am searching for crime news in your area.'})
    url = "https://api.ydc-index.io/news"

    headers = {"X-API-Key": YOUCOM_API_KEY}
    query = f"crime {city}"
    params = {"query": f"crime {city}",
              "count": 3,
              "recency": "week",}
    response = requests.get(f'{url}?={query}', headers=headers, params=params)
    print(f"Response: {response.json()}")
    return response.json()


async def handle_summary_of_search_crime_results(websocket, crime_news_summary):
    await websocket.send_json({'sender': 'system', 'message': 'Here are the crime news in your area.'})
    await websocket.send_json({'sender': 'system', 'message': crime_news_summary})
    return {"crime_news_summary": crime_news_summary}

async def send_email_to_user(websocket, content: str, subject: str) -> str:
    api_key = MAILGUN_API_KEY
    domain = MAILGUN_DOMAIN
    send_to = MAILGUN_SEND_TO
    
    if not api_key or not domain:
        raise ValueError("MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables must be set")
    data={"from": f"Moxie <mailgun@{domain}>",
              "to": [send_to],
              "subject": "Potential Apartments ",
              "html": content}

    result = requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data=data
        )
    await websocket.send_json({'sender': 'system', 'message': 'I sent an email to you about the apartment search results.\n Anthing else I can help you with?'})
    return "Email sent!"

async def send_email_to_owner(websocket, content: str, subject: str) -> str:
    api_key = MAILGUN_API_KEY
    domain = MAILGUN_DOMAIN
    send_to = MAILGUN_SEND_TO
    
    if not api_key or not domain:
        raise ValueError("MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables must be set")
    data={"from": f"Moxie <mailgun@{domain}>",
              "to": [send_to],
              "subject": "Potential Apartments ",
              "html": content}

    result = requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data=data
        )
    await websocket.send_json({'sender': 'system', 'message': 'I sent an email to the apartment owner about your interest\n Anthing else I can help you with?'})
    return "Email sent!"