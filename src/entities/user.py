from datetime import datetime

class User:
    def __init__(self, 
    id,
    systemId,
    author,
    detection,
    initDate,
    lastDate,
    properties = {},
    knowledge = False,
    frequency = 1,
    createdOn = datetime.now(),
    modifiedOn = datetime.now(),
    ) -> None:

        self.detection = detection
        self.properties = properties
        self.initDate = initDate
        self.lastDate = lastDate
        self.knowledge = knowledge
        self.frequency = frequency
        self.author = author
        self.createdOn = createdOn
        self.modifiedOn = modifiedOn
        self.systemId = systemId
        self.id = id
        
    def get_obj(self) -> None:
        return {

        }

    def __validate_values