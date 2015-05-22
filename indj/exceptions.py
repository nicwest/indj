class IndjHumanReadableError(Exception):
    error_number = 1

    def get_message(self):
        return '{0}\n'.format(self.args[0])


class DjangoIndexError(IndjHumanReadableError):
    error_number = 3


class LookupHandlerError(IndjHumanReadableError):
    error_number = 4


class ExactMatchNotFound(IndjHumanReadableError):
    error_number = 5


class FuzzyMatchNotFound(IndjHumanReadableError):
    error_number = 6
