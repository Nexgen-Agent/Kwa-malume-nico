from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, orders, admin, reviews
from app.database.database import engine, Base
import os

# Create tables on startup (if not using Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Malume Nico API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(reviews.router)

# Mount static files for images
if not os.path.exists("assets/images/reviews"):
    os.makedirs("assets/images/reviews", exist_ok=True)
app.mount("/assets/images/reviews", StaticFiles(directory="assets/images/reviews"), name="reviews")

@app.get("/")
def read_root():
    return {"message": "Welcome to Malume Nico Backend API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
