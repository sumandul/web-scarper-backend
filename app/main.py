from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.routers.user import router as auth_router
from app.routers.scraper import router as scraper_router
from app.routers.chat import router as chat_router
from app.core.database import Base, engine
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key="tes-api")

app.include_router(auth_router, tags=["GoogleAuth"])
app.include_router(scraper_router, prefix="/scrape", tags=["scraper"])
app.include_router(chat_router, prefix="/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
