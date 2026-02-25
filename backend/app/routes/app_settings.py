import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.settings.config import settings

router = APIRouter()

@router.get("/settings", tags=["settings"])
async def get_frontend_settings():
    """Get frontend configuration settings"""
    is_testing = os.getenv("TESTING", "").lower() == "true"
    
    return JSONResponse({
        "google_oauth": {
            "enabled": settings.app_config.google_oauth.enabled,
        },
        "auth": {
            "mode": getattr(settings.app_config, 'auth').mode if hasattr(settings.app_config, 'auth') else 'hybrid'
        },
        "oidc_providers": [
            {
                "name": p.name,
                "enabled": p.enabled
            } for p in getattr(settings.app_config, "oidc_providers", []) or []
        ],
        "features": {
            "allow_uninvited_signups": settings.app_config.features.allow_uninvited_signups,
            "allow_multiple_organizations": settings.app_config.features.allow_multiple_organizations,
            "verify_emails": settings.app_config.features.verify_emails,
        },
        "deployment": {
            "type": settings.app_config.deployment.type if hasattr(settings.app_config, 'deployment') else "development",
        },
        "base_url": settings.app_config.base_url,
        "intercom": {
            "enabled": settings.app_config.intercom.enabled and not is_testing,
        },
        "telemetry": {
            "enabled": settings.app_config.telemetry.enabled and not is_testing,
        },
        "smtp_enabled": settings.app_config.smtp_settings is not None,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
    })
