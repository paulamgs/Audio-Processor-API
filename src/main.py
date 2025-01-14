from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database_connection import create_db
from app.routers import audio


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database")
    await create_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(audio.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the IoT Audio Processing API"}
