from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_api_key, get_current_user
from app.models.user import User

api_router = APIRouter()


@api_router.get("/me", tags=["auth"])
def me(
    user: User = Depends(get_current_user),
    api_key=Depends(get_current_api_key),
) -> dict[str, str | None]:
    team = api_key.team
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "team_id": str(team.id) if team else None,
        "team_slug": team.slug if team else None,
    }
