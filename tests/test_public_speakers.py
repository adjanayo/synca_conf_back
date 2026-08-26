import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import Speaker


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


def make_speaker(**overrides) -> Speaker:
    defaults = dict(
        first_name="M",
        last_name="Ba",
        title_role="CTO",
        country="SN",
        email="m@example.com",
        phone_whatsapp="+221700000000",
        intervention_format="Keynote",
        intervention_title="Titre",
        theme="IA",
        summary="Résumé",
        motivation="Motivation",
        gdpr_consent=True,
        is_public=True,
    )
    defaults.update(overrides)
    return Speaker(**defaults)


@pytest.mark.asyncio
async def test_speakers_filter_by_theme_and_format_excludes_private(db_session, client):
    db_session.add_all(
        [
            make_speaker(email="a@example.com", theme="IA", intervention_format="Keynote"),
            make_speaker(
                email="b@example.com", theme="Cybersec", intervention_format="Panel",
                last_name="Zzz",
            ),
            make_speaker(
                email="c@example.com", theme="IA", intervention_format="Keynote",
                is_public=False, last_name="Aaa",
            ),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/speakers?theme=IA&format=Keynote")

    assert response.status_code == 200
    emails = [s["email"] for s in response.json()]
    assert emails == ["a@example.com"]


@pytest.mark.asyncio
async def test_speakers_empty_result(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/speakers?theme=Impact")

    assert response.status_code == 200
    assert response.json() == []
