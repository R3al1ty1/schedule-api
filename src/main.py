import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from contextlib import asynccontextmanager

from core.settings import settings
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Приложение запускается...")
    yield
    print("🛑 Приложение выключается...")


app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    title="""Расписание Таврида""",
    version="1.0.0"
)

# origins = [
#     "http://localhost:3000",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    api_router,
    prefix="/api"
)


if __name__=="__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True
    )
