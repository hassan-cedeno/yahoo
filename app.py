import sys, os
import json
import xmltodict
import requests

def get_credentials(path=None):
    data = None
    if not path:
        if 'yahoo' in os.getcwd():
            path = os.path.join(os.getcwd(), 'settings.json')
        else:
            path = os.path.join(os.getcwd(), 'yahoo', 'settings.json')
    with open(path) as json_data_file:
        data = json.load(json_data_file)
    return data

def generate_catalog_req_dict(credentials, item_id):    
    item_id_list = None
    req_dict = None
    if item_id:
        if isinstance(item_id, list):
            item_id_list = []
        for id in item_id:
            item_id_list.append({'ID': id})
        else:
            item_id_list = {'ID': item_id}
        req_dict = {
            'ystorewsRequest': {
                'StoreID': credentials['StoreID'],
                'SecurityHeader': {
                    'PartnerStoreContractToken': credentials['Token']
                },
                'Verb': 'get',
                'Version': '1.0',
                'ResourceList': {
                    'CatalogQuery': {
                        'ItemQueryList': {
                            'AttributesType': 'all',
                            'ItemIDList': item_id_list
                        }
                    }
                }
            }
        }
    return req_dict

def execute_request(credentials, item_id = None):
    result = None
    url = None
    if 'StoreID' in credentials.keys():
        url = f'https://{credentials["StoreID"]}.catalog.store.yahooapis.com/V1/CatalogQuery'
    req_dict = generate_catalog_req_dict(credentials, item_id)
    if req_dict:
        headers = {'Content-Type': 'application/xml'}
        data = xmltodict.unparse(req_dict)
        response = requests.post(url, data=data, headers=headers)
        if response.ok:
            result = xmltodict.parse(response.text)
    
    return result

if __name__ == '__main__':
    credentials = get_credentials()
    result = None
    ids = ['kj2375-intel-core-i58400-coffee-lake-6core-28-ghz-lga115', 'jw4213-gigabyte-bluetooth-wifi-pcie-adapter', 
            'te5364-intel-bx80673i77820x-core-i7-xseries-cpu', 'ou6449-asus-rog-strix-geforce-gtx-1080ti-11gb-video-card']
    if 'credentials' in credentials.keys():
        result = execute_request(credentials['credentials'], item_id=ids)
    try:
        if result and result['ystorews:ystorewsResponse']['ResponseResourceList']['Catalog']['ItemList']['Item']:
            items = result['ystorews:ystorewsResponse']['ResponseResourceList']['Catalog']['ItemList']['Item']
            for item in items:
                try:
                    if item['Orderable'] == 'Yes':
                        print(item['ID'] + ' is orderable')
                    else:
                        print(item['ID'] + ' is not orderable')
                except:
                    print('error retrieving Orderable value from item')
    except:
        print('error retrieving resutls from xml')