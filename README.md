# dzencode-ws-be

dZENCode test task

# Docker actions

1. Build
    ```shell
    docker compose build
    ```
2. Run
    ```shell
    docker compose up -d
    docker ps
    ```
3. Stop
    ```shell
    docker compose stop
    ```
4. Down
    ```shell
    docker compose down
    ```

#### By default u don't have any admin user

##### Create admin user

```shell
docker compose run --rm --entrypoint "python manage.py createsuperuser" web
```

# Generate jwt for access

```python
from datetime import datetime

import jwt

print('Bearer %s' % jwt.encode({'iss': 'client', 'iat': datetime.now().timestamp()}, '12345', algorithm='HS256'))
```

### WS endpoint 
ws://localhost:8000/ws/comments/

#### Create new comment
```
{
    "type": "comment.create",
    "data": {
        "user_name": <str> - required
        "text": <str> - required
        "email": <email> - optional
        "home_page": <url> - optional
        "parent": <int> - optional, if provided will create child comment for this parent comment
    }
}
```
#### Get child list
```
{
    "type": "comment.child.list",
    "data": {
        "parent": <int> - required
        "page": <int> - optinal, default 1
    }
}
```

# Test coverage

1. Install poetry if not have already
    ```shell
    pip install poetry
    ```
2. Activate virtual env
    ```shell
    poetry install
    poetry shell
    ```
3. Set env var
    ```shell
    touch .env 
    echo TEST=1 >> .env
    ```
4. Run test
    ```shell
    make test
    ```
5. After u can find report file [HERE](htmlcov/index.html) and open it in your browser
