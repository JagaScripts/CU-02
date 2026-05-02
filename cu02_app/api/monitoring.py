from __future__ import annotations
from fastapi import APIRouter
from cu02_app.runner.engine import run_pending_checks

router = APIRouter()

@router.post("/trigger", tags=["ops"])
def manual_trigger():
    """
    Dispara manualmente un ciclo de monitoreo (para pruebas/debug).
    """
    run_pending_checks()
    return {"message": "Ciclo de monitoreo disparado manualmente"}

@router.get("/status", tags=["ops"])
def get_status():
    """
    Devuelve el estado del planificador.
    """
    from cu02_app.runner.engine import scheduler
    return {
        "is_running": scheduler.running,
        "jobs": [str(job) for job in scheduler.get_jobs()]
    }
