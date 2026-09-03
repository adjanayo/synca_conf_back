from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.content import Faq
from app.models.referentials import FaqCategory
from app.schemas.content import FaqCreate, FaqRead, FaqUpdate
from app.schemas.referentials import FaqCategoryCreate, FaqCategoryRead, FaqCategoryUpdate

admin_faq_categories_router = APIRouter(
    prefix="/api/admin/faq-categories", tags=["admin-faqs"]
)
admin_faqs_router = APIRouter(prefix="/api/admin/faqs", tags=["admin-faqs"])


# --- Categories -----------------------------------------------------------


@admin_faq_categories_router.get("", response_model=list[FaqCategoryRead])
@limiter.limit("30/minute")
async def list_faq_categories_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("faqs.manage")),
) -> list[FaqCategoryRead]:
    categories = (
        await db.execute(select(FaqCategory).order_by(FaqCategory.id))
    ).scalars().all()
    return [FaqCategoryRead.model_validate(category) for category in categories]


@admin_faq_categories_router.post(
    "", response_model=FaqCategoryRead, status_code=status.HTTP_201_CREATED
)
@limiter.limit("30/minute")
async def create_faq_category(
    request: Request,
    body: FaqCategoryCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("faqs.manage")),
) -> FaqCategoryRead:
    existing = (
        await db.execute(select(FaqCategory).where(FaqCategory.name == body.name))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une catégorie FAQ existe déjà avec ce nom.",
        )

    category = FaqCategory(name=body.name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return FaqCategoryRead.model_validate(category)


@admin_faq_categories_router.patch("/{category_id}", response_model=FaqCategoryRead)
@limiter.limit("30/minute")
async def update_faq_category(
    request: Request,
    category_id: int,
    body: FaqCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("faqs.manage")),
) -> FaqCategoryRead:
    category = await db.get(FaqCategory, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie FAQ introuvable."
        )

    if body.name is not None and body.name != category.name:
        existing = (
            await db.execute(select(FaqCategory).where(FaqCategory.name == body.name))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une catégorie FAQ existe déjà avec ce nom.",
            )
        category.name = body.name

    await db.commit()
    await db.refresh(category)
    return FaqCategoryRead.model_validate(category)


@admin_faq_categories_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_faq_category(
    request: Request,
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("faqs.manage")),
) -> None:
    category = await db.get(FaqCategory, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie FAQ introuvable."
        )

    has_faqs = (
        await db.execute(select(Faq.id).where(Faq.category_id == category_id).limit(1))
    ).scalar_one_or_none()
    if has_faqs is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer une catégorie ayant des questions rattachées.",
        )

    await db.delete(category)
    await db.commit()


# --- Faqs -------------------------------------------------------------


@admin_faqs_router.get("", response_model=list[FaqRead])
@limiter.limit("30/minute")
async def list_faqs_admin(
    request: Request,
    category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("faqs.manage")),
) -> list[FaqRead]:
    query = select(Faq)
    if category_id is not None:
        query = query.where(Faq.category_id == category_id)
    query = query.order_by(Faq.category_id, Faq.sort_order)

    faqs = (await db.execute(query)).scalars().all()
    return [FaqRead.model_validate(faq) for faq in faqs]


@admin_faqs_router.post("", response_model=FaqRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_faq(
    request: Request,
    body: FaqCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("faqs.manage")),
) -> FaqRead:
    category = await db.get(FaqCategory, body.category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie FAQ introuvable."
        )

    faq = Faq(
        category_id=body.category_id,
        question=body.question,
        answer=body.answer,
        sort_order=body.sort_order,
    )
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    return FaqRead.model_validate(faq)


@admin_faqs_router.patch("/{faq_id}", response_model=FaqRead)
@limiter.limit("30/minute")
async def update_faq(
    request: Request,
    faq_id: int,
    body: FaqUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("faqs.manage")),
) -> FaqRead:
    faq = await db.get(Faq, faq_id)
    if faq is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question FAQ introuvable.")

    if body.category_id is not None and body.category_id != faq.category_id:
        category = await db.get(FaqCategory, body.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie FAQ introuvable."
            )
        faq.category_id = body.category_id

    if body.question is not None:
        faq.question = body.question
    if body.answer is not None:
        faq.answer = body.answer
    if body.sort_order is not None:
        faq.sort_order = body.sort_order

    await db.commit()
    await db.refresh(faq)
    return FaqRead.model_validate(faq)


@admin_faqs_router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_faq(
    request: Request,
    faq_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("faqs.manage")),
) -> None:
    faq = await db.get(Faq, faq_id)
    if faq is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question FAQ introuvable.")

    await db.delete(faq)
    await db.commit()
