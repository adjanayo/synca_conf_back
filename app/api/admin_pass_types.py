from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.referentials import PassType
from app.schemas.referentials import PassTypeCreate, PassTypeRead, PassTypeUpdate

router = APIRouter(prefix="/api/admin/pass-types", tags=["admin-pass-types"])


@router.get("", response_model=list[PassTypeRead])
@limiter.limit("30/minute")
async def list_pass_types_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("pass_types.manage")),
) -> list[PassTypeRead]:
    pass_types = (
        await db.execute(select(PassType).order_by(PassType.price))
    ).scalars().all()
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

    pass_type = PassType(
        name=body.name,
        price=body.price,
        description=body.description,
        inclusions=body.inclusions,
        max_days=body.max_days,
        is_active=body.is_active,
    )
    db.add(pass_type)
    await db.commit()
    await db.refresh(pass_type)
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
    pass_type = await db.get(PassType, pass_type_id)
    if pass_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pass introuvable."
        )

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
    if body.inclusions is not None:
        pass_type.inclusions = body.inclusions
    if body.max_days is not None:
        pass_type.max_days = body.max_days
    if body.is_active is not None:
        pass_type.is_active = body.is_active

    await db.commit()
    await db.refresh(pass_type)
    return PassTypeRead.model_validate(pass_type)
