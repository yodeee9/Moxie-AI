import json
import boto3
import os
import ldclient
from ldclient.config import Config
from ldclient import Context

ldclient.set_config(Config("sdk-fa09e802-0d20-4337-820a-d1a9ce324d3a"))
client = ldclient.get()

def lambda_handler(event, context):
    try:
        context = Context.builder("example-user-key-1").name("Sandy").build()
        flag_value = client.variation("ai-model-provider", context, False)

        if flag_value == "Claude-Agent-v1":
            agent_id = os.getenv('CLAUD_AGENT_ID_V1')
            agent_alias_id = os.getenv('CLAUD_AGENT_ALIAS_ID_V1')
        elif flag_value == "Claude-Agent-v2":
            agent_id = os.getenv('CLAUD_AGENT_ID_V2')
            agent_alias_id = os.getenv('CLAUD_AGENT_ALIAS_ID_V2')
        # elif flag_value == "Cohere-Agent-v1":
        #     agent_id = os.getenv('COHERE_AGENT_ID_V1')
        #     agent_alias_id = os.getenv('COHERE_AGENT_ALIAS_ID_V1')
        # else:
        #     agent_id = os.getenv('CLAUD_AGENT_ID_V1')
        #     agent_alias_id = os.getenv('CLAUD_AGENT_ALIAS_ID_V1')

        # Extract the body from the event
        body = json.loads(event['body'])

        # Extract user input and session_id from the body
        user_input = body.get('input', 'hello')
        session_id = body.get('session_id', '123')
        print(f"Session ID: {session_id}")
        print(f"User Input: {user_input}")
        
        # Get agentId and agentAliasId from environment variables

        
        # Initialize the Bedrock client
        bedrockClient = boto3.client(service_name="bedrock-agent-runtime")
         
        response = bedrockClient.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=user_input,
        )
        
        print(response)

        completion = ""

        for event in response.get("completion", []):
            chunk = event.get("chunk", {})
            completion += chunk.get("bytes", b'').decode()
            
        print(f"Completion: {completion}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'response': completion})
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
