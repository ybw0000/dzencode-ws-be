import strawberry


@strawberry.input
class CreateCommentInput:
    user_name: str
    text: str
    email: str | None = None
    home_page: str | None = None


@strawberry.input
class CreateChildCommentInput(CreateCommentInput):
    parent: int


@strawberry.type
class CreateCommentType:
    id: int
    user_name: str
    text: str
    email: str | None
    home_page: str | None
    parent: int | None
