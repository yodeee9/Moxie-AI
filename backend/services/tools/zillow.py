import json
import os
import http.client
import urllib.parse

from config import RAPIDAPI_KEY

def search_properties(search_conditions):
    try:
        query_params = {
            'location': search_conditions.get('location', None),
            'maxPrice': search_conditions.get('maxPrice', None),
            'bedsMax': search_conditions.get('bedsMax', None),
            'schools': search_conditions.get('schools', None),
            # 'isCityView': search_conditions.get('isCityView', None),
            # 'isWaterfront': search_conditions.get('isWaterfront', None),
            # 'isMountainView': search_conditions.get('isMountainView', None),
            # 'isWaterView': search_conditions.get('isWaterView', None),
            # 'isParkView': search_conditions.get('isParkView', None)
        }

        filtered_params = {key: value for key, value in query_params.items() if value}
        
        encoded_params = urllib.parse.urlencode(filtered_params)

        conn = http.client.HTTPSConnection("zillow-com1.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            # 'x-rapidapi-host': "zillow-com1.p.rapidapi.com"
        }
        
        query = f"/propertyExtendedSearch?{encoded_params}&status_type=ForRent&sort=Newest"
        print(f"Query: {query}")
        conn.request("GET", query, headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        decoded_data = json.loads(data.decode("utf-8"))
        print(f"Response: {decoded_data}")
        
        properties = []
        if 'props' in decoded_data:
            for item in decoded_data['props'][:10]:
                # properties.append({
                #     'id': item.get('zpid'),
                #     'address': item.get('address'),
                #     'price': item.get('price'),
                #     'area': item.get('livingArea'),
                #     'imgSrc': item.get('imgSrc'),
                #     'detailUrl': item.get('detailUrl')
                # })
                properties.append(item)
        
        return {
            'statusCode': 200,
            'body': json.dumps(properties)
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
