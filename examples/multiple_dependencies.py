from typing import Annotated
from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings
from fastapi_lifespan_dependencies import Lifespan

from redis.asyncio import Redis


lifespan = Lifespan()

app = FastAPI(lifespan=lifespan)


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


@app.get("/example")
async def example(db: Annotated[Redis, Depends(get_db)]):
    return await db.get("example")
