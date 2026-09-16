class SantoFindsError(Exception):
    pass


class AuthenticationError(SantoFindsError):
    pass


class LookupRunError(SantoFindsError):
    pass


class LookupTimeoutError(SantoFindsError):
    pass
