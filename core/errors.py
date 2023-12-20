import enum


class ErrorMessages(str, enum.Enum):
    IAT_IN_FUTURE = '"iat" value cannot be in future.'
    TOKEN_EXPIRED = "Token expired."
    ERROR_DECODING = "Error decoding signature."
    SECRET_NOT_FOUND = "Secret key not found."
    INVALID_TOKEN_NAME = "Invalid token name %. Expected Bearer."
    TOKEN_NOT_PROVIDED = "Token not provided."
