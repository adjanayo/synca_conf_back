# Graph Report - /Users/kodjododjango/Downloads/dev_projects/synca_conf_back  (2026-09-02)

## Corpus Check
- 168 files · ~162,286 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 847 nodes · 1433 edges · 70 communities detected
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 436 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]

## God Nodes (most connected - your core abstractions)
1. `create_access_token()` - 46 edges
2. `Base` - 32 edges
3. `PassType` - 30 edges
4. `User` - 20 edges
5. `Role` - 20 edges
6. `AdminUser` - 19 edges
7. `make_admin_with_permission()` - 18 edges
8. `get_settings()` - 17 edges
9. `PromoCode` - 17 edges
10. `Payment` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Base` --uses--> `Run migrations in 'offline' mode.      This configures the context with just a U`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/database.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/alembic/env.py
- `Base` --uses--> `In this scenario we need to create an Engine     and associate a connection with`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/database.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/alembic/env.py
- `Base` --uses--> `Run migrations in 'online' mode.`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/database.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/alembic/env.py
- `PassType` --calls--> `test_pass_type_defaults()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_referentials.py
- `PassType` --calls--> `test_pass_type_read()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_schemas.py

## Communities

### Community 0 - "Community 0"

Cohesion: 0.03
Nodes (78): AmbassadorAdminCreate, AmbassadorStatusUpdate, ExhibitorAdminCreate, ExhibitorStatusUpdate, PartnerAdminCreate, PartnerStatusUpdate, SpeakerAdminCreate, SpeakerStatusUpdate (+70 more)

### Community 1 - "Community 1"

Cohesion: 0.03
Nodes (63): create_exhibitor_admin(), create_partner_admin(), create_speaker_admin(), create_day(), create_session(), Ambassador, Exhibitor, Partner (+55 more)

### Community 2 - "Community 2"

Cohesion: 0.06
Nodes (61): create_access_token(), AdminUser, Permission, Role, RolePermission, make_admin_with_permission(), make_ambassador(), make_exhibitor() (+53 more)

### Community 3 - "Community 3"

Cohesion: 0.06
Nodes (47): create_pass_type(), join_waitlist(), Payment, PromoCode, Ticket, Waitlist, PassType, open_ticketing() (+39 more)

### Community 4 - "Community 4"

Cohesion: 0.06
Nodes (43): AdminAuth, build_admin_auth(), SQLAdmin login backed by the same admin_users/Argon2id/lockout path     as POST, AccountDisabledError, AccountLockedError, authenticate_admin(), create_participant_token(), create_refresh_token() (+35 more)

### Community 5 - "Community 5"

Cohesion: 0.07
Nodes (23): downgrade(), encrypt users phone_whatsapp and special_needs (PII 7.8)  Revision ID: d7d5f8910, upgrade(), BaseSettings, get_settings(), Settings, db_session(), EncryptedString (+15 more)

### Community 6 - "Community 6"

Cohesion: 0.11
Nodes (28): application_received_email(), otp_login_email(), TODO.md: HTML email templates.  Table-based, inline-CSS layout (the only markup, registration_confirmed_email(), _render(), ticket_delivered_email(), apply_as_exhibitor(), apply_as_partner() (+20 more)

### Community 7 - "Community 7"

Cohesion: 0.12
Nodes (22): create_admin_user(), list_admin_users(), _to_read(), update_admin_user(), ParticipantTokenOut, main(), _generate_code(), InvalidOtpError (+14 more)

### Community 8 - "Community 8"

Cohesion: 0.13
Nodes (18): make_user(), test_null_special_needs_stays_null(), test_orm_read_returns_plaintext(), test_raw_db_row_is_not_plaintext(), make_verified_user(), test_request_otp_only_creates_row_for_known_verified_email(), test_request_otp_rate_limited_after_three_per_15_minutes(), test_request_otp_same_generic_response_known_and_unknown_email() (+10 more)

### Community 9 - "Community 9"

Cohesion: 0.14
Nodes (15): Send a transactional email, or log it in dev.      Without RESEND_API_KEY config, send_email(), _mock_response(), test_send_email_calls_resend_when_key_configured(), test_send_email_logs_in_dev_without_key(), test_send_email_raises_on_resend_error(), make_ticket(), test_finalize_ticket_is_idempotent_when_already_finalized() (+7 more)

### Community 10 - "Community 10"

Cohesion: 0.17
Nodes (16): payment_webhook(), test_verify_hmac_signature_accepts_valid(), test_verify_hmac_signature_rejects_empty_secret_even_with_matching_forged_signature(), test_verify_hmac_signature_rejects_invalid(), test_verify_stripe_signature_accepts_valid(), test_verify_stripe_signature_rejects_bad_signature(), test_verify_stripe_signature_rejects_empty_secret_even_with_matching_forged_signature(), test_verify_stripe_signature_rejects_expired_timestamp() (+8 more)

### Community 11 - "Community 11"

Cohesion: 0.13
Nodes (8): create_ambassador_admin(), update_ambassador_status(), create_payment(), validate_promo(), compute_discounted_amount(), generate_ambassador_promo_code(), get_valid_promo_code(), Create and attach a promo code to a newly-accepted ambassador.      No usage_lim

### Community 12 - "Community 12"

Cohesion: 0.26
Nodes (7): ModelView, AmbassadorAdmin, ContactMessageAdmin, ExhibitorAdmin, _has_permission(), PartnerAdmin, SpeakerAdmin

### Community 13 - "Community 13"

Cohesion: 0.29
Nodes (7): make_ticket_for(), make_user(), test_delete_me_anonymizes_and_revokes_token(), test_delete_me_token_cannot_be_reused(), test_get_me_rejects_invalid_token(), test_get_me_returns_own_data(), test_get_my_tickets_returns_only_own_tickets()

### Community 14 - "Community 14"

Cohesion: 0.31
Nodes (6): grant_permission(), make_admin(), test_any_authenticated_admin_can_read_contact_messages(), test_login_success_grants_access_to_a_permitted_view(), test_login_wrong_password_is_rejected(), test_role_without_permission_gets_403_on_gated_view()

### Community 15 - "Community 15"

Cohesion: 0.36
Nodes (8): get_current_admin(), require_permission(), make_admin_with_role(), test_get_current_admin_invalid_token_raises_401(), test_get_current_admin_missing_token_raises_401(), test_get_current_admin_valid_token(), test_require_permission_denied_returns_403(), test_require_permission_granted()

### Community 16 - "Community 16"

Cohesion: 0.49
Nodes (8): form_fields(), make_png_bytes(), open_call_for_speaker(), test_speaker_apply_closed_window_forbidden(), test_speaker_apply_missing_gdpr_consent_422(), test_speaker_apply_oversized_photo_rejected_400(), test_speaker_apply_rejects_fake_image(), test_speaker_apply_success()

### Community 17 - "Community 17"

Cohesion: 0.22
Nodes (0): 

### Community 18 - "Community 18"

Cohesion: 0.47
Nodes (7): open_call_for_ambassador(), payload(), test_ambassador_apply_closed_window_forbidden(), test_ambassador_apply_empty_channels_422(), test_ambassador_apply_missing_gdpr_consent_422(), test_ambassador_apply_success(), test_ambassador_apply_under_age_422()

### Community 19 - "Community 19"

Cohesion: 0.44
Nodes (7): require_open_campaign(), set_window(), test_missing_window_forbidden(), test_open_window_allows(), test_window_already_closed_forbidden(), test_window_deactivated_forbidden_even_within_dates(), test_window_not_yet_started_forbidden()

### Community 20 - "Community 20"

Cohesion: 0.29
Nodes (3): Pagination, pagination_params(), test_pagination_custom_values()

### Community 21 - "Community 21"

Cohesion: 0.5
Nodes (6): open_call_for_exhibitor(), payload(), test_exhibitor_apply_closed_window_forbidden(), test_exhibitor_apply_invalid_reps_count_422(), test_exhibitor_apply_rules_not_accepted_422(), test_exhibitor_apply_success()

### Community 22 - "Community 22"

Cohesion: 0.29
Nodes (6): Run migrations in 'offline' mode.      This configures the context with just a U, In this scenario we need to create an Engine     and associate a connection with, Run migrations in 'online' mode., run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 23 - "Community 23"

Cohesion: 0.47
Nodes (3): _make_test_app(), test_common_headers_always_present(), test_hsts_only_sent_when_enabled()

### Community 24 - "Community 24"

Cohesion: 0.4
Nodes (2): BaseHTTPMiddleware, SecurityHeadersMiddleware

### Community 25 - "Community 25"

Cohesion: 0.5
Nodes (2): make_exhibitor(), test_exhibitors_excludes_private()

### Community 26 - "Community 26"

Cohesion: 0.7
Nodes (4): _csv_response(), export_payments_csv(), export_registrations_csv(), _sanitize_csv_cell()

### Community 27 - "Community 27"

Cohesion: 0.4
Nodes (0): 

### Community 28 - "Community 28"

Cohesion: 0.4
Nodes (0): 

### Community 29 - "Community 29"

Cohesion: 0.4
Nodes (0): 

### Community 30 - "Community 30"

Cohesion: 0.5
Nodes (1): event_settings, pass_types & sessions admin permissions  Revision ID: 547ad7a3ad

### Community 31 - "Community 31"

Cohesion: 0.5
Nodes (1): admin_users lockout columns  Revision ID: 5a30c6996bc8 Revises: 2c2d07493eb5 Cre

### Community 32 - "Community 32"

Cohesion: 0.5
Nodes (1): referentials (days, pass_types, partner_levels, faq_categories)  Revision ID: e1

### Community 33 - "Community 33"

Cohesion: 0.5
Nodes (1): newsletter_subscribers table  Revision ID: c375ad4fa2bb Revises: 866edbae2931 Cr

### Community 34 - "Community 34"

Cohesion: 0.5
Nodes (1): promo_codes, payments, tickets, waitlist  Revision ID: a3f8aaae2d58 Revises: 9dd

### Community 35 - "Community 35"

Cohesion: 0.5
Nodes (1): waitlist.view permission  Revision ID: 80348b151263 Revises: 547ad7a3ad02 Create

### Community 36 - "Community 36"

Cohesion: 0.5
Nodes (1): admin_users.status column + admin_users.manage permission  Revision ID: 9c1e2f4a

### Community 37 - "Community 37"

Cohesion: 0.5
Nodes (1): campaign_window_event_key  Revision ID: b1c2d3e4f5a6 Revises: 75418b933d4f Creat

### Community 38 - "Community 38"

Cohesion: 0.5
Nodes (1): otp_codes table (participant OTP login)  Revision ID: 75418b933d4f Revises: d7d5

### Community 39 - "Community 39"

Cohesion: 0.5
Nodes (1): users and user_profiles  Revision ID: 86b8fb32827d Revises: e15b192c81f5 Create

### Community 40 - "Community 40"

Cohesion: 0.5
Nodes (1): campaign_windows  Revision ID: 2c2d07493eb5 Revises: a9e9ba5fc6f7 Create Date: 2

### Community 41 - "Community 41"

Cohesion: 0.5
Nodes (1): rbac (roles, permissions, role_permissions, admin_users)  Revision ID: a9e9ba5fc

### Community 42 - "Community 42"

Cohesion: 0.5
Nodes (1): faqs, contact_messages  Revision ID: 3f306df50f16 Revises: 7b6712058249 Create D

### Community 43 - "Community 43"

Cohesion: 0.5
Nodes (1): initial (empty)  Revision ID: 5e965f30353e Revises:  Create Date: 2026-08-25 21:

### Community 44 - "Community 44"

Cohesion: 0.5
Nodes (1): speakers, ambassadors, partners, exhibitors  Revision ID: 7b6712058249 Revises:

### Community 45 - "Community 45"

Cohesion: 0.5
Nodes (1): audit_logs table  Revision ID: 866edbae2931 Revises: 5a30c6996bc8 Create Date: 2

### Community 46 - "Community 46"

Cohesion: 0.5
Nodes (1): sessions  Revision ID: 9dd893772cc0 Revises: 86b8fb32827d Create Date: 2026-08-2

### Community 47 - "Community 47"

Cohesion: 0.67
Nodes (0): 

### Community 48 - "Community 48"

Cohesion: 0.67
Nodes (0): 

### Community 49 - "Community 49"

Cohesion: 0.67
Nodes (0): 

### Community 50 - "Community 50"

Cohesion: 0.67
Nodes (0): 

### Community 51 - "Community 51"

Cohesion: 0.67
Nodes (0): 

### Community 52 - "Community 52"

Cohesion: 0.67
Nodes (0): 

### Community 53 - "Community 53"

Cohesion: 0.67
Nodes (0): 

### Community 54 - "Community 54"

Cohesion: 1.0
Nodes (0): 

### Community 55 - "Community 55"

Cohesion: 1.0
Nodes (0): 

### Community 56 - "Community 56"

Cohesion: 1.0
Nodes (0): 

### Community 57 - "Community 57"

Cohesion: 1.0
Nodes (0): 

### Community 58 - "Community 58"

Cohesion: 1.0
Nodes (0): 

### Community 59 - "Community 59"

Cohesion: 1.0
Nodes (0): 

### Community 60 - "Community 60"

Cohesion: 1.0
Nodes (0): 

### Community 61 - "Community 61"

Cohesion: 1.0
Nodes (0): 

### Community 62 - "Community 62"

Cohesion: 1.0
Nodes (0): 

### Community 63 - "Community 63"

Cohesion: 1.0
Nodes (0): 

### Community 64 - "Community 64"

Cohesion: 1.0
Nodes (0): 

### Community 65 - "Community 65"

Cohesion: 1.0
Nodes (0): 

### Community 66 - "Community 66"

Cohesion: 1.0
Nodes (0): 

### Community 67 - "Community 67"

Cohesion: 1.0
Nodes (1): Verify admin credentials, enforcing the account-lockout policy.      Always take

### Community 68 - "Community 68"

Cohesion: 1.0
Nodes (1): Issued after a successful OTP verify (app/api/participant_auth.py).      Distinc

### Community 69 - "Community 69"

Cohesion: 1.0
Nodes (1): Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background

## Knowledge Gaps
- **36 isolated node(s):** `Validate a multipart form's non-file fields against a Pydantic model.      Works`, `Application-layer encryption for genuinely sensitive PII (7.8).      Not for fie`, `Verify admin credentials, enforcing the account-lockout policy.      Always take`, `Issued after a successful OTP verify (app/api/participant_auth.py).      Distinc`, `Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 54`** (2 nodes): `list_audit_logs()`, `admin_audit.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (2 nodes): `list_waitlist()`, `admin_waitlist.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (2 nodes): `test_health()`, `test_health.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `rate_limit.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Verify admin credentials, enforcing the account-lockout policy.      Always take`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Issued after a successful OTP verify (app/api/participant_auth.py).      Distinc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.