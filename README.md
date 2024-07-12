# FastAPI Lifespan Dependencies

Allows for the creation of _lifespan dependencies_ -
[FastAPI dependencies] that are only run once per app, instead of once per path.

This library is inspired by [`fastapi-lifespan-manager`]
and by [this suggestion][lifespan dependencies suggestion] on the FastAPI GitHub page.


## Usage

To get started with lifespan dependencies, create a `Lifespan` object and pass
it to the `FastAPI` constructor:

```python
from fastapi import FastAPI
from fastapi_lifespan_dependencies import Lifespan

lifespan = Lifespan()

app = FastAPI(lifespan=lifespan)
```

Any function that `yield`s a value can be turned into a lifespan dependency
by using the `Lifespan.register` decorator method
(both `def` and `async def` functions are supported):

```python
from redis.asyncio import redis

@lifespan.register
async def get_db():
    db = Redis(host="localhost", port=6379)

    yield db

    await db.aclose()
```

That's it!

You can now use `fastapi.Depends` to access the value `yield`ed by the lifespan dependency:

```python
from typing import Annotated
from fastapi import Depends

@app.get("/example")
async def get_example(db: Annotated[Redis, Depends(get_db)]):
    return await db.get('example')


@app.delete("/example")
async def delete_example(db: Annotated[Redis, Depends(get_db)]):
    return await db.delete('example')
```


## Usage with Other Dependencies

Similarly to normal FastAPI dependencies, lifespan dependencies can depend on each other:

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    redis_host: str
    redis_port: int


@lifespan.register
def get_config():
    yield Config()


@lifespan.register
async def get_db(config: Annotated[Config, Depends(get_config)]):
    db = Redis(host=config.redis_host, port=config.redis_port)

    yield db

    await db.aclose()
```

Lifespan dependencies can also depend on normal dependencies,
as long as none of them require path-related dependencies
(like `Query()` or `Body()`).


## When Are Lifespan Dependencies Run?

Every function decorated with `Lifespan.register` will be run when the application
starts, up until a `yield` statement is encountered.
Everything past the `yield` will only be executed right before the application shuts down.

This means that, unlike normal FastAPI dependencies, using the same dependency
in multiple path functions won't run the dependency multiple times, and every
function will share the same instance of the dependency.


## Examples

More examples can be found [here](./examples/).


[FastAPI Dependencies]: https://fastapi.tiangolo.com/tutorial/dependencies/
[`fastapi-lifespan-manager`]: https://pypi.org/project/fastapi-lifespan-manager/
[lifespan dependencies suggestion]: https://github.com/tiangolo/fastapi/issues/617#issuecomment-1458443561
[FastAPI Lifespan]: https://fastapi.tiangolo.com/advanced/events/?h=even#lifespan
