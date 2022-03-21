from typing import Any
from mongobd import MongoDB
from bson.objectid import ObjectId
from pymongo.results import UpdateResult, DeleteResult

class SystemDB(MongoDB):

    def __init__(self, properties: dict, db: str, collection: str = "systems") -> None:
        super().__init__(properties, db)
        self.collection = collection
         
    def find_by_id(self, id: str) -> 'dict':

        _id = ObjectId(id)
        found = self.find_one(self.collection,{
            "_id": _id
        })

        found["id"] = str(found.pop("_id"))

        return found
    
    def insert_one(self, value: 'dict', **kargs) -> 'ObjectId':

        if "id" in value.values():
            value["_id"] = ObjectId(value.pop("id"))

        return super().insert_one(self.collection, value, **kargs)

    def update_one(self, id: 'str', update: 'dict', **kargs) -> 'UpdateResult':

        _id = ObjectId(id)

        return super().update_one(self.collection, {"_id": _id}, update, **kargs)

    def find_one(self, filter: 'Any', **kargs) -> 'UpdateResult':
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        return super().find_one(self.collection, filter, **kargs)
    
    def delete_one(self, filter: 'Any', **kargs) -> 'DeleteResult':
        
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        return super().delete_one(self.collection, filter, **kargs)

class UserDB(MongoDB):

    def __init__(self, properties: dict, db: str, collection: str = "users") -> None:
        super().__init__(properties, db)
        self.collection = collection
         
    def find_by_id(self, id: str) -> 'dict':

        _id = ObjectId(id)
        found = self.find_one(self.collection,{
            "_id": _id
        })

        found["id"] = str(found.pop("_id"))

        return found

    def find_many(self, filter: 'Any', **kargs) -> 'list[Any]|None':
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        return super().find(self.collection, filter, **kargs)

    def insert_one(self, value: 'dict', **kargs) -> 'ObjectId':

        if "id" in value.values():
            value["_id"] = ObjectId(value.pop("id"))

        return super().insert_one(self.collection, value, **kargs)

    def update_one(self, id: 'str', update: 'dict', **kargs) -> 'UpdateResult':

        _id = ObjectId(id)

        return super().update_one(self.collection, {"_id": _id}, update, **kargs)

    def find_one(self, filter: 'Any', **kargs) -> 'UpdateResult':
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        return super().find_one(self.collection, filter, **kargs)
    
    def delete_one(self, filter: 'Any', **kargs) -> 'DeleteResult':
        
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        return super().delete_one(self.collection, filter, **kargs)