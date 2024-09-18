def check_if_WL_meets(data1,data2):
    (kords1,rotation1)= data1
    (kords2,rotation2) = data2
    if kords1 == kords2:
        return True
    
def check_if_fest_per_scheibe(value):
    if len(value) == 1:
        if value[0]['type'] == 'F':
            return True
    print(f'val.{value}')
    P_indexes = [index for index, d in enumerate(value) if d['type'] == 'P']
    WL_indexes = [index for index, d in enumerate(value) if d['type'] == 'WL']

    #if len(P_indexes) == 1 
    print(P_indexes)
    print(WL_indexes)
    return False


def check(pole, objects):
    for key,scheiben_pol_value in pole.items():
        #pass
        check_if_fest_per_scheibe(scheiben_pol_value)

