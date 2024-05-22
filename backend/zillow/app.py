import json
import boto3
import os


def lambda_handler(event, context):
    try:
        # Extract the body from the event
        body = json.loads(event['body'])

        # Extract user input and session_id from the body
        user_input = body.get('input', 'hello')
        session_id = body.get('session_id', '123')
        print(f"Session ID: {session_id}")
        print(f"User Input: {user_input}")

        # Get agentId and agentAliasId from environment variables
        agent_id = os.getenv('AGENT_ID')
        agent_alias_id = os.getenv('AGENT_ALIAS_ID')

        # Initialize the Bedrock client
        client = boto3.client(service_name="bedrock-agent-runtime")

        response = client.invoke_agent(
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
