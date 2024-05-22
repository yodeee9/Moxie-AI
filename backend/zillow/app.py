import json
import boto3
import os
import http.client
import urllib.parse


def lambda_handler(event, context):
    try:
        # print('event', event['location'])

        location = urllib.parse.quote(event['location'])
        maxPrice = urllib.parse.quote(event['maxPrice'])
        bedsMax = urllib.parse.quote(event['bedsMax'])
        schools = urllib.parse.quote(event['schools'])
        isCityView = urllib.parse.quote(event['isCityView'])

        conn = http.client.HTTPSConnection("zillow-com1.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': "c754b740e1mshbde5b0dfae21d33p113bbdjsn555c70485622",
            'x-rapidapi-host': "zillow-com1.p.rapidapi.com"
        }
        conn.request("GET", f"/propertyExtendedSearch?location={location}&maxPrice={
                     maxPrice}&bedsMax={bedsMax}&schools={schools}&isCityView={isCityView}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        decoded_data = data.decode("utf-8")

        return {
            'statusCode': 200,
            'body': json.dumps({'response': decoded_data})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
