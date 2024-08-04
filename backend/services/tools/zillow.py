import json
import os
import http.client
import urllib.parse

def lambda_handler(event, context):
    debug_info = {}

    try:
        # パラメータが存在しない場合のデフォルト値
        default_location = "San Mateo, CA"
        default_maxPrice = "1000000"
        default_bedsMax = "3"
        default_schools = "high"
        default_isCityView = "false"
        
        # イベントからパラメータを取得し、存在しない場合はデフォルト値を使用
        location = urllib.parse.quote(event.get('location', default_location))
        maxPrice = urllib.parse.quote(event.get('maxPrice', default_maxPrice))
        bedsMax = urllib.parse.quote(event.get('bedsMax', default_bedsMax))
        schools = urllib.parse.quote(event.get('schools', default_schools))
        isCityView = urllib.parse.quote(event.get('isCityView', default_isCityView))
        
        debug_info['params'] = {
            'location': location,
            'maxPrice': maxPrice,
            'bedsMax': bedsMax,
            'schools': schools,
            'isCityView': isCityView
        }

        conn = http.client.HTTPSConnection("zillow-com1.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': os.environ['RAPIDAPI_KEY'],  # 環境変数からAPIキーを取得
            'x-rapidapi-host': "zillow-com1.p.rapidapi.com"
        }

        query = f"/propertyExtendedSearch?location={location}&maxPrice={maxPrice}&bedsMax={bedsMax}&schools={schools}&isCityView={isCityView}"
        conn.request("GET", query, headers=headers)

        res = conn.getresponse()
        data = res.read()
        decoded_data = json.loads(data.decode("utf-8"))

        # 必要なデータのみを抽出
        properties = []
        if 'props' in decoded_data:
            for item in decoded_data['props'][:3]:
                properties.append({
                    'id': item.get('zpid'),
                    'address': item.get('address'),
                    'price': item.get('price'),
                    'area': item.get('livingArea'),
                    'imgSrc': item.get('imgSrc'),
                    'detailUrl': item.get('detailUrl')
                })
        print(properties)

        session_attributes = event["sessionAttributes"]
        prompt_session_attributes = event["promptSessionAttributes"]
        
        response_body = {
            'application/json': {
                'body': json.dumps(properties)
            }
        }

        action_response = {
            'httpStatusCode': 200,
            'responseBody': response_body
        }
    
        session_attributes = event['sessionAttributes']
        prompt_session_attributes = event['promptSessionAttributes']
    
        api_response = {
            'messageVersion': '1.0', 
            'response': action_response,
            'sessionAttributes': session_attributes,
            'promptSessionAttributes': prompt_session_attributes
        }
        return api_response
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }