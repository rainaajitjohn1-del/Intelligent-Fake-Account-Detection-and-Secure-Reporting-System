from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import profile
from models.database import init_db

app = FastAPI(title="Fake Account Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"status": "Backend is running"}