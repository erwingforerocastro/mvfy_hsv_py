class FailedConnectionWithRSTP(Exception):
    """
    Exception raised when a connection to a remote device is failed.
    """
    pass
    def __init__(self, url_connection: str, *args: object) -> None:
        super().__init__(*args)
        self.url_connection = url_connection

    def __str__(self) -> str:
        return f"System can't connect with - {self.url_connection} -> {self.message}" 