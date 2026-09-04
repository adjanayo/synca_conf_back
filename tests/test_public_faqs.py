import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import Faq, FaqCategory


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_faqs_filter_by_category(db_session, client):
    billeterie = FaqCategory(name="Billetterie (test)")
    speakers = FaqCategory(name="Speakers (test)")
    db_session.add_all([billeterie, speakers])
    await db_session.flush()

    db_session.add_all(
        [
            Faq(category_id=billeterie.id, question="Q1?", answer="A1.", sort_order=1),
            Faq(category_id=speakers.id, question="Q2?", answer="A2.", sort_order=0),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(f"/api/faqs?category={billeterie.id}")

    assert response.status_code == 200
    questions = [f["question"] for f in response.json()]
    assert questions == ["Q1?"]


@pytest.mark.asyncio
async def test_faqs_empty_result(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/faqs?category=999999")

    assert response.status_code == 200
    assert response.json() == []
