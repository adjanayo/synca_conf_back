# Role

> God node · 20 connections · [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/rbac.py#L9)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as Role
    participant P1 as Base
    participant P2 as PassType
    participant P3 as PromoCode
    participant P4 as Payment
    participant P5 as Ticket
    participant P6 as make_pending_payment()
    participant P7 as make_ticket()
    participant P8 as Waitlist
    participant P9 as make_payment()
    participant P10 as make_payment()
    participant P11 as test_webhook_increments_promo_usage_count_on_completion()
    participant P12 as make_ticket_for()
    participant P13 as make_user_and_pass()
    participant P14 as test_register_valid_promo_code_accepted()
    participant P15 as test_register_duplicate_email_conflict()
    participant P16 as test_register_success()
    participant P17 as test_register_sends_confirmation_email()
    participant P18 as test_register_inactive_pass_type_400()
    participant P19 as test_register_invalid_promo_code_400()
    participant P20 as make_user_and_pass_type()
    participant P21 as test_create_payment_applies_percent_discount()
    participant P22 as test_create_payment_applies_fixed_discount()
    participant P23 as test_create_payment_success_no_promo()
    participant P24 as test_create_payment_invalid_promo_400()
    participant P25 as create_pass_type()
    participant P26 as test_list_pass_types_excludes_inactive()
    participant P27 as test_pass_type_defaults()
    participant P28 as test_create_payment_invalid_user_400()
    participant P29 as test_pass_type_read()
    participant P30 as User
    participant P31 as AdminUser
    participant P32 as PartnerLevel
    participant P33 as RolePermission
    participant P34 as Permission
    participant P35 as Speaker
    participant P36 as Partner
    participant P37 as FaqCategory
    participant P38 as Ambassador
    participant P39 as Exhibitor
    participant P40 as Day
    participant P41 as Session
    participant P42 as Faq
    participant P43 as ContactMessage
    participant P44 as UserProfile
    participant P45 as OtpCode
    participant P46 as CampaignWindow
    participant P47 as EventSettings
    participant P48 as HackathonTeam
    participant P49 as HackathonTeamMember
    participant P50 as AuditLog
    participant P51 as NewsletterSubscriber
    participant P52 as Login code for the participant OTP flow (app/api/participant_auth.py).      Sepa
    participant P53 as Run migrations in 'offline' mode.      This configures the context with just a U
    participant P54 as In this scenario we need to create an Engine     and associate a connection with
    participant P55 as Run migrations in 'online' mode.
    participant P56 as make_admin_with_permission()
    participant P57 as make_admin_with_permission()
    participant P58 as make_admin()
    participant P59 as make_admin_with_permission()
    participant P60 as make_admin_with_permission()
    participant P61 as make_admin_with_permission()
    participant P62 as make_admin()
    participant P63 as make_admin_with_role()
    participant P64 as make_admin_with_permissions()
    participant P65 as test_admin_endpoint_limited_to_30_per_minute()
    participant P66 as make_admin_with_role()
    participant P67 as make_admin()
    participant P68 as test_rbac_read()
    participant P69 as test_superadmin_can_update_role_permissions()
    participant P70 as test_non_superadmin_forbidden()
    participant P71 as test_unknown_permission_code_rejected()
    participant P72 as test_unauthenticated_rejected()
    P0->>+ P1: uses
    P1-->>- P0: return
    P1->>+ P2: uses
    P2-->>- P1: return
    P2->>+ P1: uses
    P1-->>- P2: return
    P2->>+ P3: uses
    P3-->>- P2: return
    P2->>+ P4: uses
    P4-->>- P2: return
    P2->>+ P5: uses
    P5-->>- P2: return
    P2->>+ P6: calls
    P6-->>- P2: return
    P2->>+ P7: calls
    P7-->>- P2: return
    P2->>+ P8: uses
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
    P2->>+ P19: calls
    P19-->>- P2: return
    P2->>+ P20: calls
    P20-->>- P2: return
    P2->>+ P21: calls
    P21-->>- P2: return
    P2->>+ P22: calls
    P22-->>- P2: return
    P2->>+ P23: calls
    P23-->>- P2: return
    P2->>+ P24: calls
    P24-->>- P2: return
    P2->>+ P25: calls
    P25-->>- P2: return
    P2->>+ P26: calls
    P26-->>- P2: return
    P2->>+ P27: calls
    P27-->>- P2: return
    P2->>+ P28: calls
    P28-->>- P2: return
    P2->>+ P29: calls
    P29-->>- P2: return
    P1->>+ P30: uses
    P30-->>- P1: return
    P1->>+ P0: uses
    P0-->>- P1: return
    P1->>+ P31: uses
    P31-->>- P1: return
    P1->>+ P3: uses
    P3-->>- P1: return
    P1->>+ P4: uses
    P4-->>- P1: return
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
    P1->>+ P5: uses
    P5-->>- P1: return
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
    P1->>+ P8: uses
    P8-->>- P1: return
    P1->>+ P44: uses
    P44-->>- P1: return
    P1->>+ P45: uses
    P45-->>- P1: return
    P1->>+ P46: uses
    P46-->>- P1: return
    P1->>+ P47: uses
    P47-->>- P1: return
    P1->>+ P48: uses
    P48-->>- P1: return
    P1->>+ P49: uses
    P49-->>- P1: return
    P1->>+ P50: uses
    P50-->>- P1: return
    P1->>+ P51: uses
    P51-->>- P1: return
    P1->>+ P52: uses
    P52-->>- P1: return
    P1->>+ P53: uses
    P53-->>- P1: return
    P1->>+ P54: uses
    P54-->>- P1: return
    P1->>+ P55: uses
    P55-->>- P1: return
    P0->>+ P56: calls
    P56-->>- P0: return
    P0->>+ P57: calls
    P57-->>- P0: return
    P0->>+ P58: calls
    P58-->>- P0: return
    P0->>+ P59: calls
    P59-->>- P0: return
    P0->>+ P60: calls
    P60-->>- P0: return
    P0->>+ P61: calls
    P61-->>- P0: return
    P0->>+ P62: calls
    P62-->>- P0: return
    P0->>+ P63: calls
    P63-->>- P0: return
    P0->>+ P64: calls
    P64-->>- P0: return
    P0->>+ P65: calls
    P65-->>- P0: return
    P0->>+ P66: calls
    P66-->>- P0: return
    P0->>+ P67: calls
    P67-->>- P0: return
    P0->>+ P68: calls
    P68-->>- P0: return
    P0->>+ P69: calls
    P69-->>- P0: return
    P0->>+ P70: calls
    P70-->>- P0: return
    P0->>+ P71: calls
    P71-->>- P0: return
    P0->>+ P72: calls
    P72-->>- P0: return
```

## Connections by Relation

### calls
- [[make_admin_with_permission()]] `INFERRED`
- [[make_admin_with_permission()]] `INFERRED`
- [[make_admin()]] `INFERRED`
- [[make_admin_with_permission()]] `INFERRED`
- [[make_admin_with_permission()]] `INFERRED`
- [[make_admin_with_permission()]] `INFERRED`
- [[make_admin()]] `INFERRED`
- [[make_admin_with_role()]] `INFERRED`
- [[make_admin_with_permissions()]] `INFERRED`
- [[test_admin_endpoint_limited_to_30_per_minute()]] `INFERRED`
- [[make_admin_with_role()]] `INFERRED`
- [[make_admin()]] `INFERRED`
- [[test_rbac_read()]] `INFERRED`
- [[test_superadmin_can_update_role_permissions()]] `INFERRED`
- [[test_non_superadmin_forbidden()]] `INFERRED`
- [[test_unknown_permission_code_rejected()]] `INFERRED`
- [[test_unauthenticated_rejected()]] `INFERRED`

### contains
- [[rbac.py]] `EXTRACTED`

### inherits
- [[Base]] `EXTRACTED`

### uses
- [[Base]] `INFERRED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*