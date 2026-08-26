from sqladmin import ModelView
from starlette.requests import Request

from app.models import Ambassador, ContactMessage, Exhibitor, Partner, Speaker


def _has_permission(request: Request, code: str) -> bool:
    return code in request.session.get("permissions", [])


class SpeakerAdmin(ModelView, model=Speaker):
    name = "Speaker"
    name_plural = "Speakers"
    icon = "fa-solid fa-microphone"
    column_list = [
        Speaker.id,
        Speaker.first_name,
        Speaker.last_name,
        Speaker.theme,
        Speaker.status,
        Speaker.is_public,
        Speaker.created_at,
    ]
    column_searchable_list = [Speaker.first_name, Speaker.last_name, Speaker.email]
    column_sortable_list = [Speaker.created_at, Speaker.status]

    def is_accessible(self, request: Request) -> bool:
        return _has_permission(request, "speakers.approve")


class AmbassadorAdmin(ModelView, model=Ambassador):
    name = "Ambassador"
    name_plural = "Ambassadors"
    icon = "fa-solid fa-bullhorn"
    column_list = [
        Ambassador.id,
        Ambassador.first_name,
        Ambassador.last_name,
        Ambassador.country,
        Ambassador.status,
        Ambassador.created_at,
    ]
    column_searchable_list = [Ambassador.first_name, Ambassador.last_name, Ambassador.email]
    column_sortable_list = [Ambassador.created_at, Ambassador.status]

    def is_accessible(self, request: Request) -> bool:
        return _has_permission(request, "ambassadors.approve")


class PartnerAdmin(ModelView, model=Partner):
    name = "Partner"
    name_plural = "Partners"
    icon = "fa-solid fa-handshake"
    column_list = [
        Partner.id,
        Partner.organization_name,
        Partner.sector,
        Partner.level,
        Partner.status,
        Partner.is_public,
        Partner.created_at,
    ]
    column_searchable_list = [Partner.organization_name, Partner.contact_email]
    column_sortable_list = [Partner.created_at, Partner.status]

    def is_accessible(self, request: Request) -> bool:
        return _has_permission(request, "partners.manage")


class ExhibitorAdmin(ModelView, model=Exhibitor):
    name = "Exhibitor"
    name_plural = "Exhibitors"
    icon = "fa-solid fa-store"
    column_list = [
        Exhibitor.id,
        Exhibitor.organization_name,
        Exhibitor.stand_type,
        Exhibitor.status,
        Exhibitor.is_public,
        Exhibitor.created_at,
    ]
    column_searchable_list = [Exhibitor.organization_name, Exhibitor.contact_email]
    column_sortable_list = [Exhibitor.created_at, Exhibitor.status]

    def is_accessible(self, request: Request) -> bool:
        return _has_permission(request, "exhibitors.manage")


class ContactMessageAdmin(ModelView, model=ContactMessage):
    name = "Contact Message"
    name_plural = "Contact Messages"
    icon = "fa-solid fa-envelope"
    column_list = [
        ContactMessage.id,
        ContactMessage.name,
        ContactMessage.email,
        ContactMessage.subject,
        ContactMessage.is_read,
        ContactMessage.created_at,
    ]
    column_searchable_list = [ContactMessage.name, ContactMessage.email, ContactMessage.subject]
    column_sortable_list = [ContactMessage.created_at, ContactMessage.is_read]
    can_create = False
    can_delete = False

    # No dedicated permission code exists for contact messages (they're
    # informational, not a workflow to gate like the application tables) --
    # any admin who passes SQLAdmin's authenticate() may read/triage them.
    def is_accessible(self, request: Request) -> bool:
        return True


ADMIN_VIEWS = [
    SpeakerAdmin,
    AmbassadorAdmin,
    PartnerAdmin,
    ExhibitorAdmin,
    ContactMessageAdmin,
]
