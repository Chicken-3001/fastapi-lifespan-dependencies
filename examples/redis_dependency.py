from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi_lifespan_dependencies import Lifespan

from redis.asyncio import Redis


lifespan = Lifespan()


app = FastAPI(lifespan=lifespan)


@lifespan.register
async def get_db():
    db = Redis(host="localhost", port=6379)

    yield db

    await db.aclose()


@app.get("/example")
async def get_example(db: Annotated[Redis, Depends(get_db)]):
    return await db.get("example")


@app.delete("/example")
async def delete_example(db: Annotated[Redis, Depends(get_db)]):
    return await db.delete("example")
