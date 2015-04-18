class DjangoIndexError(Exception):
    message = None

    def __init__(self, message):
        self.message = message
