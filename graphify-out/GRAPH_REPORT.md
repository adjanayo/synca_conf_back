# Graph Report - /Users/kodjododjango/Downloads/dev_projects/synca_conf_back  (2026-09-02)

## Corpus Check
- 158 files · ~151,770 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 784 nodes · 1346 edges · 59 communities detected
- Extraction: 69% EXTRACTED · 31% INFERRED · 0% AMBIGUOUS · INFERRED: 421 edges (avg confidence: 0.76)
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

## God Nodes (most connected - your core abstractions)
1. `create_access_token()` - 46 edges
2. `Base` - 31 edges
3. `PassType` - 29 edges
4. `User` - 20 edges
5. `Role` - 20 edges
6. `AdminUser` - 18 edges
7. `make_admin_with_permission()` - 18 edges
8. `get_settings()` - 17 edges
9. `PromoCode` - 17 edges
10. `Payment` - 16 edges

## Surprising Connections (you probably didn't know these)
- `PassType` --calls--> `test_pass_type_defaults()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_referentials.py
- `PassType` --calls--> `test_pass_type_read()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_schemas.py
- `PartnerLevel` --calls--> `test_partner_level_read()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_schemas.py
- `get_settings()` --calls--> `build_admin_auth()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/config.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/admin/auth.py
- `get_settings()` --calls--> `main()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/config.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/cli/create_admin.py

## Communities

### Community 0 - "Community 0"

Cohesion: 0.03
Nodes (61): AmbassadorStatusUpdate, ExhibitorStatusUpdate, PartnerStatusUpdate, SpeakerStatusUpdate, list_registrations(), RegistrationRead, AdminStatsRead, get_admin_stats() (+53 more)

### Community 1 - "Community 1"

Cohesion: 0.06
Nodes (61): create_access_token(), AdminUser, get_current_admin(), Permission, require_permission(), Role, RolePermission, make_admin_with_permission() (+53 more)

### Community 2 - "Community 2"

Cohesion: 0.05
Nodes (40): AuditLog, Base, CampaignWindow, ContactMessage, Faq, Base, DeclarativeBase, Run migrations in 'offline' mode.      This configures the context with just a U (+32 more)

### Community 3 - "Community 3"

Cohesion: 0.06
Nodes (42): Ambassador, Exhibitor, Partner, Speaker, application_received_email(), otp_login_email(), TODO.md: HTML email templates.  Table-based, inline-CSS layout (the only markup, registration_confirmed_email() (+34 more)

### Community 4 - "Community 4"

Cohesion: 0.06
Nodes (44): AdminAuth, build_admin_auth(), login(), SQLAdmin login backed by the same admin_users/Argon2id/lockout path     as POST, AccountLockedError, authenticate_admin(), create_participant_token(), create_refresh_token() (+36 more)

### Community 5 - "Community 5"

Cohesion: 0.08
Nodes (40): join_waitlist(), Payment, PromoCode, Ticket, Waitlist, PassType, make_admin_with_permission(), make_user_and_pass_type() (+32 more)

### Community 6 - "Community 6"

Cohesion: 0.07
Nodes (29): downgrade(), encrypt users phone_whatsapp and special_needs (PII 7.8)  Revision ID: d7d5f8910, upgrade(), BaseSettings, get_settings(), Settings, db_session(), EncryptedString (+21 more)

### Community 7 - "Community 7"

Cohesion: 0.08
Nodes (23): update_ambassador_status(), create_payment(), payment_webhook(), validate_promo(), compute_discounted_amount(), generate_ambassador_promo_code(), get_valid_promo_code(), Create and attach a promo code to a newly-accepted ambassador.      No usage_lim (+15 more)

### Community 8 - "Community 8"

Cohesion: 0.09
Nodes (24): ParticipantTokenOut, main(), _generate_code(), InvalidOtpError, Create + email a login code if the address matches a verified account.      Sile, Consume the most recent unexpired, unconsumed code for this email.      Every fa, request_otp(), verify_otp() (+16 more)

### Community 9 - "Community 9"

Cohesion: 0.13
Nodes (21): make_user(), test_null_special_needs_stays_null(), test_orm_read_returns_plaintext(), test_raw_db_row_is_not_plaintext(), make_pending_payment(), stripe_signature(), test_webhook_completes_payment_and_creates_ticket(), test_webhook_failed_status_marks_payment_failed() (+13 more)

### Community 10 - "Community 10"

Cohesion: 0.14
Nodes (15): Send a transactional email, or log it in dev.      Without RESEND_API_KEY config, send_email(), _mock_response(), test_send_email_calls_resend_when_key_configured(), test_send_email_logs_in_dev_without_key(), test_send_email_raises_on_resend_error(), make_ticket(), test_finalize_ticket_is_idempotent_when_already_finalized() (+7 more)

### Community 11 - "Community 11"

Cohesion: 0.26
Nodes (7): ModelView, AmbassadorAdmin, ContactMessageAdmin, ExhibitorAdmin, _has_permission(), PartnerAdmin, SpeakerAdmin

### Community 12 - "Community 12"

Cohesion: 0.27
Nodes (8): make_verified_user(), test_request_otp_only_creates_row_for_known_verified_email(), test_request_otp_rate_limited_after_three_per_15_minutes(), test_request_otp_same_generic_response_known_and_unknown_email(), test_verify_otp_cannot_be_reused(), test_verify_otp_expired_code_returns_401(), test_verify_otp_success_grants_access_to_user_me(), test_verify_otp_wrong_code_returns_401()

### Community 13 - "Community 13"

Cohesion: 0.29
Nodes (7): make_ticket_for(), make_user(), test_delete_me_anonymizes_and_revokes_token(), test_delete_me_token_cannot_be_reused(), test_get_me_rejects_invalid_token(), test_get_me_returns_own_data(), test_get_my_tickets_returns_only_own_tickets()

### Community 14 - "Community 14"

Cohesion: 0.33
Nodes (8): contact(), Verify a reCAPTCHA v3 token, raising 400 on failure.      Skipped entirely when, verify_recaptcha(), _mock_response(), test_verify_recaptcha_accepts_good_score(), test_verify_recaptcha_rejects_low_score(), test_verify_recaptcha_rejects_unsuccessful_response(), test_verify_recaptcha_skips_when_no_secret_configured()

### Community 15 - "Community 15"

Cohesion: 0.49
Nodes (8): form_fields(), make_png_bytes(), open_call_for_speaker(), test_speaker_apply_closed_window_forbidden(), test_speaker_apply_missing_gdpr_consent_422(), test_speaker_apply_oversized_photo_rejected_400(), test_speaker_apply_rejects_fake_image(), test_speaker_apply_success()

### Community 16 - "Community 16"

Cohesion: 0.22
Nodes (0): 

### Community 17 - "Community 17"

Cohesion: 0.47
Nodes (7): open_call_for_ambassador(), payload(), test_ambassador_apply_closed_window_forbidden(), test_ambassador_apply_empty_channels_422(), test_ambassador_apply_missing_gdpr_consent_422(), test_ambassador_apply_success(), test_ambassador_apply_under_age_422()

### Community 18 - "Community 18"

Cohesion: 0.44
Nodes (7): require_open_campaign(), set_window(), test_missing_window_forbidden(), test_open_window_allows(), test_window_already_closed_forbidden(), test_window_deactivated_forbidden_even_within_dates(), test_window_not_yet_started_forbidden()

### Community 19 - "Community 19"

Cohesion: 0.29
Nodes (3): Pagination, pagination_params(), test_pagination_custom_values()

### Community 20 - "Community 20"

Cohesion: 0.5
Nodes (6): open_call_for_exhibitor(), payload(), test_exhibitor_apply_closed_window_forbidden(), test_exhibitor_apply_invalid_reps_count_422(), test_exhibitor_apply_rules_not_accepted_422(), test_exhibitor_apply_success()

### Community 21 - "Community 21"

Cohesion: 0.47
Nodes (3): _make_test_app(), test_common_headers_always_present(), test_hsts_only_sent_when_enabled()

### Community 22 - "Community 22"

Cohesion: 0.4
Nodes (2): BaseHTTPMiddleware, SecurityHeadersMiddleware

### Community 23 - "Community 23"

Cohesion: 0.7
Nodes (4): _csv_response(), export_payments_csv(), export_registrations_csv(), _sanitize_csv_cell()

### Community 24 - "Community 24"

Cohesion: 0.4
Nodes (0): 

### Community 25 - "Community 25"

Cohesion: 0.4
Nodes (0): 

### Community 26 - "Community 26"

Cohesion: 0.4
Nodes (0): 

### Community 27 - "Community 27"

Cohesion: 0.5
Nodes (1): admin_users lockout columns  Revision ID: 5a30c6996bc8 Revises: 2c2d07493eb5 Cre

### Community 28 - "Community 28"

Cohesion: 0.5
Nodes (1): referentials (days, pass_types, partner_levels, faq_categories)  Revision ID: e1

### Community 29 - "Community 29"

Cohesion: 0.5
Nodes (1): newsletter_subscribers table  Revision ID: c375ad4fa2bb Revises: 866edbae2931 Cr

### Community 30 - "Community 30"

Cohesion: 0.5
Nodes (1): promo_codes, payments, tickets, waitlist  Revision ID: a3f8aaae2d58 Revises: 9dd

### Community 31 - "Community 31"

Cohesion: 0.5
Nodes (1): otp_codes table (participant OTP login)  Revision ID: 75418b933d4f Revises: d7d5

### Community 32 - "Community 32"

Cohesion: 0.5
Nodes (1): users and user_profiles  Revision ID: 86b8fb32827d Revises: e15b192c81f5 Create

### Community 33 - "Community 33"

Cohesion: 0.5
Nodes (1): campaign_windows  Revision ID: 2c2d07493eb5 Revises: a9e9ba5fc6f7 Create Date: 2

### Community 34 - "Community 34"

Cohesion: 0.5
Nodes (1): rbac (roles, permissions, role_permissions, admin_users)  Revision ID: a9e9ba5fc

### Community 35 - "Community 35"

Cohesion: 0.5
Nodes (1): faqs, contact_messages  Revision ID: 3f306df50f16 Revises: 7b6712058249 Create D

### Community 36 - "Community 36"

Cohesion: 0.5
Nodes (1): initial (empty)  Revision ID: 5e965f30353e Revises:  Create Date: 2026-08-25 21:

### Community 37 - "Community 37"

Cohesion: 0.5
Nodes (1): speakers, ambassadors, partners, exhibitors  Revision ID: 7b6712058249 Revises:

### Community 38 - "Community 38"

Cohesion: 0.5
Nodes (1): audit_logs table  Revision ID: 866edbae2931 Revises: 5a30c6996bc8 Create Date: 2

### Community 39 - "Community 39"

Cohesion: 0.5
Nodes (1): sessions  Revision ID: 9dd893772cc0 Revises: 86b8fb32827d Create Date: 2026-08-2

### Community 40 - "Community 40"

Cohesion: 0.67
Nodes (0): 

### Community 41 - "Community 41"

Cohesion: 0.67
Nodes (0): 

### Community 42 - "Community 42"

Cohesion: 0.67
Nodes (0): 

### Community 43 - "Community 43"

Cohesion: 0.67
Nodes (0): 

### Community 44 - "Community 44"

Cohesion: 0.67
Nodes (0): 

### Community 45 - "Community 45"

Cohesion: 0.67
Nodes (0): 

### Community 46 - "Community 46"

Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"

Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"

Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"

Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"

Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"

Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"

Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"

Cohesion: 1.0
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
Nodes (1): Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background

## Knowledge Gaps
- **30 isolated node(s):** `Validate a multipart form's non-file fields against a Pydantic model.      Works`, `Application-layer encryption for genuinely sensitive PII (7.8).      Not for fie`, `Verify admin credentials, enforcing the account-lockout policy.      Always take`, `Issued after a successful OTP verify (app/api/participant_auth.py).      Distinc`, `Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 46`** (2 nodes): `list_audit_logs()`, `admin_audit.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (2 nodes): `test_health()`, `test_health.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `rate_limit.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.