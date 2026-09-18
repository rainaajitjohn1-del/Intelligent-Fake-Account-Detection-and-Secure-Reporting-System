from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import profile, report
from models.database import init_db

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Fake Account Detection & Secure Reporting API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(report.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"status": "Backend is running"}