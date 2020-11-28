class ServerClosedError(Exception):
    def __init__(self, message="Server Closed"):
        self.message = message
        super().__init__(self.message)
