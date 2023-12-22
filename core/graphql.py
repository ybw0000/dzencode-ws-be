from strawberry import Schema

from comments.mutation import Mutation
from comments.query import Query
from comments.subscription import Subscription

schema = Schema(query=Query, subscription=Subscription, mutation=Mutation)
