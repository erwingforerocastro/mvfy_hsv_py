
def distribute_object(object_left: dict, object_right: dict) -> dict:
    """Insert object_right inside object_left
    
    Expected: same keys in both dicts
    
    Args:
        object_left (dict): object to be inserted
        object_right (dict): object to insert

    Raises:
        ValueError: [description]

    Returns:
        dict: objects merged
    """
    temp_object = {}

    if get_diff_list(object_left.keys(), object_right.keys()) is not None or get_diff_list(object_left.keys(), object_right.keys()) != []:
        raise ValueError("Invalid keys between objects")

    for key, item in object_right.items():
        temp_object[key] = object_left[key] if item is None else item

    return temp_object

def get_diff_list(lists: 'tuple(list)',   _type: 'str' = 'all') -> list:
    """Get difference between two list

    Args:
        lists (tuple): two list to be compared
        _type (str, optional): _type of get diff:

        all - get all list values different
        left - get only left different values
        right - get only right different values
        
        Defaults to 'all'.

    Raises:
        ValueError: Invalid size of lists, expected: __len__ 2
        ValueError: Invalid _type of lists

    Returns:
        list: difference
    """
    if len(lists) != 2:
        raise ValueError("Invalid size of lists, expected: __len__ 2")

    if not is_iterable(lists[0]) or not is_iterable(lists[1]):
        raise ValueError("Invalid _type of lists")

    diff = list(set(lists[0]) ^ set(lists[1]))

    if _type == "left":
        diff = [column for column in diff if column in lists[0]]
    
    elif _type == "right":
        diff = [column for column in diff if column in lists[1]]

    elif _type == "left":
        pass
    
    return diff

def is_iterable(posibleList):
    """Validate if element is iterable

    Args:
        posibleList (Any): posible iterable element

    Returns:
        bool: if element is iterable
    """
    try:
        if isinstance(posibleList, (tuple, list)) or hasattr(posibleList, "__iter__"):
            _ = posibleList[0]
            return True

        return False
    except Exception as e:
        return False