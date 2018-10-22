import sys, os
import json
import xmltodict
import requests
from enum import Enum

'''
All – Fetches all attributes

Mandatory- Fetches all
    mandatory attributes

Store- Fetches all store
    attributes

Shopping – Fetches all the
    shopping attributes

Custom- Fetches all the
    custom attributes
    Attributes for each category
    can be found in Catalog
    Manager > Manage Tables.
'''

class AttributesType(Enum):
    ALL = 'all'
    MANDATORY = 'mandatory'
    STORE = 'store'
    SHOPPING = 'shopping'
    CUSTOM = 'custom'

if 'yahoo' in os.getcwd():
    path = os.path.join(os.getcwd())
else:
    path = os.path.join(os.getcwd(), 'yahoo')
with open(os.path.join(path, 'settings.json')) as json_data_file:
    credentials = json.load(json_data_file)

def generate_request_header(credentials):
    '''
    Args
    ---------
    credentials: Object
        Store Credentials
    '''
    req_dict = {
        'ystorewsRequest': {
            'StoreID': credentials['StoreID'],
            'SecurityHeader': {
                'PartnerStoreContractToken': credentials['Token']
            },
            'Verb': 'get',
            'Version': '1.0'
        }
    }
    return req_dict

def generate_get_items_dict(credentials, item_id):    
    '''
    Args
    ---------
    credentials: Object
        Store Credentials
    item_id: list
        List of products ids to retrieve
    '''
    item_id_list = None
    req_dict = None
    if item_id:
        if isinstance(item_id, list):
            item_id_list = []
            for id in item_id:
                item_id_list.append({'ID': id})
        req_dict = generate_request_header(credentials)
        if 'ResourceList' not in req_dict['ystorewsRequest'].keys():
            req_dict['ystorewsRequest']['ResourceList'] = {
                'CatalogQuery': {
                    'ItemQueryList': {
                        'AttributesType': AttributesType.ALL.value,
                        'ItemIDList': item_id_list
                    }
                }
            }
    return req_dict

def generate_search_items_dict(credentials, keywords, start=None, end=None):    
    '''
    Args
    ---------
    credentials: Object
        Store Credentials
    keywords: string
         The id, name, or code of the item to be searched for
    start: Int
        Used to set a start value when requesting to see a range of matching records. For example,
        Used to set a start value when requesting to see a range of matching records. For example,
        if your search has 5000 matching records and you wish to see records 1001 to 2000, use
        1001 for the <StartIndex> value. A maximum of 1000 matching records may be seen at one time
    end: Int
        Used to set a start value when requesting to see a range of matching records. For example,
        if your search has 5000 matching records and you wish to see records 10001 to 2000,
        this value would be 2000. A maximum of 1000 matching records may be seen at one time
    '''
    if not start:
        start = 1
    if not end:
        end = start + 999
    req_dict = None
    req_dict = generate_request_header(credentials)
    if 'ResourceList' not in req_dict['ystorewsRequest'].keys():
        req_dict['ystorewsRequest']['ResourceList'] = {
            'CatalogQuery': {
                'SimpleSearch': {
                    'StartIndex': start,
                    'EndIndex': end,
                    'Keyword': keywords
                }
            }
        }
    return req_dict

def execute_get_items_request(credentials, item_id = None):
    result = None
    url = None
    if 'StoreID' in credentials.keys():
        url = f'https://{credentials["StoreID"]}.catalog.store.yahooapis.com/V1/CatalogQuery'
    req_dict = generate_get_items_dict(credentials, item_id)
    if req_dict:
        headers = {'Content-Type': 'application/xml'}
        data = xmltodict.unparse(req_dict)
        response = requests.post(url, data=data, headers=headers)
        if response.ok:
            result = xmltodict.parse(response.text)
    return result

def execute_search_items_request(credentials, keywords, start=None, end=None):
    result = None
    url = None
    if 'StoreID' in credentials.keys():
        url = f'https://{credentials["StoreID"]}.catalog.store.yahooapis.com/V1/CatalogQuery'
    req_dict = generate_search_items_dict(credentials, keywords, start, end)
    if req_dict:
        headers = {'Content-Type': 'application/xml'}
        data = xmltodict.unparse(req_dict)
        response = requests.post(url, data=data, headers=headers)
        if response.ok:
            result = xmltodict.parse(response.text)
    return result

def load_data():
    with open(os.path.join(path, 'data.json')) as json_data_file:
        data = json.load(json_data_file)
    return data

def main():
    if 'credentials' in credentials.keys():
        data = load_data()
        result = None
        if False: # get items
            ids = data["GET"]
            result = execute_get_items_request(credentials['credentials'], item_id=ids)
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
        elif True: # search 
            result = execute_search_items_request(credentials['credentials'],keywords= data['SEARCH']['keyword'], start=data['SEARCH']['start'], end=data['SEARCH']['end'])
            try:
                if result and 'ID' in result['ystorews:ystorewsResponse']['ResponseResourceList']['Catalog']['ItemIDList'].keys():
                    print(f"items matching keywords ({data['SEARCH']['keyword']}):")
                    for id in result['ystorews:ystorewsResponse']['ResponseResourceList']['Catalog']['ItemIDList']['ID']:
                        print('\t', id)
            except:
                print('error retrieving resutls from xml')

if __name__ == '__main__':
    main()
    