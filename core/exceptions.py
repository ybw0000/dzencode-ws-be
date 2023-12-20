class IATException(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class DecodeException(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class SecretNotFoundException(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class InvalidTokenName(Exception):
    def __init__(self, message=None, token_name=None):
        self.message = message
        self.token_name = token_name

    def __str__(self):
        return self.message.format(self.token_name)
