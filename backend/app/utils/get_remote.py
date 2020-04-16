import json
import requests
from RptSer.Config.Parser import run_config
main_config = run_config()

def getIndicateDetail(code,name):
    items = json.loads(requests.get(main_config['remote_api']['indicate_info'], \
                                           params={'primary_code':code,'indicate_name': name}).json())
    class_info = json.loads(requests.get(main_config['remote_api']['indicate_class_info'], \
                                           params={'primary_code':items['primary_code'], 'indicate_class_name': items['indicate_class']}).json())
    
    if items['primary_code'] == 'DM':          
        items['explanation'] = class_info['explanation_test_results']
        items['trademark'] = class_info['trademark']
        items['drug_class'] = class_info['drug_class']
        items['prescription'] = class_info['prescription']
        items['Indication'] = class_info['Indication']
        items['related_knowledge'] = class_info['related_knowledge']

    return items