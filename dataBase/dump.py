import json

from asgiref.sync import sync_to_async

@sync_to_async
def dump_dict(dict_of_profiles):
    try:
        with open('static/load_data/dump.json', 'w') as file:
            json.dump(dict_of_profiles, file)
        return 1
    except:
        return 0
    
