from typing import Any
from .mongobd import MongoDB
from bson.objectid import ObjectId
from pymongo.results import UpdateResult, DeleteResult

class SystemDB(MongoDB):

    def __init__(self, properties: dict, db: str, collection: str = "systems") -> None:
        super().__init__(properties, db)
        self.collection = collection

    def find_by_id(self, id: str) -> 'dict':

        _id = ObjectId(id)
        found = self.find_one({
            "_id": _id
        })

        found["id"] = str(found.pop("_id"))

        return found 

    def find_by_hash(self, hash: 'str', **kargs) -> 'None|dict':

        return self.find_one({"hash": hash}, **kargs)

    def insert_one(self, value: 'dict', **kargs) -> 'dict':

        if "id" in value.keys():
            value["_id"] = ObjectId(value.pop("id"))

        inserted_id = super().insert_one(self.collection, value, **kargs)

        return super().find_one(self.collection, {"_id": str(inserted_id)})

    def update_one(self, id: 'str', update: 'dict', **kargs) -> 'dict':

        _id = ObjectId(id)
        updated = super().update_one(self.collection, {"_id": _id}, update, **kargs)

        updated["id"] = str(updated.pop("_id"))

        return updated

    def find_one(self, filter: 'Any', **kargs) -> 'None|dict':
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        found = super().find_one(self.collection, filter, **kargs)

        if found is None:
            return None

        found["id"] = str(found.pop("_id"))

        return found
    
    def delete_one(self, filter: 'Any', **kargs) -> 'None':
        
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        super().delete_one(self.collection, filter, **kargs)
        

class UserDB(MongoDB):

    def __init__(self, properties: dict, db: str, collection: str = "users") -> None:
        super().__init__(properties, db)
        self.collection = collection
         
    def find_by_id(self, id: str) -> 'dict':
        
        _id = ObjectId(id)
        found = self.find_one({
            "_id": _id
        })

        found["id"] = str(found.pop("_id"))

        return found

    def find_many(self, filter: 'Any', **kargs) -> 'list[dict]|None':

        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        founds = super().find(self.collection, filter, **kargs)

        if founds is None:
            return None

        for found in founds:
            found["id"] = str(found.pop("_id"))

        return founds

    def insert_one(self, value: 'dict', **kargs) -> 'dict|None':

        if "id" in value.values():
            value["_id"] = ObjectId(value.pop("id"))

        inserted_id = super().insert_one(self.collection, value, **kargs)

        return  super().find_one(self.collection, {"_id": str(inserted_id)})

    def update_one(self, id: 'str', update: 'dict', **kargs) -> 'dict|None':

        _id = ObjectId(id)

        updated = super().update_one(self.collection, {"_id": _id}, update, **kargs)
        updated["id"] = str(updated.pop("_id"))

        return updated

    def find_one(self, filter: 'Any', **kargs) -> 'UpdateResult':
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        found = super().find_one(self.collection, filter, **kargs)
        found["id"] = str(found.pop("_id"))

        return found

    def delete_one(self, filter: 'Any', **kargs) -> 'DeleteResult':
        
        if "id" in filter.values():
            filter["_id"] = ObjectId(filter.pop("id"))

        super().delete_one(self.collection, filter, **kargs)