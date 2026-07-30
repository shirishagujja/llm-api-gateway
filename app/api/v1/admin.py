from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.permissions import require_admin
from app.models.user import User
from app.schemas.admin import (
    AllowedModelResponse,
    ProviderPermissionResponse,
    SetAllowedModelsRequest,
    SetProviderPermissionRequest,
    TeamCreateRequest,
    TeamResponse,
)
from app.services.team_admin_service import TeamAdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/teams", response_model=list[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[TeamResponse]:
    teams = TeamAdminService(db).list_teams()
    return [TeamResponse.model_validate(team) for team in teams]


@router.post("/teams", response_model=TeamResponse, status_code=201)
def create_team(
    body: TeamCreateRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> TeamResponse:
    team = TeamAdminService(db).create_team(body)
    return TeamResponse.model_validate(team)


@router.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> TeamResponse:
    team = TeamAdminService(db).get_team(team_id)
    return TeamResponse.model_validate(team)


@router.get("/teams/{team_id}/providers")
def list_team_providers(
    team_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return TeamAdminService(db).list_provider_permissions(team_id)


@router.put("/teams/{team_id}/providers")
def set_team_provider(
    team_id: UUID,
    body: SetProviderPermissionRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return TeamAdminService(db).set_provider_permission(
        team_id,
        provider_id=body.provider_id,
        is_allowed=body.is_allowed,
    )


@router.get("/teams/{team_id}/models")
def list_team_models(
    team_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return TeamAdminService(db).list_allowed_models(team_id)


@router.put("/teams/{team_id}/models")
def set_team_models(
    team_id: UUID,
    body: SetAllowedModelsRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return TeamAdminService(db).set_allowed_models(team_id, body.model_ids)
