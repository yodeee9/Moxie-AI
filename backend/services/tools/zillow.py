import json
import os
import http.client
import urllib.parse

from config import RAPIDAPI_KEY

def search_properties(search_conditions):
    try:
        default_location = "San Mateo, CA"
        default_maxPrice = "1000000"
        default_bedsMax = "3"
        default_schools = "high"
        default_isCityView = "false"
        
        location = urllib.parse.quote(str(search_conditions.get('location', default_location)))
        maxPrice = urllib.parse.quote(str(search_conditions.get('maxPrice', default_maxPrice)))
        bedsMax = urllib.parse.quote(str(search_conditions.get('bedsMax', default_bedsMax)))
        schools = urllib.parse.quote(str(search_conditions.get('schools', default_schools)))
        isCityView = urllib.parse.quote(str(search_conditions.get('isCityView', default_isCityView)))

        
        conn = http.client.HTTPSConnection("zillow-com1.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "zillow-com1.p.rapidapi.com"
        }
        
        query = f"/propertyExtendedSearch?location={location}&maxPrice={maxPrice}&bedsMax={bedsMax}&schools={schools}&isCityView={isCityView}"
        print(f"Query: {query}")
        conn.request("GET", query, headers=headers)
        
        res = conn.getresponse()
        print(f"Response: {res}")
        data = res.read()
        decoded_data = json.loads(data.decode("utf-8"))
        
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
