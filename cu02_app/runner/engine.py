from __future__ import annotations
import httpx
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from shared_kernel.settings import settings
from shared_kernel.logging import get_logger

logger = get_logger("monitoring.runner")
scheduler = BackgroundScheduler()

def run_pending_checks():
    """
    Tarea periódica que busca reglas activas y ejecuta sus comprobaciones.
    """
    logger.info("Iniciando ciclo de monitoreo proactivo")
    
    try:
        # 1. Obtener todas las reglas activas de CU-01
        # En un entorno real, esto podría ser una consulta a la DB compartida 
        # o una llamada API. Aquí simulamos la llamada API por desacoplamiento.
        with httpx.Client() as client:
            # Nota: user_id=system_admin o similar para obtener globales si aplica
            # Por simplicidad, simulamos la obtención de una lista.
            resp = client.get(f"{settings.cu01_service_url}/api/v1/rules", params={"is_enabled": True, "user_id": "global"})
            if not resp.is_success:
                logger.error(f"Error consultando reglas en CU-01: {resp.status_code}")
                return
            
            rules = resp.json().get("items", [])
            
        for rule in rules:
            execute_rule(rule)
            
    except Exception as e:
        logger.exception(f"Fallo crítico en el ciclo de monitoreo: {e}")

def execute_rule(rule: dict):
    """
    Ejecuta la lógica de una regla específica.
    """
    rule_id = rule.get("id")
    rule_type = rule.get("rule_type")
    scope = rule.get("scope", {})
    domains = scope.get("domains", [])
    
    logger.info(f"Ejecutando regla {rule_id} ({rule_type}) para {len(domains)} dominios")
    
    for domain_name in domains:
        # Llamar a CU-03 para analizar reputación
        with httpx.Client() as client:
            resp = client.post(
                f"{settings.cu03_service_url}/api/v1/analyze", 
                json={"domain": domain_name}
            )
            
            if resp.is_success:
                analysis = resp.json()
                # Lógica de disparo de alerta (ejemplo simple)
                if analysis.get("risk_score", 0) > 70:
                    trigger_alert(rule, domain_name, analysis)
            else:
                logger.warning(f"No se pudo analizar dominio {domain_name}: {resp.status_code}")

def trigger_alert(rule: dict, domain: str, analysis: dict):
    """
    Simula el envío de una alerta (Email/Slack).
    """
    logger.warning(f"¡ALERTA DISPARADA! Regla: {rule['name']} | Dominio: {domain} | Riesgo: {analysis['risk_score']}")
    # Aquí iría la integración real con SendGrid, Slack Webhook, etc.

def start_scheduler():
    if not scheduler.running:
        # Ejecutar cada 5 minutos (ajustable)
        scheduler.add_job(run_pending_checks, 'interval', minutes=5, id="monitoring_job")
        scheduler.start()
        logger.info("Planificador de monitoreo iniciado")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Planificador de monitoreo detenido")
