

def get_new_data_format(data: dict, callback_to_ask_for_verbindung) -> dict:
    """ Ask for the connection type and return the new data format """
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

    
def load_connected_to_into_objects(data: dict) -> dict:
    """ Add a Connection type list to the objects """
    objects = data['objects']
    connections = data['connections']
    for (a,b) in connections:
        objects[a].setdefault('connections', [])
        objects[b].setdefault('connections', [])
        objects[a]['connections'].append({'to': b, 'type': None if objects[a]['type'] != 'Einspannung' else 'fest'})
        objects[b]['connections'].append({'to': a, 'type': None if objects[b]['type'] != 'Einspannung' else 'fest'})
    return objects

    