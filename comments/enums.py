import enum


class EventTypes(str, enum.Enum):
    COMMENT_CREATE: str = "comment.create"
    COMMENT_PARENT_LIST: str = "comment.parent.list"
    COMMENT_CHILD_LIST: str = "comment.child.list"

    COMMENT_CHILD_LIST_ERROR: str = "comment.child.list.error"
    ERROR: str = "error"
    COMMENT_ERROR: str = "comment.error"
