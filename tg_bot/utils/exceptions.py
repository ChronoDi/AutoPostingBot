class PostExist(Exception):
    pass


class PostNotFound(Exception):
    pass


class FileNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PostInMailing(Exception):
    pass
