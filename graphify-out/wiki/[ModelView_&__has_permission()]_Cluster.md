# [ModelView & _has_permission()] Cluster

> 17 nodes · cohesion 0.13

## Key Concepts

- [create_payment()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/payments.py#L48) (4 connections)
- [generate_ambassador_promo_code()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/promo_service.py#L36) (4 connections)
- [get_valid_promo_code()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/promo_service.py#L14) (4 connections)
- [admin_applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_applications.py#L1) (4 connections)
- [_validate_promo_code()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/forms.py#L55) (3 connections)
- [validate_promo()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/payments.py#L31) (3 connections)
- [PromoValidateResponse](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py#L8) (3 connections)
- [payments.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/payments.py#L1) (3 connections)
- [promo_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/promo_service.py#L1) (3 connections)
- [update_ambassador_status()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_applications.py#L49) (2 connections)
- [PromoValidateRequest](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py#L4) (2 connections)
- [compute_discounted_amount()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/promo_service.py#L30) (2 connections)
- [promo.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py#L1) (2 connections)
- [update_exhibitor_status()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_applications.py#L92) (1 connections)
- [update_partner_status()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_applications.py#L72) (1 connections)
- [update_speaker_status()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_applications.py#L27) (1 connections)
- [Create and attach a promo code to a newly-accepted ambassador.      No usage_lim](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/promo_service.py#L37) (1 connections)

## Class Diagram

```mermaid
classDiagram
    class PromoValidateRequest {
        +promo.py()
    }
    class PromoValidateResponse {
        +promo.py()
    }
```

## Relationships

- [[[verify_stripe_signature() & payment_webhook()] Cluster]] (1 shared connections)

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_applications.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/forms.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/forms.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/payments.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/payments.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/promo.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/promo_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/promo_service.py)

## Audit Trail

- EXTRACTED: 29 (67%)
- INFERRED: 14 (33%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*