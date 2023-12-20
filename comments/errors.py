import enum


class ErrorMessages(str, enum.Enum):
    INVALID_MESSAGE_TYPE: str = "Invalid message type"
