from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from routers import rooms, bookings, restaurant, admin

load_dotenv()

app = FastAPI(
    title="Yulimo API",
    description="API для бази відпочинку Юлімо",
    version="1.0.0"
)

# CORS
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутери
app.include_router(rooms.router,      prefix="/api/rooms",      tags=["Номери"])
app.include_router(bookings.router,   prefix="/api/bookings",   tags=["Бронювання"])
app.include_router(restaurant.router, prefix="/api/restaurant", tags=["Ресторан"])
app.include_router(admin.router,      prefix="/api/admin",      tags=["Адмін"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "project": "Yulimo"}
