def get_new_data_format(data: dict, callback_to_ask_for_verbindung) -> dict:
    objects = data['objects']
    connections = data['connections']

    if not (objects.keys()).__contains__('type'):
        new_connections = {}
        for (a,b) in connections:
            objects[a]['connections'] = []
            type = callback_to_ask_for_verbindung(a,b)
            objects[a]['connections'].append({'to': b, 'type': type})

            # Make new connections type
            new_connections[(a,b)] = {'length': None, 'EI': None, 'EA': None}    # Hier kann das dann geändert werden
    return {'objects': objects, 'connections': new_connections}

    

    