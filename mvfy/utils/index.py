
import asyncio
from datetime import datetime
import inspect
import logging
from queue import Queue
from threading import Thread
import threading
from time import strptime
from typing import Any, Callable, Coroutine, Iterable, Iterator, Tuple

def get_actual_date(format: str) -> datetime:
    """Get the actual date from a given format.

    Args:
        format (str): valid format datetime

    Returns:
        datetime: formatted datetime
    """
    date = datetime.now()
    try:
        return datetime.strptime(date, format) if format is not None else date
    except Exception as e:
        logging.error(f"get_actual_date - Error to format datetime {e}")
        return date
        
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

def get_date_diff_so_far(date: datetime, _type: str = "days") -> float:
    """Returns the difference between two date objects.

    Args:
        date (datetime): date to be compared with today
        _type (str, optional): type of difference <"days" or "weeks" or "months">. Defaults to "days".

    Returns:
        float: difference between "date" and now
    """
    date_now = get_actual_date()
    if date is not None:
        res = None
        if _type == "days":
            res = abs((date_now - date).days) 
        elif _type == "weeks":
            res = abs((date_now - date).days) // 7
        elif _type == "months":
            res = abs((date_now.year - date.year) * 12 + date_now.month - date.month)

        return res
    
def frequency(total: float, percentage: float, value: float, invert: bool = False) -> float:
    """Return frequency of a given value .

    Freq = v*t/p

    v-> value
    t-> total
    p-> percentage

    Args:
        total (float): total value
        percentage (float): percentage value between 0 and 1
        value (float): value
        invert (bool, optional): change total by percentage in formula. Defaults to False.

    Returns:
        float: frequency result
    """
    return (value * total) / percentage if invert is True else (value * percentage) / total

def run_async_in_thread(coroutine: Coroutine) -> Thread:
    """Run a coroutine in a thread.
    Args:
        coroutine (Coroutine): coroutine to run"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    thread = threading.Thread(target = loop.run_until_complete, args = (coroutine, ))
    thread.start()

    return thread

#------------------------------------------------------------------------------- CLASES ----------------------------------------------------------------------------------------

class ThreadedGenerator():
    """
    Generator that runs on a separate thread, returning values to calling
    thread. Care must be taken that the iterator does not mutate any shared
    variables referenced in the calling thread.
    """

    def __init__(self, 
        iterator: Iterable,
        daemon = False,
        Thread = Thread,
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

    def insert_action(self, cb: 'Callable', args=()):
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
                except Exception as err:
                    logging.warning(f"{inspect.currentframe().f_code.co_name} Error inside function: \n {err}")

            self._queue.put(value)
            
        self._queue.put(self._sentinel)
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

