class DjangoIndexError(Exception):
    pass


class LookupHandlerError(Exception):
    pass


class ExactMatchNotFound(Exception):
    pass


class FuzzyMatchNotFound(Exception):
    pass
