"""API v1 routers."""

from fastapi import APIRouter

from app.api.v1 import players

router = APIRouter()

router.include_router(players.router)

__all__ = ["router"]
