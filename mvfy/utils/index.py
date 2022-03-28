
import inspect
import logging
from queue import Queue
from threading import Thread
from typing import Iterable, Iterator


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

def extract_objects(object_list: list[dict], keys: list[str]) -> list[dict]:
    """Extracts keys from a list of objects.

    Args:
        object_list (list[dict]): list of objects
        keys (list[str]): keys that be extracted

    Returns:
        list[dict]: list of objects
    """
    res = []
    object_list = object_list if is_iterable(object_list) else [object_list]

    for obj in object_list:
        res.append({
            f"{k}":v for k, v in obj.items() if k in keys
        })

    return res
#------------------------------------------------------------------------------- CLASES ----------------------------------------------------------------------------------------

class ThreadedGenerator():
    """
    Generator that runs on a separate thread, returning values to calling
    thread. Care must be taken that the iterator does not mutate any shared
    variables referenced in the calling thread.
    """

    def __init__(self, 
        iterator: Iterator,
        daemon=False,
        Thread=Thread,
        sentinel: 'Any' = None,
        queue=Queue):

        self.size = len(iterator)
        self._iterator = iterator
        self._sentinel = sentinel
        self._queue = queue()
        self._thread = Thread(
            target=self._run
        )
        self._thread.daemon = daemon
        self._cb = None

    def insert_action(self, cb: 'function', args=()):
        """Add a callback to the intance.

        Args:
            cb (function): callback function
            args (tuple, optional): args. Defaults to ().

        """
        self._cb = ( lambda value: cb(value, *args) ) if args == () else ( lambda value: cb(value) )

    def __repr__(self):
        return 'ThreadedGenerator({!r})'.format(self._iterator)

    def _run(self):
        """Execute queue put process
        """
        for value in self._iterator:
            if self._cb is not None:
                try:
                    value = self._cb(value)
                except Exception as e:
                    logging.warning(f"{inspect.currentframe().f_code.co_name} Error inside function: \n {e}")

            self._queue.put(value)
        self._queue.task_done()

    def __iter__(self):
        """Iterate over the values in the queue .

        Yields:
            Any: value in the queue
        """
        self._thread.start()
        end = 0

        for value in iter(self._queue.get, self._sentinel):
            if value != self._sentinel:
                end += 1

            if end >= self.size:
                break

            yield value

        self._thread.join()

