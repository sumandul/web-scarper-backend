from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from app.routers.user import router as user_router
from app.routers.scraper import router as scraper_router
from app.routers.chat import router as chat_router

from dotenv import load_dotenv
from app.core.database import Base, engine
# from app.models.user import Base
from app.models.scraper import Base
from app.models.chat_history  import Base
from starlette.middleware.sessions import SessionMiddleware
import os

load_dotenv()


Base.metadata.create_all(bind=engine)   
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code here
    print("Starting up...")
    yield
    # shutdown code here
    print("Shutting down...")
def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

 

app = FastAPI(
    title="FastAPI Application",
    description="A FastAPI application",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(SessionMiddleware, secret_key="tes-api")
app.include_router(user_router, tags=["GoogleAuth", "test", "login"])
app.include_router(scraper_router, prefix="/scrape", tags=["scraper"])
app.include_router(chat_router, prefix="/chat")

if __name__ == "__main__":
    import uvicorn
    create_tables()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
