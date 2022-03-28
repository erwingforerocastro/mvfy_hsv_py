from typing import Any
from utils import index as utils
from entities.visual_knowledge_entities import System, User

class SystemUseCases:
    def __init__(self, db) -> None:
        self.db = db

    def add_system(self, system: 'System') -> 'None|dict':
        result = None
        if isinstance(system, (System)):
            result = self.db.insert_one(self.collection, system.get_obj())
        else:
            _obj = System(**system).get_obj()
            result = self.db.insert_one(_obj)
        
        return result
    
    def get_system(self, system: 'dict') -> 'None|dict':

        res_system = System(**system)

        if res_system.id is not None:
            result = self.db.find_by_id(res_system.id)
        else:
            result = self.db.find_by_hash(res_system.hash)
        return result
    
    def update_system(self, id: 'str', new_system: 'dict') -> 'None|dict':

        if id is None:
            raise ValueError("You must supply an id.")
        
        existing_system = self.db.find_by_id(id)
        if existing_system is None:
            return None
        
        updated_system = utils.distribute_object(existing_system, new_system)
        updated_system = System(**updated_system)

        return self.db.update_one(id, updated_system)
    
    def delete_system(self, filter: 'dict') -> 'None|dict':

        if filter["id"] is None:
            raise ValueError("You must supply an id.")
        
        return self.db.delete_one()

class UserUseCases:
    def __init__(self, db) -> None:
        self.db = db

    def add_user(self, user: 'User') -> 'None|dict':
        result = None
        if isinstance(user, (User)):
            result = self.db.insert_one(self.collection, user.get_obj())
        else:
            _obj = User(**user).get_obj()
            result = self.db.insert_one(_obj)
        
        return result
    
    def get_user(self, filter: 'dict') -> 'None|User':

        result = self.db.find_one(filter)
        res_user = User(**result)
        return res_user
    
    def get_users(self, filter: 'dict') -> 'None|list[User]':

        result = self.db.find_many(filter)
        if result is None:
            return []

        new_result = []
        for user in result:
            new_result.append(User(**user))

        return new_result

    def update_user(self, id: 'str', new_user: 'dict') -> 'None|Any':

        if id is None:
            raise ValueError("You must supply an id.")
        
        existing_user = self.db.find_by_id(id)
        if existing_user is None:
            return None
        
        updated_user = utils.distribute_object(existing_user, new_user)
        updated_user = User(**updated_user)

        return self.db.update_one(id, updated_user)
    
    def delete_user(self, filter: 'dict') -> 'None|Any':

        if filter["id"] is None:
            raise ValueError("You must supply an id.")
        
        return self.db.delete_one()