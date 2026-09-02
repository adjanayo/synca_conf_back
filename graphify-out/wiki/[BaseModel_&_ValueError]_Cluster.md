# [BaseModel & ValueError] Cluster

> 84 nodes · cohesion 0.03

## Key Concepts

- **BaseModel** (50 connections)
- **ValueError** (8 connections)
- [rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/rbac.py#L1) (6 connections)
- [login()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/auth.py#L21) (5 connections)
- [auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L1) (5 connections)
- [admin_applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L1) (4 connections)
- [applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/applications.py#L1) (4 connections)
- [payments.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payments.py#L1) (4 connections)
- [referentials.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/referentials.py#L1) (4 connections)
- [RegistrationRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_registrations.py#L6) (3 connections)
- [AdminStatsRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_stats.py#L4) (3 connections)
- [TokenPair](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L9) (3 connections)
- [PromoValidateResponse](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py#L8) (3 connections)
- [RoleWithPermissionsRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/rbac.py#L17) (3 connections)
- [update_role_permissions()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/rbac.py#L17) (3 connections)
- [exhibitor_apply.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/exhibitor_apply.py#L1) (3 connections)
- [AmbassadorStatusUpdate](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L12) (2 connections)
- [ExhibitorStatusUpdate](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L20) (2 connections)
- [PartnerStatusUpdate](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L16) (2 connections)
- [SpeakerStatusUpdate](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/admin_applications.py#L8) (2 connections)
- [list_registrations()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_registrations.py#L20) (2 connections)
- [get_admin_stats()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_stats.py#L23) (2 connections)
- [AmbassadorApplyCreate](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/ambassador_apply.py#L13) (2 connections)
- [gdpr_must_be_true()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/ambassador_apply.py#L36) (2 connections)
- [AmbassadorRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/applications.py#L39) (2 connections)
- *... and 59 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class AmbassadorStatusUpdate {
        +admin_applications.py()
    }
    class ExhibitorStatusUpdate {
        +admin_applications.py()
    }
    class PartnerStatusUpdate {
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
    class AdminLoginRequest {
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
    class PromoCodeRead {
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
    class DayRead {
        +referentials.py()
    }
    class FaqCategoryRead {
        +referentials.py()
    }
    class PartnerLevelRead {
        +referentials.py()
    }
    class PassTypeRead {
        +referentials.py()
    }
    class RegisterCreate {
        +register.py()
    }
    class SessionRead {
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
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/ambassador_apply.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/ambassador_apply.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/applications.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/campaign.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/campaign.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/contact.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/contact.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/content.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/content.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/exhibitor_apply.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/exhibitor_apply.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/newsletter.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/newsletter.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/partner_apply.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/partner_apply.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payment_create.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payment_create.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payment_webhook.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payment_webhook.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payments.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/payments.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py)

## Audit Trail

- EXTRACTED: 211 (89%)
- INFERRED: 25 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*