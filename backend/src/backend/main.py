from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import (
    agent,
    equipment,
    events,
    incidents,
    people,
    plans,
    reservations,
    rooms,
    vendors,
)
from backend.routers.operational_observations import router as operational_observations_router

app = FastAPI(
    title="NexCord API",
    description="Backend API for the NexCord operations intelligence platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    operational_observations_router,
    prefix="/api/v1",
)

app.include_router(
    events.router,
    prefix="/api/v1",
)

app.include_router(
    rooms.router,
    prefix="/api/v1",
)

app.include_router(
    incidents.router,
    prefix="/api/v1",
)

app.include_router(
    reservations.router,
    prefix="/api/v1",
)

app.include_router(
    equipment.router,
    prefix="/api/v1",
)

app.include_router(
    people.router,
    prefix="/api/v1",
)

app.include_router(
    vendors.router,
    prefix="/api/v1",
)

app.include_router(
    plans.router,
    prefix="/api/v1",
)

app.include_router(
    agent.router,
    prefix="/api/v1",
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "nexcord-api",
    }