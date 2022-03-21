from typing import Any
from pymongo import MongoClient
from pymongo.results import UpdateResult, BulkWriteResult, DeleteResult
from bson.objectid import ObjectId

class MongoDB:

    def __init__(self, properties: str, db: 'str') -> None:
        self.client = MongoClient(properties)
        self.url = self.client.address
        self.db = self.client[db]

    def insert_one(self, collection: str, value: 'Any', **kargs) -> 'ObjectId': 
        _collect = self.db[collection]

        _id = _collect.insert_one(value, **kargs).inserted_id
        return _id
    
    def insert_many(self, collection: str, value: 'Any', **kargs) -> 'list[ObjectId]': 
        _collect = self.db[collection]

        _ids = _collect.insert_many(value, **kargs).inserted_ids
        return _ids
    
    def replace_one(self, collection: str, registry_found: 'Any', registry_replace: 'Any', **kargs) -> 'UpdateResult': 
        _collect = self.db[collection]

        result = _collect.replace_one(registry_found, registry_replace, **kargs)
        return result
    
    def update_many(self, collection: str, filter: 'Any', update: 'Any', **kargs) -> 'list[UpdateResult]': 
        _collect = self.db[collection]

        result = _collect.update_many(filter, update, **kargs)
        return result
    
    def update_one(self, collection: str, filter: 'Any', update: 'Any', **kargs) -> 'UpdateResult': 
        _collect = self.db[collection]

        result = _collect.update_one(filter, update, **kargs)
        return result   
    
    def find(self, collection: str, filter: 'Any', **kargs) -> 'Any': 
        _collect = self.db[collection]

        result = _collect.find(filter, **kargs)
        return result

    def find_one(self, collection: str, filter: 'Any', **kargs) -> 'Any': 
        _collect = self.db[collection]

        result = _collect.find_one(filter, **kargs)
        return result
        
    def bulk_write(self, collection: str, requests: 'list[UpdateResult]', **kargs) -> 'BulkWriteResult':
        _collect = self.db[collection]

        result = _collect.bulk_write(requests, **kargs)
        return result

    def delete_one(self, collection: str, filter: 'Any', **kargs) -> 'DeleteResult': 
        _collect = self.db[collection]

        result = _collect.delete_one(filter, **kargs)
        return result
    
    def delete_many(self, collection: str, filter: 'Any', **kargs) -> 'list[DeleteResult]': 
        _collect = self.db[collection]

        result = _collect.delete_many(filter, **kargs)
        return result