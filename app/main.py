from fastapi import FastAPI
from app.core.database import engine, Base
from app.core.config import AppSettings
from app.routes import root_route
from app.routes import auth_route
from app.routes import user_route

# Load app settings
app_settings = AppSettings()

# Initialize FastAPI
app = FastAPI(title=app_settings.app_name)

# Include routers
app.include_router(root_route.router)
app.include_router(auth_route.router)
app.include_router(user_route.router)

# Create tables
Base.metadata.create_all(bind=engine)
