import datetime

from app.models import (
    AdminUser,
    Ambassador,
    CampaignWindow,
    ContactMessage,
    Day,
    Exhibitor,
    Faq,
    FaqCategory,
    Partner,
    PartnerLevel,
    PassType,
    Payment,
    Permission,
    PromoCode,
    Role,
    RolePermission,
    Session,
    Speaker,
    Ticket,
    User,
    UserProfile,
    Waitlist,
)
from app.schemas import (
    AdminUserRead,
    AmbassadorRead,
    CampaignWindowRead,
    ContactMessageRead,
    DayRead,
    ExhibitorRead,
    FaqCategoryRead,
    FaqRead,
    PartnerLevelRead,
    PartnerRead,
    PassTypeRead,
    PaymentRead,
    PermissionRead,
    PromoCodeRead,
    RolePermissionRead,
    RoleRead,
    SessionRead,
    SpeakerRead,
    TicketRead,
    UserProfileRead,
    UserRead,
    WaitlistRead,
)

NOW = datetime.datetime(2027, 1, 1)
TODAY = datetime.date(2027, 1, 1)


def test_day_read():
    obj = Day(id=1, date=TODAY, label="Jour 1", created_at=NOW)
    read = DayRead.model_validate(obj)
    assert read.label == "Jour 1"


def test_pass_type_read():
    obj = PassType(
        id=1, name="Standard", price=15000, description=None,
        max_days=3, is_active=True, created_at=NOW,
    )
    read = PassTypeRead.model_validate(obj)
    assert read.price == 15000


def test_partner_level_read():
    obj = PartnerLevel(id=1, name="Gold", price=500000, sort_order=0, created_at=NOW)
    read = PartnerLevelRead.model_validate(obj)
    assert read.name == "Gold"


def test_faq_category_read():
    obj = FaqCategory(id=1, name="Billetterie")
    read = FaqCategoryRead.model_validate(obj)
    assert read.name == "Billetterie"


def test_user_and_profile_read():
    user = User(
        id=1, first_name="Awa", last_name="Diop", gender=None, email="awa@example.com",
        email_verified=False, phone_whatsapp="+221771234567", country="Sénégal", city="Dakar",
        sector=None, experience_level=None, linkedin_url=None, portfolio_url=None,
        special_needs=None, heard_from=None, gdpr_consent=True, newsletter_consent=False,
        created_at=NOW, updated_at=NOW,
    )
    read = UserRead.model_validate(user)
    assert read.email == "awa@example.com"

    profile = UserProfile(id=1, user_id=1, profile="Étudiant")
    profile_read = UserProfileRead.model_validate(profile)
    assert profile_read.profile == "Étudiant"


def test_session_read():
    obj = Session(
        id=1, day_id=1, title="Keynote", description=None, category="keynote",
        start_time=datetime.time(9, 0), end_time=datetime.time(10, 0), room=None,
        speaker_id=None, is_public=True, created_at=NOW,
    )
    read = SessionRead.model_validate(obj)
    assert read.category == "keynote"


def test_promo_code_payment_ticket_waitlist_read():
    promo = PromoCode(
        id=1, code="AMB1", discount_pct=10, discount_fixed=None, usage_limit=None,
        usage_count=0, valid_from=None, valid_until=None, is_active=True, created_at=NOW,
    )
    assert PromoCodeRead.model_validate(promo).code == "AMB1"

    payment = Payment(
        id=1, user_id=1, pass_type_id=1, promo_code_id=None, amount_original=15000,
        amount_paid=15000, currency="XOF", payment_method="wave", transaction_ref=None,
        status="pending", paid_at=None, created_at=NOW,
    )
    assert PaymentRead.model_validate(payment).status == "pending"

    ticket = Ticket(
        id=1, user_id=1, payment_id=1, pass_type_id=1, ticket_number="SYNCA-0001",
        qr_code_hash="hash", pdf_url=None, is_scanned=False, scanned_at=None, created_at=NOW,
    )
    assert TicketRead.model_validate(ticket).ticket_number == "SYNCA-0001"

    waitlist = Waitlist(
        id=1, email="a@example.com", notified=False, registered=False, created_at=NOW
    )
    assert WaitlistRead.model_validate(waitlist).email == "a@example.com"


