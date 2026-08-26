import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.deps.pagination import pagination_params
from app.main import app
from app.models import Faq, FaqCategory


def test_pagination_custom_values():
    pagination = pagination_params(limit=10, offset=20)
    assert pagination.limit == 10
    assert pagination.offset == 20


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint",
    ["/api/sessions", "/api/speakers", "/api/partners", "/api/exhibitors", "/api/faqs"],
)
async def test_pagination_rejects_out_of_range_limit(db_session, client, endpoint):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        too_high = await http.get(endpoint, params={"limit": 500})
        too_low = await http.get(endpoint, params={"limit": 0})
        negative_offset = await http.get(endpoint, params={"offset": -1})

    assert too_high.status_code == 422
    assert too_low.status_code == 422
    assert negative_offset.status_code == 422


@pytest.mark.asyncio
async def test_pagination_defaults_apply_without_query_params(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/faqs")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_pagination_limit_actually_limits_results(db_session, client):
    category = FaqCategory(name="Test")
    db_session.add(category)
    await db_session.flush()

    db_session.add_all(
        [
            Faq(category_id=category.id, question=f"Q{i}?", answer="A.", sort_order=i)
            for i in range(5)
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/faqs", params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2
