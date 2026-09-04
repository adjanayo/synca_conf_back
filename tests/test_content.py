import pytest
from sqlalchemy import select

from app.models import ContactMessage, Faq, FaqCategory


@pytest.mark.asyncio
async def test_faq_crud_basic(db_session):
    category = FaqCategory(name="Billetterie (test)")
    db_session.add(category)
    await db_session.flush()

    faq = Faq(category_id=category.id, question="Q?", answer="A.")
    db_session.add(faq)
    await db_session.commit()

    result = await db_session.execute(select(Faq).where(Faq.category_id == category.id))
    assert result.scalar_one().answer == "A."

    faq.answer = "Réponse mise à jour."
    await db_session.commit()
    await db_session.refresh(faq)
    assert faq.answer == "Réponse mise à jour."

    await db_session.delete(faq)
    await db_session.commit()
    result = await db_session.execute(select(Faq).where(Faq.id == faq.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_contact_message_default_unread(db_session):
    message = ContactMessage(name="Awa", email="awa@example.com", message="Bonjour")
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    assert message.is_read is False