def test_applications_read():
    speaker = Speaker(
        id=1, first_name="M", last_name="B", title_role="CTO", company=None, country="SN",
        email="m@example.com", phone_whatsapp="+221700000000", linkedin_url=None,
        website_url=None, photo_url=None, intervention_format="Keynote",
        intervention_title="Titre", theme="IA", summary="Résumé", audience_level=None,
        language=None, past_experience=None, video_link=None, availability=None,
        departure_city=None, needs_accommodation=False, motivation="Motivation",
        video_consent=None, gdpr_consent=True, status="pending", is_public=False, created_at=NOW,
    )
    assert SpeakerRead.model_validate(speaker).status == "pending"

    ambassador = Ambassador(
        id=1, first_name="F", last_name="S", age=22, country="SN", city="Dakar",
        email="f@example.com", phone_whatsapp="+221700000001", current_profile=None,
        institution_company=None, linkedin_url=None, social_handles={"instagram": "@f"},
        followers_range=None, motivation="M", mobilization_plan="P", estimated_reach=None,
        previous_synca=False, preferred_channels="WhatsApp", availability_pre=None,
        gdpr_consent=True, promo_code_id=None, status="pending", created_at=NOW,
    )
    assert AmbassadorRead.model_validate(ambassador).social_handles == {"instagram": "@f"}

    partner = Partner(
        id=1, organization_name="ACME", sector="Tech/ESN", country="SN", city="Dakar",
        website_url=None, contact_name="J", contact_position="CEO", contact_email="j@acme.com",
        contact_phone="+221700000002", level_id=1, has_budget=None, objectives="Visibilité",
        previous_sponsor=False, message=None, heard_from=None, gdpr_consent=True,
        status="pending", logo_url=None, is_public=False, created_at=NOW,
    )
    assert PartnerRead.model_validate(partner).organization_name == "ACME"

    exhibitor = Exhibitor(
        id=1, organization_name="Expo", sector="Tech", country="SN", city="Dakar",
        website_url=None, contact_name="A", contact_position="Manager",
        contact_email="a@expo.com", contact_phone="+221700000003", stand_type="Standard",
        reps_count=2, linked_partner_level=None, products_services="Logiciels",
        equipment_needs=None, side_activities=None, visuals_url=None, payment_method=None,
        rules_accepted=True, gdpr_consent=True, status="pending", is_public=False, created_at=NOW,
    )
    assert ExhibitorRead.model_validate(exhibitor).stand_type == "Standard"


def test_content_read():
    faq = Faq(id=1, category_id=1, question="Q?", answer="A.", sort_order=0, created_at=NOW)
    assert FaqRead.model_validate(faq).answer == "A."

    message = ContactMessage(
        id=1, name="Awa", email="awa@example.com", subject=None, message="Bonjour",
        is_read=False, created_at=NOW,
    )
    assert ContactMessageRead.model_validate(message).is_read is False


def test_rbac_read():
    role = Role(id=1, name="superadmin")
    assert RoleRead.model_validate(role).name == "superadmin"

    permission = Permission(id=1, code="speakers.approve")
    assert PermissionRead.model_validate(permission).code == "speakers.approve"

    role_permission = RolePermission(id=1, role_id=1, permission_id=1)
    assert RolePermissionRead.model_validate(role_permission).role_id == 1

    admin_user = AdminUser(
        id=1, email="admin@synca.conf", password_hash="hash", role_id=1,
        last_login=None, created_at=NOW,
    )
    read = AdminUserRead.model_validate(admin_user)
    assert read.email == "admin@synca.conf"
    assert not hasattr(read, "password_hash")


def test_campaign_window_read():
    obj = CampaignWindow(
        id=1, key="ticketing", start_at=NOW, end_at=NOW + datetime.timedelta(days=1),
        is_active=True, created_at=NOW, updated_at=NOW,
    )
    assert CampaignWindowRead.model_validate(obj).key == "ticketing"
