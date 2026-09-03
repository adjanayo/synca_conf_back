from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.multipart import parse_multipart_form
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.hackathon import HackathonTeam, HackathonTeamMember
from app.schemas.hackathon import (
    HackathonTeamCreate,
    HackathonTeamMemberCreate,
    HackathonTeamMemberRead,
    HackathonTeamMemberUpdate,
    HackathonTeamRead,
    HackathonTeamUpdate,
)
from app.services.storage import MAX_PHOTO_BYTES, UploadRejectedError, upload_file

admin_hackathon_teams_router = APIRouter(
    prefix="/api/admin/hackathon/teams", tags=["admin-hackathon"]
)


async def _get_team_or_404(db: AsyncSession, team_id: int) -> HackathonTeam:
    team = (
        await db.execute(
            select(HackathonTeam)
            .where(HackathonTeam.id == team_id)
            .options(selectinload(HackathonTeam.members))
        )
    ).scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Équipe introuvable.")
    return team


# --- Teams ----------------------------------------------------------------


@admin_hackathon_teams_router.get("", response_model=list[HackathonTeamRead])
@limiter.limit("30/minute")
async def list_teams_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("hackathon.manage")),
) -> list[HackathonTeamRead]:
    teams = (
        (
            await db.execute(
                select(HackathonTeam)
                .options(selectinload(HackathonTeam.members))
                .order_by(HackathonTeam.university_name, HackathonTeam.name)
            )
        )
        .scalars()
        .all()
    )
    return [HackathonTeamRead.model_validate(team) for team in teams]


@admin_hackathon_teams_router.post(
    "", response_model=HackathonTeamRead, status_code=status.HTTP_201_CREATED
)
@limiter.limit("30/minute")
async def create_team(
    request: Request,
    body: HackathonTeamCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("hackathon.manage")),
) -> HackathonTeamRead:
    team = HackathonTeam(
        university_name=body.university_name,
        name=body.name,
        project_name=body.project_name,
        project_description=body.project_description,
    )
    db.add(team)
    await db.commit()
    team = await _get_team_or_404(db, team.id)
    return HackathonTeamRead.model_validate(team)


@admin_hackathon_teams_router.patch("/{team_id}", response_model=HackathonTeamRead)
@limiter.limit("30/minute")
async def update_team(
    request: Request,
    team_id: int,
    body: HackathonTeamUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("hackathon.manage")),
) -> HackathonTeamRead:
    team = await _get_team_or_404(db, team_id)

    if body.university_name is not None:
        team.university_name = body.university_name
    if body.name is not None:
        team.name = body.name
    if body.project_name is not None:
        team.project_name = body.project_name
    if body.project_description is not None:
        team.project_description = body.project_description

    await db.commit()
    team = await _get_team_or_404(db, team_id)
    return HackathonTeamRead.model_validate(team)


@admin_hackathon_teams_router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_team(
    request: Request,
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("hackathon.manage")),
) -> None:
    team = await _get_team_or_404(db, team_id)
    if team.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer une équipe ayant des membres rattachés.",
        )

    await db.delete(team)
    await db.commit()


# --- Team members -----------------------------------------------------------


@admin_hackathon_teams_router.post(
    "/{team_id}/members",
    response_model=HackathonTeamMemberRead,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("30/minute")
async def create_team_member(
    request: Request,
    team_id: int,
    photo: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("hackathon.manage")),
) -> HackathonTeamMemberRead:
    await _get_team_or_404(db, team_id)
    body = await parse_multipart_form(request, HackathonTeamMemberCreate)

    photo_url = None
    if photo is not None:
        content = await photo.read()
        try:
            photo_url = await upload_file(
                content,
                photo.filename or "photo",
                photo.content_type or "",
                max_bytes=MAX_PHOTO_BYTES,
            )
        except UploadRejectedError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    member = HackathonTeamMember(
        team_id=team_id,
        full_name=body.full_name,
        study_level=body.study_level,
        specialty=body.specialty,
        photo_url=photo_url,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return HackathonTeamMemberRead.model_validate(member)


@admin_hackathon_teams_router.patch(
    "/{team_id}/members/{member_id}", response_model=HackathonTeamMemberRead
)
@limiter.limit("30/minute")
async def update_team_member(
    request: Request,
    team_id: int,
    member_id: int,
    photo: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("hackathon.manage")),
) -> HackathonTeamMemberRead:
    member = await db.get(HackathonTeamMember, member_id)
    if member is None or member.team_id != team_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membre introuvable.")

    body = await parse_multipart_form(request, HackathonTeamMemberUpdate)

    if photo is not None:
        content = await photo.read()
        try:
            member.photo_url = await upload_file(
                content,
                photo.filename or "photo",
                photo.content_type or "",
                max_bytes=MAX_PHOTO_BYTES,
            )
        except UploadRejectedError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if body.full_name is not None:
        member.full_name = body.full_name
    if body.study_level is not None:
        member.study_level = body.study_level
    if body.specialty is not None:
        member.specialty = body.specialty

    await db.commit()
    await db.refresh(member)
    return HackathonTeamMemberRead.model_validate(member)


@admin_hackathon_teams_router.delete(
    "/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT
)
@limiter.limit("30/minute")
async def delete_team_member(
    request: Request,
    team_id: int,
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("hackathon.manage")),
) -> None:
    member = await db.get(HackathonTeamMember, member_id)
    if member is None or member.team_id != team_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membre introuvable.")

    await db.delete(member)
    await db.commit()
