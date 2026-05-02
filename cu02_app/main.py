from __future__ import annotations
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from cu02_app.api import monitoring
from cu02_app.runner.engine import start_scheduler, stop_scheduler
from shared_kernel.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar planificador de tareas al arrancar
    start_scheduler()
    yield
    # Detener planificador al cerrar
    stop_scheduler()

setup_logging(app_name="srv-cu02-monitoring")
app = FastAPI(title="CU-02 Proactive Monitoring Service", lifespan=lifespan)

app.include_router(monitoring.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "service": "CU-02"}
