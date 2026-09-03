from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.referentials import PassContent, PassType
from app.schemas.referentials import (
    PassContentCreate,
    PassContentRead,
    PassContentUpdate,
    PassTypeCreate,
    PassTypeRead,
    PassTypeUpdate,
)

router = APIRouter(prefix="/api/admin/pass-types", tags=["admin-pass-types"])
contents_router = APIRouter(prefix="/api/admin/pass-contents", tags=["admin-pass-contents"])


async def _resolve_contents(db: AsyncSession, content_ids: list[int]) -> list[PassContent]:
    if not content_ids:
        return []
    contents = (
        (await db.execute(select(PassContent).where(PassContent.id.in_(content_ids))))
        .scalars()
        .all()
    )
    found_ids = {c.id for c in contents}
    missing = set(content_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contenu(s) de pass introuvable(s) : {sorted(missing)}.",
        )
    return contents


async def _get_pass_type_or_404(db: AsyncSession, pass_type_id: int) -> PassType:
    pass_type = (
        await db.execute(
            select(PassType)
            .where(PassType.id == pass_type_id)
            .options(selectinload(PassType.contents))
        )
    ).scalar_one_or_none()
    if pass_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pass introuvable.")
    return pass_type


# --- Pass types -------------------------------------------------------------


@router.get("", response_model=list[PassTypeRead])
@limiter.limit("30/minute")
async def list_pass_types_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> list[PassTypeRead]:
    pass_types = (
        (
            await db.execute(
                select(PassType).order_by(PassType.price).options(selectinload(PassType.contents))
            )
        )
        .scalars()
        .all()
    )
    return [PassTypeRead.model_validate(pass_type) for pass_type in pass_types]


@router.post("", response_model=PassTypeRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_pass_type(
    request: Request,
    body: PassTypeCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> PassTypeRead:
    existing = (
        await db.execute(select(PassType).where(PassType.name == body.name))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom de pass existe déjà.",
        )

    contents = await _resolve_contents(db, body.content_ids)
    pass_type = PassType(
        name=body.name,
        price=body.price,
        description=body.description,
        max_days=body.max_days,
        is_active=body.is_active,
        contents=contents,
    )
    db.add(pass_type)
    await db.commit()
    pass_type = await _get_pass_type_or_404(db, pass_type.id)
    return PassTypeRead.model_validate(pass_type)


@router.patch("/{pass_type_id}", response_model=PassTypeRead)
@limiter.limit("30/minute")
async def update_pass_type(
    request: Request,
    pass_type_id: int,
    body: PassTypeUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> PassTypeRead:
    pass_type = await _get_pass_type_or_404(db, pass_type_id)

    if body.name is not None and body.name != pass_type.name:
        existing = (
            await db.execute(select(PassType).where(PassType.name == body.name))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom de pass existe déjà.",
            )
        pass_type.name = body.name

    if body.price is not None:
        pass_type.price = body.price
    if body.description is not None:
        pass_type.description = body.description
    if body.max_days is not None:
        pass_type.max_days = body.max_days
    if body.is_active is not None:
        pass_type.is_active = body.is_active
    if body.content_ids is not None:
        pass_type.contents = await _resolve_contents(db, body.content_ids)

    await db.commit()
    pass_type = await _get_pass_type_or_404(db, pass_type_id)
    return PassTypeRead.model_validate(pass_type)


@router.delete("/{pass_type_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_pass_type(
    request: Request,
    pass_type_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> None:
    pass_type = await _get_pass_type_or_404(db, pass_type_id)
    await db.delete(pass_type)
    await db.commit()


# --- Pass contents (catalogue de bénéfices/inclusions) -----------------------


@contents_router.get("", response_model=list[PassContentRead])
@limiter.limit("30/minute")
async def list_pass_contents_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> list[PassContentRead]:
    contents = (
        await db.execute(select(PassContent).order_by(PassContent.label))
    ).scalars().all()
    return [PassContentRead.model_validate(c) for c in contents]


@contents_router.post("", response_model=PassContentRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_pass_content(
    request: Request,
    body: PassContentCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> PassContentRead:
    existing = (
        await db.execute(select(PassContent).where(PassContent.label == body.label))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce contenu de pass existe déjà.",
        )

    content = PassContent(label=body.label)
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return PassContentRead.model_validate(content)


@contents_router.patch("/{content_id}", response_model=PassContentRead)
@limiter.limit("30/minute")
async def update_pass_content(
    request: Request,
    content_id: int,
    body: PassContentUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> PassContentRead:
    content = await db.get(PassContent, content_id)
    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contenu introuvable.")

    if body.label is not None and body.label != content.label:
        existing = (
            await db.execute(select(PassContent).where(PassContent.label == body.label))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce contenu de pass existe déjà.",
            )
        content.label = body.label

    await db.commit()
    await db.refresh(content)
    return PassContentRead.model_validate(content)


@contents_router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_pass_content(
    request: Request,
    content_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> None:
    content = await db.get(PassContent, content_id)
    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contenu introuvable.")

    # Retire aussi le contenu des pass qui l'avaient coché (table
    # d'association pure, pas de FK bloquante côté pass_types) plutôt que de
    # bloquer la suppression comme days/sessions -- un contenu de pass est un
    # simple libellé réutilisable, pas une entité avec une identité propre à
    # préserver sur les pass existants.
    await db.delete(content)
    await db.commit()
