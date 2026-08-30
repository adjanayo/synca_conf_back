# PassType

> God node · 29 connections · [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py#L19)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as PassType
    participant P1 as Base
    participant P2 as User
    participant P3 as make_pending_payment()
    participant P4 as EncryptedString
    participant P5 as make_ticket()
    participant P6 as make_user()
    participant P7 as make_payment()
    participant P8 as make_payment()
    participant P9 as test_webhook_increments_promo_usage_count_on_completion()
    participant P10 as make_user()
    participant P11 as register()
    participant P12 as make_user_and_pass()
    participant P13 as test_register_duplicate_email_conflict()
    participant P14 as make_user()
    participant P15 as make_user_and_pass_type()
    participant P16 as make_user()
    participant P17 as test_user_and_profile_read()
    participant P18 as test_null_special_needs_stays_null()
    participant P19 as Role
    participant P20 as PromoCode
    participant P21 as AdminUser
    participant P22 as Payment
    participant P23 as PartnerLevel
    participant P24 as RolePermission
    participant P25 as Permission
    participant P26 as Speaker
    participant P27 as Ticket
    participant P28 as Partner
    participant P29 as FaqCategory
    participant P30 as Exhibitor
    participant P31 as ContactMessage
    participant P32 as Day
    participant P33 as Session
    participant P34 as Ambassador
    participant P35 as Faq
    participant P36 as Waitlist
    participant P37 as UserProfile
    participant P38 as AuditLog
    participant P39 as CampaignWindow
    participant P40 as NewsletterSubscriber
    participant P41 as Run migrations in 'offline' mode.      This configures the context with just a U
    participant P42 as In this scenario we need to create an Engine     and associate a connection with
    participant P43 as Run migrations in 'online' mode.
    participant P44 as make_ticket_for()
    participant P45 as test_register_valid_promo_code_accepted()
    participant P46 as test_register_success()
    participant P47 as test_register_sends_confirmation_email()
    participant P48 as test_register_inactive_pass_type_400()
    participant P49 as test_register_invalid_promo_code_400()
    participant P50 as test_create_payment_applies_percent_discount()
    participant P51 as test_create_payment_applies_fixed_discount()
    participant P52 as test_create_payment_success_no_promo()
    participant P53 as test_create_payment_invalid_promo_400()
    participant P54 as test_list_pass_types_excludes_inactive()
    participant P55 as test_pass_type_defaults()
    participant P56 as test_create_payment_invalid_user_400()
    participant P57 as test_pass_type_read()
    P0->>+ P1: uses
    P1-->>- P0: return
    P1->>+ P0: uses
    P0-->>- P1: return
    P1->>+ P2: uses
    P2-->>- P1: return
    P2->>+ P1: uses
    P1-->>- P2: return
    P2->>+ P3: calls
    P3-->>- P2: return
    P2->>+ P4: uses
    P4-->>- P2: return
    P2->>+ P5: calls
    P5-->>- P2: return
    P2->>+ P6: calls
    P6-->>- P2: return
    P2->>+ P7: calls
    P7-->>- P2: return
    P2->>+ P8: calls
    P8-->>- P2: return
    P2->>+ P9: calls
    P9-->>- P2: return
    P2->>+ P10: calls
    P10-->>- P2: return
    P2->>+ P11: calls
    P11-->>- P2: return
    P2->>+ P12: calls
    P12-->>- P2: return
    P2->>+ P13: calls
    P13-->>- P2: return
    P2->>+ P14: calls
    P14-->>- P2: return
    P2->>+ P15: calls
    P15-->>- P2: return
    P2->>+ P16: calls
    P16-->>- P2: return
    P2->>+ P17: calls
    P17-->>- P2: return
    P2->>+ P18: calls
    P18-->>- P2: return
    P1->>+ P19: uses
    P19-->>- P1: return
    P1->>+ P20: uses
    P20-->>- P1: return
    P1->>+ P21: uses
    P21-->>- P1: return
    P1->>+ P22: uses
    P22-->>- P1: return
    P1->>+ P23: uses
    P23-->>- P1: return
    P1->>+ P24: uses
    P24-->>- P1: return
    P1->>+ P25: uses
    P25-->>- P1: return
    P1->>+ P26: uses
    P26-->>- P1: return
    P1->>+ P27: uses
    P27-->>- P1: return
    P1->>+ P28: uses
    P28-->>- P1: return
    P1->>+ P29: uses
    P29-->>- P1: return
    P1->>+ P30: uses
    P30-->>- P1: return
    P1->>+ P31: uses
    P31-->>- P1: return
    P1->>+ P32: uses
    P32-->>- P1: return
    P1->>+ P33: uses
    P33-->>- P1: return
    P1->>+ P34: uses
    P34-->>- P1: return
    P1->>+ P35: uses
    P35-->>- P1: return
    P1->>+ P36: uses
    P36-->>- P1: return
    P1->>+ P37: uses
    P37-->>- P1: return
    P1->>+ P38: uses
    P38-->>- P1: return
    P1->>+ P39: uses
    P39-->>- P1: return
    P1->>+ P40: uses
    P40-->>- P1: return
    P1->>+ P41: uses
    P41-->>- P1: return
    P1->>+ P42: uses
    P42-->>- P1: return
    P1->>+ P43: uses
    P43-->>- P1: return
    P0->>+ P20: uses
    P20-->>- P0: return
    P0->>+ P22: uses
    P22-->>- P0: return
    P0->>+ P27: uses
    P27-->>- P0: return
    P0->>+ P3: calls
    P3-->>- P0: return
    P0->>+ P36: uses
    P36-->>- P0: return
    P0->>+ P5: calls
    P5-->>- P0: return
    P0->>+ P7: calls
    P7-->>- P0: return
    P0->>+ P8: calls
    P8-->>- P0: return
    P0->>+ P9: calls
    P9-->>- P0: return
    P0->>+ P44: calls
    P44-->>- P0: return
    P0->>+ P12: calls
    P12-->>- P0: return
    P0->>+ P45: calls
    P45-->>- P0: return
    P0->>+ P13: calls
    P13-->>- P0: return
    P0->>+ P46: calls
    P46-->>- P0: return
    P0->>+ P47: calls
    P47-->>- P0: return
    P0->>+ P48: calls
    P48-->>- P0: return
    P0->>+ P49: calls
    P49-->>- P0: return
    P0->>+ P15: calls
    P15-->>- P0: return
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
    P0->>+ P57: calls
    P57-->>- P0: return
```

## Connections by Relation

### calls
- [[make_pending_payment()]] `INFERRED`
- [[make_ticket()]] `INFERRED`
- [[make_payment()]] `INFERRED`
- [[make_payment()]] `INFERRED`
- [[test_webhook_increments_promo_usage_count_on_completion()]] `INFERRED`
- [[make_ticket_for()]] `INFERRED`
- [[make_user_and_pass()]] `INFERRED`
- [[test_register_valid_promo_code_accepted()]] `INFERRED`
- [[test_register_duplicate_email_conflict()]] `INFERRED`
- [[test_register_success()]] `INFERRED`
- [[test_register_sends_confirmation_email()]] `INFERRED`
- [[test_register_inactive_pass_type_400()]] `INFERRED`
- [[test_register_invalid_promo_code_400()]] `INFERRED`
- [[make_user_and_pass_type()]] `INFERRED`
- [[test_create_payment_applies_percent_discount()]] `INFERRED`
- [[test_create_payment_applies_fixed_discount()]] `INFERRED`
- [[test_create_payment_success_no_promo()]] `INFERRED`
- [[test_create_payment_invalid_promo_400()]] `INFERRED`
- [[test_list_pass_types_excludes_inactive()]] `INFERRED`
- [[test_pass_type_defaults()]] `INFERRED`

### contains
- [[referentials.py]] `EXTRACTED`

### inherits
- [[Base]] `EXTRACTED`

### uses
- [[Base]] `INFERRED`
- [[PromoCode]] `INFERRED`
- [[Payment]] `INFERRED`
- [[Ticket]] `INFERRED`
- [[Waitlist]] `INFERRED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*