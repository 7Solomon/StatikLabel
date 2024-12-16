from src.statik.analyse_functions import check_if_WL_colide,check_if_WL_and_point_meet

def check_if_fest_per_scheibe(pole_ordered_per_scheibe, pole_data, node_data):
    for pol_pair in pole_ordered_per_scheibe:
        if pol_pair[1] == 0:   ## Hauptpol
            test_1 = [_['node'] for _ in pole_data[pol_pair] if _['type'] == 'WL']
            test_2 = [_['node'] for _ in pole_data[pol_pair] if  _['type'] == 'P']
            #test_3 = [_['node'] for _ in pole_data[pol_pair] if _['type'] == 'FWL']
            test_4 = [_['node'] for _ in pole_data[pol_pair] if _['type'] == 'F']


            if len(test_1) >= 3:                                  # 3 Loslager
                if not check_if_WL_colide(test_1, node_data):
                    return True
            elif len(test_2) >= 2:                                # 2 Festlager
                return True
            #if len(test_3) >= 1:      ### FWL IST WEIRD
            #    pass     
            elif len(test_4) >= 1:                               # 1 Einspannung
                return True
            elif len(test_1) >= 1 and len(test_2) == 1:   
                if check_if_WL_and_point_meet(test_1, test_2, node_data):
                    return False
                return True
        else:
            return False

def analyze_polplan(pol_data, node_data):
    """
    Analyzes a polplan system for mismatches and extracts all Weglinien (WLs).
    
    Args:
        pol_data: Dictionary with pol pairs as keys and lists of their properties as values
        node_data: Dictionary with node information including coordinates and types
    
    Returns:
        tuple: (mismatches, weglinien, status)
            - mismatches: List of identified mismatches
            - weglinien: List of all WLs in the system
            - status: Boolean indicating if system is valid (True) or has mismatches (False)
    """
    status_of_scheiben = {}
    mismatches = []
    weglinien = []
    connecting_pols = []

    pols_of_same_scheibe = {}
    for pol_pair, pol_properties in pol_data.items():
        pol_1_in_data = pol_pair[0] in pols_of_same_scheibe
        pol_2_in_data = pol_pair[1] in pols_of_same_scheibe
        if not pol_1_in_data:
            pols_of_same_scheibe[pol_pair[0]] = []
            pols_of_same_scheibe[pol_pair[0]].append(pol_pair)
        else:
            pols_of_same_scheibe[pol_pair[0]].append(pol_pair)

        if pol_pair[1] != 0:    # Nur für keine Hauptpole
            if not pol_2_in_data:
                pols_of_same_scheibe[pol_pair[1]] = []
                pols_of_same_scheibe[pol_pair[0]].append(pol_pair)
            else:  
                pols_of_same_scheibe[pol_pair[1]].append(pol_pair)

    
    for scheibe, pole in pols_of_same_scheibe.items():
        result = check_if_fest_per_scheibe(pole, pol_data, node_data)
        status_of_scheiben[scheibe] = result


    return status_of_scheiben
        
        

    #return mismatches, weglinien, connecting_pols, len(mismatches) == 0