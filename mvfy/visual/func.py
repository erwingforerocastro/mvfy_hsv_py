import asyncio
from asyncio import Queue, Task
from datetime import datetime
import logging
from entities.visual_knowledge_entities import System
from data_access.visual_knowledge_db import SystemDB, UserDB
from mvfy.use_cases.visual_knowledge_cases import SystemUseCases
from use_cases.visual_knowledge_cases import UserUseCases
from ..utils import index as utils

async def loop_manager(func: function) -> 'function':
    """Decorator for Manage Event Loop.

    Args:
        func ([type]): callback async function
    
    Returns:
        (function): result of func
    """
    async def wrapper_function(*args, **kargs):
        loop = asyncio.get_event_loop()
        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return await func(*args, **kargs, loop=loop)
        
    return wrapper_function

async def async_queue_object_put(list: list[dict], keys: list[str], queue: 'Queue' = Queue()) -> None:
    """Generate Queue with object properties extracted

    Args:
        list (list[dict]): list of objects 
        keys (list[str]): list of pairs key:value, required
        queue (Queue, optional): [description]. Defaults to Queue().
    
    Example
        >>> ... await async_queue_object([..., {..., "system": 1}], ["system"])

    """
    for obj in list:
        await queue.put({
            f"{k}":v for k, v in obj.items() if k in keys
        })
    
    queue.task_done()

async def async_queue_object_get(queue: 'Queue', callback: 'function', args: tuple = ()) -> None:

    while not queue.empty():
        res = await queue.get()
        await callback(*args, queue_result=res)

    queue.task_done()

def get_actual_date(format: str) -> datetime:
    """Get the actual date from a given format.

    Args:
        format (str): valid format datetime

    Returns:
        datetime: formatted datetime
    """
    date = datetime.now()
    try:
        return datetime.strptime(date, format)
    except Exception as e:
        logging.error(f"get_actual_date - Error to format datetime {e}")
        return date

@loop_manager
async def load_user_descriptors(system_id: str, db: UserDB, loop: 'asyncio.AbstractEventLoop') -> 'utils.ThreadedGenerator|None':
    """Load user descriptors from database.

    Args:
        system_id (str): id of parent system
        db (str): data-base of users
        loop (asyncio.AbstractEventLoop): actual event loop

    Returns:
        list[dict]: [description]
    """

    use_cases = UserUseCases(db)

    results = await loop.run_until_complete(use_cases.get_users({
        "system_id": system_id
    }))

    if results == [] or results is None:
        return None

    users_queue = utils.ThreadedGenerator(results, daemon=True)
    users_queue.insert_action(cb=utils.extract_objects, args=(["detection"]))

    return users_queue

@loop_manager
async def get_system(system: 'dict', db: SystemDB, loop: 'asyncio.AbstractEventLoop') -> 'dict|None':
    """Get information about a system.

    Returns:
        dict: system found
    """
    use_cases = SystemUseCases(db)
    result = await loop.run_until_complete(use_cases.get_system(system))

    if result == [] or result is None:
        return None

    return result

@loop_manager
async def insert_system(system: 'dict', db: SystemDB, loop: 'asyncio.AbstractEventLoop') -> 'dict|None':
    """add information about a system.

    Returns:
        str: id of system insert
    """
    use_cases = SystemUseCases(db)
    result = await loop.run_until_complete(use_cases.add_system(system))

    if result == [] or result is None:
        return None

    return result

@loop_manager
async def insert_user(user: 'dict', db: UserDB, loop: 'asyncio.AbstractEventLoop') -> 'dict|None':
    """add information about a user.

    Returns:
        str: id of user insert
    """
    use_cases = UserUseCases(db)
    result = await loop.run_until_complete(use_cases.add_user(user))

    if result == [] or result is None:
        return None

    return result