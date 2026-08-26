# make_admin_with_permission()

> God node · 18 connections · [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_applications.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_applications.py#L22)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as make_admin_with_permission()
    participant P1 as Role
    participant P2 as Base
    participant P3 as PassType
    participant P4 as User
    participant P5 as PromoCode
    participant P6 as AdminUser
    participant P7 as Payment
    participant P8 as PartnerLevel
    participant P9 as RolePermission
    participant P10 as Permission
    participant P11 as Speaker
    participant P12 as Partner
    participant P13 as FaqCategory
    participant P14 as Ticket
    participant P15 as Exhibitor
    participant P16 as ContactMessage
    participant P17 as Day
    participant P18 as Session
    participant P19 as Ambassador
    participant P20 as Faq
    participant P21 as Waitlist
    participant P22 as UserProfile
    participant P23 as AuditLog
    participant P24 as CampaignWindow
    participant P25 as NewsletterSubscriber
    participant P26 as Run migrations in 'offline' mode.      This configures the context with just a U
    participant P27 as In this scenario we need to create an Engine     and associate a connection with
    participant P28 as Run migrations in 'online' mode.
    participant P29 as make_admin_with_permission()
    participant P30 as make_admin()
    participant P31 as make_admin_with_permission()
    participant P32 as make_admin_with_permission()
    participant P33 as make_admin_with_permission()
    participant P34 as make_admin()
    participant P35 as make_admin_with_role()
    participant P36 as test_admin_endpoint_limited_to_30_per_minute()
    participant P37 as make_admin_with_role()
    participant P38 as make_admin()
    participant P39 as test_rbac_read()
    participant P40 as test_superadmin_can_update_role_permissions()
    participant P41 as test_non_superadmin_forbidden()
    participant P42 as test_unknown_permission_code_rejected()
    participant P43 as test_unauthenticated_rejected()
    participant P44 as test_speaker_accepted_publishes_it()
    participant P45 as test_speaker_rejected_stays_unpublished()
    participant P46 as test_speaker_update_forbidden_without_permission()
    participant P47 as test_speaker_update_rejects_invalid_status()
    participant P48 as test_ambassador_accepted()
    participant P49 as test_ambassador_accepted_twice_does_not_regenerate_promo_code()
    participant P50 as test_ambassador_update_forbidden_without_permission()
    participant P51 as test_partner_confirmed_publishes_it()
    participant P52 as test_partner_negotiating_stays_unpublished()
    participant P53 as test_partner_update_forbidden_without_permission()
    participant P54 as test_exhibitor_confirmed_publishes_it()
    participant P55 as test_exhibitor_update_forbidden_without_permission()
    participant P56 as test_speaker_update_404_for_unknown_id()
    P0->>+ P1: calls
    P1-->>- P0: return
    P1->>+ P2: uses
    P2-->>- P1: return
    P2->>+ P3: uses
    P3-->>- P2: return
    P2->>+ P4: uses
    P4-->>- P2: return
    P2->>+ P1: uses
    P1-->>- P2: return
    P2->>+ P5: uses
    P5-->>- P2: return
    P2->>+ P6: uses
    P6-->>- P2: return
    P2->>+ P7: uses
    P7-->>- P2: return
    P2->>+ P8: uses
    P8-->>- P2: return
    P2->>+ P9: uses
    P9-->>- P2: return
    P2->>+ P10: uses
    P10-->>- P2: return
    P2->>+ P11: uses
    P11-->>- P2: return
    P2->>+ P12: uses
    P12-->>- P2: return
    P2->>+ P13: uses
    P13-->>- P2: return
    P2->>+ P14: uses
    P14-->>- P2: return
    P2->>+ P15: uses
    P15-->>- P2: return
    P2->>+ P16: uses
    P16-->>- P2: return
    P2->>+ P17: uses
    P17-->>- P2: return
    P2->>+ P18: uses
    P18-->>- P2: return
    P2->>+ P19: uses
    P19-->>- P2: return
    P2->>+ P20: uses
    P20-->>- P2: return
    P2->>+ P21: uses
    P21-->>- P2: return
    P2->>+ P22: uses
    P22-->>- P2: return
    P2->>+ P23: uses
    P23-->>- P2: return
    P2->>+ P24: uses
    P24-->>- P2: return
    P2->>+ P25: uses
    P25-->>- P2: return
    P2->>+ P26: uses
    P26-->>- P2: return
    P2->>+ P27: uses
    P27-->>- P2: return
    P2->>+ P28: uses
    P28-->>- P2: return
    P1->>+ P0: calls
    P0-->>- P1: return
    P1->>+ P29: calls
    P29-->>- P1: return
    P1->>+ P30: calls
    P30-->>- P1: return
    P1->>+ P31: calls
    P31-->>- P1: return
    P1->>+ P32: calls
    P32-->>- P1: return
    P1->>+ P33: calls
    P33-->>- P1: return
    P1->>+ P34: calls
    P34-->>- P1: return
    P1->>+ P35: calls
    P35-->>- P1: return
    P1->>+ P36: calls
    P36-->>- P1: return
    P1->>+ P37: calls
    P37-->>- P1: return
    P1->>+ P38: calls
    P38-->>- P1: return
    P1->>+ P39: calls
    P39-->>- P1: return
    P1->>+ P40: calls
    P40-->>- P1: return
    P1->>+ P41: calls
    P41-->>- P1: return
    P1->>+ P42: calls
    P42-->>- P1: return
    P1->>+ P43: calls
    P43-->>- P1: return
    P0->>+ P6: calls
    P6-->>- P0: return
    P0->>+ P9: calls
    P9-->>- P0: return
    P0->>+ P10: calls
    P10-->>- P0: return
    P0->>+ P44: calls
    P44-->>- P0: return
    P0->>+ P45: calls
    P45-->>- P0: return
    P0->>+ P46: calls
    P46-->>- P0: return
    P0->>+ P47: calls
    P47-->>- P0: return
    P0->>+ P48: calls
    P48-->>- P0: return
    P0->>+ P49: calls
    P49-->>- P0: return
    P0->>+ P50: calls
    P50-->>- P0: return
    P0->>+ P51: calls
    P51-->>- P0: return
    P0->>+ P52: calls
    P52-->>- P0: return
    P0->>+ P53: calls
    P53-->>- P0: return
    P0->>+ P54: calls
    P54-->>- P0: return
    P0->>+ P55: calls
    P55-->>- P0: return
    P0->>+ P56: calls
    P56-->>- P0: return
```

## Connections by Relation

### calls
- [[Role]] `INFERRED`
- [[AdminUser]] `INFERRED`
- [[RolePermission]] `INFERRED`
- [[Permission]] `INFERRED`
- [[test_speaker_accepted_publishes_it()]] `EXTRACTED`
- [[test_speaker_rejected_stays_unpublished()]] `EXTRACTED`
- [[test_speaker_update_forbidden_without_permission()]] `EXTRACTED`
- [[test_speaker_update_rejects_invalid_status()]] `EXTRACTED`
- [[test_ambassador_accepted()]] `EXTRACTED`
- [[test_ambassador_accepted_twice_does_not_regenerate_promo_code()]] `EXTRACTED`
- [[test_ambassador_update_forbidden_without_permission()]] `EXTRACTED`
- [[test_partner_confirmed_publishes_it()]] `EXTRACTED`
- [[test_partner_negotiating_stays_unpublished()]] `EXTRACTED`
- [[test_partner_update_forbidden_without_permission()]] `EXTRACTED`
- [[test_exhibitor_confirmed_publishes_it()]] `EXTRACTED`
- [[test_exhibitor_update_forbidden_without_permission()]] `EXTRACTED`
- [[test_speaker_update_404_for_unknown_id()]] `EXTRACTED`

### contains
- [[test_admin_applications.py]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*