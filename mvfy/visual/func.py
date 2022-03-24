import asyncio
from asyncio import Queue
from use_cases.visual_knowledge_cases import UserUseCases


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
        queue.put({
            f"{k}":v for k, v in obj.items() if k in keys
        })
    
    queue.task_done()

async def async_queue_object_get(queue: 'Queue', callback: 'function', args: tuple = ()) -> None:
    while not queue.empty():
        res = await queue.get()
        await callback(*args, queue_element=res)
        queue.task_done()
    
@loop_manager
async def load_user_descriptors(system_id: str, db: str, loop: 'asyncio.AbstractEventLoop') -> list[dict]:
    """Load user descriptors from database.

    Args:
        system_id (str): id of parent system
        db (str): data-base of users
        loop (asyncio.AbstractEventLoop): actual event loop

    Returns:
        list[dict]: [description]
    """
    users_queue = Queue()
    use_cases = UserUseCases(db)

    results = await loop.run_until_complete(use_cases.get_users({
        "system_id": system_id
    }))

    if results == []:
        return result
    await async_queue_object(results, ["detection"], users_queue)

    return users_queue