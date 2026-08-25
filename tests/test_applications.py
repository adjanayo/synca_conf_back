import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Ambassador, Exhibitor, Partner, PartnerLevel, Speaker


def make_speaker(**overrides) -> Speaker:
    defaults = dict(
        first_name="Moussa",
        last_name="Ba",
        title_role="CTO",
        country="Sénégal",
        email="moussa@example.com",
        phone_whatsapp="+221771111111",
        intervention_format="Keynote",
        intervention_title="L'IA en Afrique",
        theme="IA",
        summary="Résumé de l'intervention.",
        motivation="Envie de partager.",
        gdpr_consent=True,
    )
    defaults.update(overrides)
    return Speaker(**defaults)


@pytest.mark.asyncio
async def test_speaker_default_status_pending_and_not_public(db_session):
    speaker = make_speaker()
    db_session.add(speaker)
    await db_session.commit()
    await db_session.refresh(speaker)

    assert speaker.status == "pending"
    assert speaker.is_public is False


@pytest.mark.asyncio
async def test_speaker_status_workflow_transition(db_session):
    speaker = make_speaker(email="autre@example.com")
    db_session.add(speaker)
    await db_session.commit()

    speaker.status = "accepted"
    speaker.is_public = True
    await db_session.commit()
    await db_session.refresh(speaker)

    assert speaker.status == "accepted"
    assert speaker.is_public is True


@pytest.mark.asyncio
async def test_ambassador_social_handles_json(db_session):
    ambassador = Ambassador(
        first_name="Fatou",
        last_name="Sow",
        age=22,
        country="Sénégal",
        city="Dakar",
        email="fatou@example.com",
        phone_whatsapp="+221772222222",
        social_handles={"instagram": "@fatou", "x": "@fatou_x"},
        motivation="Motivation.",
        mobilization_plan="Plan.",
        preferred_channels="WhatsApp, Instagram",
        gdpr_consent=True,
    )
    db_session.add(ambassador)
    await db_session.commit()
    await db_session.refresh(ambassador)

    assert ambassador.social_handles == {"instagram": "@fatou", "x": "@fatou_x"}
    assert ambassador.status == "pending"


@pytest.mark.asyncio
async def test_partner_requires_valid_level_fk(db_session):
    partner = Partner(
        organization_name="ACME",
        sector="Tech/ESN",
        country="Sénégal",
        city="Dakar",
        contact_name="Jean Dupont",
        contact_position="CEO",
        contact_email="jean@acme.com",
        contact_phone="+221773333333",
        level_id=999999,
        objectives="Visibilité",
        gdpr_consent=True,
    )
    db_session.add(partner)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_partner_negotiation_workflow(db_session):
    level = PartnerLevel(name="Silver", price=200000)
    db_session.add(level)
    await db_session.flush()

    partner = Partner(
        organization_name="ACME",
        sector="Tech/ESN",
        country="Sénégal",
        city="Dakar",
        contact_name="Jean Dupont",
        contact_position="CEO",
        contact_email="jean@acme.com",
        contact_phone="+221773333333",
        level_id=level.id,
        objectives="Visibilité",
        gdpr_consent=True,
    )
    db_session.add(partner)
    await db_session.commit()
    assert partner.status == "pending"

    for next_status in ("contacted", "negotiating", "confirmed"):
        partner.status = next_status
        await db_session.commit()
        await db_session.refresh(partner)
        assert partner.status == next_status


@pytest.mark.asyncio
async def test_exhibitor_default_status_and_public(db_session):
    exhibitor = Exhibitor(
        organization_name="Expo Corp",
        sector="Tech",
        country="Sénégal",
        city="Dakar",
        contact_name="Awa Fall",
        contact_position="Manager",
        contact_email="awa@expo.com",
        contact_phone="+221774444444",
        stand_type="Standard",
        reps_count=2,
        products_services="Logiciels B2B",
        rules_accepted=True,
        gdpr_consent=True,
    )
    db_session.add(exhibitor)
    await db_session.commit()
    await db_session.refresh(exhibitor)

    assert exhibitor.status == "pending"
    assert exhibitor.is_public is False
