
class StreamTemplateNotFound(Exception):
    def __init__(self, 
    path_file: str,
    message: str = "Html Stream template not found" 
    ) -> None:
        self.path_file = path_file
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.message} -> {self.path_file}"