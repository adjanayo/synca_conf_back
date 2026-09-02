# [Base & Base] Cluster

> 109 nodes · cohesion 0.03

## Key Concepts

- **BaseModel** (70 connections)
- [referentials.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/referentials.py#L1) (10 connections)
- [admin_applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L1) (8 connections)
- **ValueError** (8 connections)
- [auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L1) (6 connections)
- [payments.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payments.py#L1) (6 connections)
- [rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/rbac.py#L1) (6 connections)
- [login()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/auth.py#L25) (5 connections)
- [RoleWithPermissionsRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/rbac.py#L17) (4 connections)
- [applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/applications.py#L1) (4 connections)
- [RegistrationRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_registrations.py#L6) (3 connections)
- [AdminStatsRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_stats.py#L4) (3 connections)
- [AdminMeOut](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L29) (3 connections)
- [TokenPair](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L9) (3 connections)
- [PromoValidateResponse](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py#L8) (3 connections)
- [AdminUserRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/rbac.py#L40) (3 connections)
- [update_role_permissions()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/rbac.py#L58) (3 connections)
- [rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/rbac.py#L1) (3 connections)
- [admin_users.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_users.py#L1) (3 connections)
- [content.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/content.py#L1) (3 connections)
- [exhibitor_apply.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/exhibitor_apply.py#L1) (3 connections)
- [sessions.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/sessions.py#L1) (3 connections)
- [AmbassadorAdminCreate](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L79) (2 connections)
- [AmbassadorStatusUpdate](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L29) (2 connections)
- [ExhibitorAdminCreate](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L133) (2 connections)
- *... and 84 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class AmbassadorAdminCreate {
        +admin_applications.py()
    }
    class AmbassadorStatusUpdate {
        +admin_applications.py()
    }
    class ExhibitorAdminCreate {
        +admin_applications.py()
    }
    class ExhibitorStatusUpdate {
        +admin_applications.py()
    }
    class PartnerAdminCreate {
        +admin_applications.py()
    }
    class PartnerStatusUpdate {
        +admin_applications.py()
    }
    class SpeakerAdminCreate {
        +admin_applications.py()
    }
    class SpeakerStatusUpdate {
        +admin_applications.py()
    }
    class RegistrationRead {
        +admin_registrations.py()
    }
    class AdminStatsRead {
        +admin_stats.py()
    }
    class AdminUserCreate {
        +admin_users.py()
    }
    class AdminUserRead {
        +admin_users.py()
    }
    class AdminUserUpdate {
        +admin_users.py()
    }
    class AmbassadorApplyCreate {
        +ambassador_apply.py()
    }
    class AmbassadorRead {
        +applications.py()
    }
    class ExhibitorRead {
        +applications.py()
    }
    class PartnerRead {
        +applications.py()
    }
    class SpeakerRead {
        +applications.py()
    }
    class AuditLogRead {
        +audit.py()
    }
    class AdminLoginRequest {
        +auth.py()
    }
    class AdminMeOut {
        +auth.py()
    }
    class OtpRequestIn {
        +auth.py()
    }
    class OtpVerifyIn {
        +auth.py()
    }
    class TokenPair {
        +auth.py()
    }
    class CampaignWindowRead {
        +campaign.py()
    }
    class CampaignWindowUpdate {
        +campaign.py()
    }
    class ContactCreate {
        +contact.py()
    }
    class ContactMessageRead {
        +content.py()
    }
    class ContactMessageUpdate {
        +content.py()
    }
    class FaqRead {
        +content.py()
    }
    class ExhibitorApplyCreate {
        +exhibitor_apply.py()
    }
    class NewsletterCreate {
        +newsletter.py()
    }
    class NewsletterSubscriberRead {
        +newsletter.py()
    }
    class PartnerApplyCreate {
        +partner_apply.py()
    }
    class PaymentCreate {
        +payment_create.py()
    }
    class PaymentWebhookPayload {
        +payment_webhook.py()
    }
    class PaymentRead {
        +payments.py()
    }
    class PromoCodeCreate {
        +payments.py()
    }
    class PromoCodeRead {
        +payments.py()
    }
    class PromoCodeUpdate {
        +payments.py()
    }
    class TicketRead {
        +payments.py()
    }
    class WaitlistRead {
        +payments.py()
    }
    class PromoValidateRequest {
        +promo.py()
    }
    class PromoValidateResponse {
        +promo.py()
    }
    class AdminUserRead {
        +rbac.py()
    }
    class PermissionRead {
        +rbac.py()
    }
    class RolePermissionRead {
        +rbac.py()
    }
    class RoleRead {
        +rbac.py()
    }
    class RoleUpdate {
        +rbac.py()
    }
    class RoleWithPermissionsRead {
        +rbac.py()
    }
    class DayCreate {
        +referentials.py()
    }
    class DayRead {
        +referentials.py()
    }
    class DayUpdate {
        +referentials.py()
    }
    class EventSettingsRead {
        +referentials.py()
    }
    class EventSettingsUpdate {
        +referentials.py()
    }
    class FaqCategoryRead {
        +referentials.py()
    }
    class PartnerLevelRead {
        +referentials.py()
    }
    class PassTypeCreate {
        +referentials.py()
    }
    class PassTypeRead {
        +referentials.py()
    }
    class PassTypeUpdate {
        +referentials.py()
    }
    class RegisterCreate {
        +register.py()
    }
    class SessionCreate {
        +sessions.py()
    }
    class SessionRead {
        +sessions.py()
    }
    class SessionUpdate {
        +sessions.py()
    }
    class SpeakerApplyCreate {
        +speaker_apply.py()
    }
    class WaitlistCreate {
        +waitlist.py()
    }
```

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_registrations.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_registrations.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_stats.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_stats.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/auth.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/rbac.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_registrations.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_registrations.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_stats.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_stats.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_users.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_users.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/ambassador_apply.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/ambassador_apply.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/applications.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/audit.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/audit.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/campaign.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/campaign.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/contact.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/contact.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/content.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/content.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/exhibitor_apply.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/exhibitor_apply.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/newsletter.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/newsletter.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/partner_apply.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/partner_apply.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payment_create.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payment_create.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payment_webhook.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payment_webhook.py)

## Audit Trail

- EXTRACTED: 297 (91%)
- INFERRED: 30 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*