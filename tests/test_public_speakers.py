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
            make_speaker(
                email="a@example.com", theme="IA", intervention_format="Keynote",
                last_name="Visible",
            ),
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
    body = response.json()
    last_names = [s["last_name"] for s in body]
    assert last_names == ["Visible"]
    assert "email" not in body[0]
    assert "phone_whatsapp" not in body[0]


@pytest.mark.asyncio
async def test_speakers_empty_result(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/speakers?theme=Impact")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_speaker_detail(db_session, client):
    speaker = make_speaker(last_name="Détail")
    db_session.add(speaker)
    await db_session.commit()
    await db_session.refresh(speaker)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(f"/api/speakers/{speaker.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["last_name"] == "Détail"
    assert "email" not in body
    assert "phone_whatsapp" not in body


@pytest.mark.asyncio
async def test_get_speaker_detail_404_when_not_public(db_session, client):
    speaker = make_speaker(is_public=False)
    db_session.add(speaker)
    await db_session.commit()
    await db_session.refresh(speaker)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(f"/api/speakers/{speaker.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_speaker_detail_404_when_missing(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/speakers/999999")

    assert response.status_code == 404
