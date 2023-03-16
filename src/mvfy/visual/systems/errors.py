
class SystemNotFoundError(Exception):
    def __init__(self, db: str, *args: object) -> None:
        super().__init__(*args)
        self.db = db

    def __str__(self) -> str:
        return f"System not found in DB or not it couldn't be saved - {self.db}"
    

 