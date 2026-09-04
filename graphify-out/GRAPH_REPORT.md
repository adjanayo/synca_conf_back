# Graph Report - /Users/kodjododjango/Downloads/dev_projects/synca_conf_back  (2026-09-04)

## Corpus Check
- 185 files · ~190,421 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 998 nodes · 1663 edges · 78 communities detected
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 472 edges (avg confidence: 0.75)
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
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]

## God Nodes (most connected - your core abstractions)
1. `create_access_token()` - 46 edges
2. `Base` - 38 edges
3. `PassType` - 30 edges
4. `User` - 20 edges
5. `Role` - 20 edges
6. `AdminUser` - 19 edges
7. `PromoCode` - 18 edges
8. `upload_file()` - 18 edges
9. `make_admin_with_permission()` - 18 edges
10. `get_settings()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `CampaignWindow` --uses--> `Rappels récurrents waitlist (voir DEVLOG.md front, phase J3 suite).  Pas de cron`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/campaign.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/waitlist_reminder.py
- `PassContent` --calls--> `create_pass_content()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_pass_types.py
- `PassType` --calls--> `test_pass_type_defaults()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_referentials.py
- `PassType` --calls--> `test_pass_type_read()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_schemas.py
- `PartnerLevel` --calls--> `test_partner_level_read()`  [INFERRED]
  /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/models/referentials.py → /Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_schemas.py

## Communities

### Community 0 - "Community 0"

Cohesion: 0.02
Nodes (106): AmbassadorAdminCreate, AmbassadorStatusUpdate, ExhibitorAdminCreate, ExhibitorStatusUpdate, PartnerAdminCreate, PartnerStatusUpdate, SpeakerAdminCreate, SpeakerStatusUpdate (+98 more)

### Community 1 - "Community 1"

Cohesion: 0.04
Nodes (55): create_partner_benefit(), AuditLog, Base, CampaignWindow, Base, DeclarativeBase, Run migrations in 'offline' mode.      This configures the context with just a U, In this scenario we need to create an Engine     and associate a connection with (+47 more)

### Community 2 - "Community 2"

Cohesion: 0.05
Nodes (54): create_promo_code(), join_waitlist(), Payment, PromoCode, Ticket, Waitlist, PassType, open_ticketing() (+46 more)

### Community 3 - "Community 3"

Cohesion: 0.04
Nodes (32): create_faq(), create_faq_category(), create_day(), create_session(), ContactMessage, Faq, contact(), Pagination (+24 more)

### Community 4 - "Community 4"

Cohesion: 0.05
Nodes (46): create_ambassador_admin(), create_exhibitor_admin(), create_partner_admin(), create_speaker_admin(), update_ambassador_status(), Ambassador, Exhibitor, Partner (+38 more)

### Community 5 - "Community 5"

Cohesion: 0.06
Nodes (43): AdminAuth, build_admin_auth(), SQLAdmin login backed by the same admin_users/Argon2id/lockout path     as POST, AccountDisabledError, AccountLockedError, authenticate_admin(), create_participant_token(), create_refresh_token() (+35 more)

### Community 6 - "Community 6"

Cohesion: 0.11
Nodes (39): create_access_token(), make_admin_with_permission(), make_ambassador(), make_exhibitor(), make_partner(), make_speaker(), test_ambassador_accepted(), test_ambassador_accepted_twice_does_not_regenerate_promo_code() (+31 more)

### Community 7 - "Community 7"

Cohesion: 0.07
Nodes (22): downgrade(), encrypt users phone_whatsapp and special_needs (PII 7.8)  Revision ID: d7d5f8910, upgrade(), BaseSettings, get_settings(), Settings, db_session(), EncryptedString (+14 more)

### Community 8 - "Community 8"

Cohesion: 0.1
Nodes (26): create_team(), create_team_member(), delete_team(), _get_team_or_404(), update_team(), update_team_member(), HackathonTeam, HackathonTeamMember (+18 more)

### Community 9 - "Community 9"

Cohesion: 0.08
Nodes (20): _is_open(), _notify_waitlist(), update_campaign_window(), BaseHTTPMiddleware, Send a transactional email, or log it in dev.      Without RESEND_API_KEY config, send_email(), lifespan(), Pas de cron dans le projet : boucle asyncio en tâche de fond,     voir app/servi (+12 more)

### Community 10 - "Community 10"

Cohesion: 0.12
Nodes (22): create_admin_user(), list_admin_users(), _to_read(), update_admin_user(), ParticipantTokenOut, main(), _generate_code(), InvalidOtpError (+14 more)

### Community 11 - "Community 11"

Cohesion: 0.13
Nodes (18): make_user(), test_null_special_needs_stays_null(), test_orm_read_returns_plaintext(), test_raw_db_row_is_not_plaintext(), make_verified_user(), test_request_otp_only_creates_row_for_known_verified_email(), test_request_otp_rate_limited_after_three_per_15_minutes(), test_request_otp_same_generic_response_known_and_unknown_email() (+10 more)

### Community 12 - "Community 12"

Cohesion: 0.12
Nodes (20): create_payment(), payment_webhook(), validate_promo(), compute_discounted_amount(), get_valid_promo_code(), test_verify_hmac_signature_accepts_valid(), test_verify_hmac_signature_rejects_empty_secret_even_with_matching_forged_signature(), test_verify_hmac_signature_rejects_invalid() (+12 more)

### Community 13 - "Community 13"

Cohesion: 0.12
Nodes (0): 

### Community 14 - "Community 14"

Cohesion: 0.26
Nodes (7): ModelView, AmbassadorAdmin, ContactMessageAdmin, ExhibitorAdmin, _has_permission(), PartnerAdmin, SpeakerAdmin

### Community 15 - "Community 15"

Cohesion: 0.23
Nodes (9): make_ticket(), test_finalize_ticket_is_idempotent_when_already_finalized(), test_finalize_ticket_noops_on_missing_ticket(), test_finalize_ticket_sets_pdf_url_and_sends_email(), finalize_ticket(), Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background, generate_and_upload_ticket_pdf(), _render_qr_png() (+1 more)

### Community 16 - "Community 16"

Cohesion: 0.27
Nodes (6): create_pass_content(), create_pass_type(), delete_pass_type(), _get_pass_type_or_404(), _resolve_contents(), update_pass_type()

### Community 17 - "Community 17"

Cohesion: 0.47
Nodes (9): form_fields(), make_png_bytes(), open_call_for_ambassador(), test_ambassador_apply_closed_window_forbidden(), test_ambassador_apply_empty_channels_422(), test_ambassador_apply_missing_gdpr_consent_422(), test_ambassador_apply_rejects_fake_image(), test_ambassador_apply_success() (+1 more)

### Community 18 - "Community 18"

Cohesion: 0.4
Nodes (9): form_fields(), make_png_bytes(), open_call_for_exhibitor(), test_exhibitor_apply_closed_window_forbidden(), test_exhibitor_apply_invalid_reps_count_422(), test_exhibitor_apply_rejects_fake_image(), test_exhibitor_apply_rules_not_accepted_422(), test_exhibitor_apply_success_with_visuals() (+1 more)

### Community 19 - "Community 19"

Cohesion: 0.31
Nodes (5): create_partner_level(), delete_partner_level(), _get_level_or_404(), _resolve_benefits(), update_partner_level()

### Community 20 - "Community 20"

Cohesion: 0.49
Nodes (8): form_fields(), make_png_bytes(), open_call_for_speaker(), test_speaker_apply_closed_window_forbidden(), test_speaker_apply_missing_gdpr_consent_422(), test_speaker_apply_oversized_photo_rejected_400(), test_speaker_apply_rejects_fake_image(), test_speaker_apply_success()

### Community 21 - "Community 21"

Cohesion: 0.44
Nodes (7): require_open_campaign(), set_window(), test_missing_window_forbidden(), test_open_window_allows(), test_window_already_closed_forbidden(), test_window_deactivated_forbidden_even_within_dates(), test_window_not_yet_started_forbidden()

### Community 22 - "Community 22"

Cohesion: 0.36
Nodes (4): make_speaker(), test_get_speaker_detail(), test_get_speaker_detail_404_when_not_public(), test_speakers_filter_by_theme_and_format_excludes_private()

### Community 23 - "Community 23"

Cohesion: 0.43
Nodes (4): make_ambassador(), test_get_ambassador_detail(), test_get_ambassador_detail_404_when_not_public(), test_list_ambassadors_excludes_private_and_pii()

### Community 24 - "Community 24"

Cohesion: 0.47
Nodes (3): _make_test_app(), test_common_headers_always_present(), test_hsts_only_sent_when_enabled()

### Community 25 - "Community 25"

Cohesion: 0.7
Nodes (4): _csv_response(), export_payments_csv(), export_registrations_csv(), _sanitize_csv_cell()

### Community 26 - "Community 26"

Cohesion: 0.4
Nodes (0): 

### Community 27 - "Community 27"

Cohesion: 0.4
Nodes (0): 

### Community 28 - "Community 28"

Cohesion: 0.4
Nodes (0): 

### Community 29 - "Community 29"

Cohesion: 0.5
Nodes (1): event_settings, pass_types & sessions admin permissions  Revision ID: 547ad7a3ad

### Community 30 - "Community 30"

Cohesion: 0.5
Nodes (1): admin_users lockout columns  Revision ID: 5a30c6996bc8 Revises: 2c2d07493eb5 Cre

### Community 31 - "Community 31"

Cohesion: 0.5
Nodes (1): referentials (days, pass_types, partner_levels, faq_categories)  Revision ID: e1

### Community 32 - "Community 32"

Cohesion: 0.5
Nodes (1): newsletter_subscribers table  Revision ID: c375ad4fa2bb Revises: 866edbae2931 Cr

### Community 33 - "Community 33"

Cohesion: 0.5
Nodes (1): waitlist last_notified_at  Revision ID: d3e4f5a6b7c8 Revises: c2d3e4f5a6b7 Creat

### Community 34 - "Community 34"

Cohesion: 0.5
Nodes (1): event_settings year  Revision ID: e4f5a6b7c8d9 Revises: d3e4f5a6b7c8 Create Date

### Community 35 - "Community 35"

Cohesion: 0.5
Nodes (1): promo_codes, payments, tickets, waitlist  Revision ID: a3f8aaae2d58 Revises: 9dd

### Community 36 - "Community 36"

Cohesion: 0.5
Nodes (1): waitlist.view permission  Revision ID: 80348b151263 Revises: 547ad7a3ad02 Create

### Community 37 - "Community 37"

Cohesion: 0.5
Nodes (1): admin_users.status column + admin_users.manage permission  Revision ID: 9c1e2f4a

### Community 38 - "Community 38"

Cohesion: 0.5
Nodes (1): faqs.manage permission and seed FAQ content  Revision ID: f5a6b7c8d9e0 Revises:

### Community 39 - "Community 39"

Cohesion: 0.5
Nodes (1): ambassador is_public  Revision ID: b2c3d4e5f6a7 Revises: a1b2c3d4e5f6 Create Dat

### Community 40 - "Community 40"

Cohesion: 0.5
Nodes (1): campaign_window_event_key  Revision ID: b1c2d3e4f5a6 Revises: 75418b933d4f Creat

### Community 41 - "Community 41"

Cohesion: 0.5
Nodes (1): otp_codes table (participant OTP login)  Revision ID: 75418b933d4f Revises: d7d5

### Community 42 - "Community 42"

Cohesion: 0.5
Nodes (1): users and user_profiles  Revision ID: 86b8fb32827d Revises: e15b192c81f5 Create

### Community 43 - "Community 43"

Cohesion: 0.5
Nodes (1): pass_contents and partner_levels admin  Revision ID: d4e5f6a7b8c9 Revises: c3d4e

### Community 44 - "Community 44"

Cohesion: 0.5
Nodes (1): promo_codes admin permission  Revision ID: c2d3e4f5a6b7 Revises: 9c1e2f4a7b3d Cr

### Community 45 - "Community 45"

Cohesion: 0.5
Nodes (1): campaign_windows  Revision ID: 2c2d07493eb5 Revises: a9e9ba5fc6f7 Create Date: 2

### Community 46 - "Community 46"

Cohesion: 0.5
Nodes (1): ambassador photo_url  Revision ID: a1b2c3d4e5f6 Revises: f5a6b7c8d9e0 Create Dat

### Community 47 - "Community 47"

Cohesion: 0.5
Nodes (1): hackathon_universitaire  Revision ID: c3d4e5f6a7b8 Revises: b2c3d4e5f6a7 Create

### Community 48 - "Community 48"

Cohesion: 0.5
Nodes (1): rbac (roles, permissions, role_permissions, admin_users)  Revision ID: a9e9ba5fc

### Community 49 - "Community 49"

Cohesion: 0.5
Nodes (1): partner_benefits  Revision ID: e5f6a7b8c9d0 Revises: d4e5f6a7b8c9 Create Date: 2

### Community 50 - "Community 50"

Cohesion: 0.5
Nodes (1): faqs, contact_messages  Revision ID: 3f306df50f16 Revises: 7b6712058249 Create D

### Community 51 - "Community 51"

Cohesion: 0.5
Nodes (1): initial (empty)  Revision ID: 5e965f30353e Revises:  Create Date: 2026-08-25 21:

### Community 52 - "Community 52"

Cohesion: 0.5
Nodes (1): speakers, ambassadors, partners, exhibitors  Revision ID: 7b6712058249 Revises:

### Community 53 - "Community 53"

Cohesion: 0.5
Nodes (1): audit_logs table  Revision ID: 866edbae2931 Revises: 5a30c6996bc8 Create Date: 2

### Community 54 - "Community 54"

Cohesion: 0.5
Nodes (1): sessions  Revision ID: 9dd893772cc0 Revises: 86b8fb32827d Create Date: 2026-08-2

### Community 55 - "Community 55"

Cohesion: 0.67
Nodes (0): 

### Community 56 - "Community 56"

Cohesion: 0.67
Nodes (0): 

### Community 57 - "Community 57"

Cohesion: 0.67
Nodes (0): 

### Community 58 - "Community 58"

Cohesion: 0.67
Nodes (0): 

### Community 59 - "Community 59"

Cohesion: 0.67
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
Nodes (0): 

### Community 68 - "Community 68"

Cohesion: 1.0
Nodes (0): 

### Community 69 - "Community 69"

Cohesion: 1.0
Nodes (0): 

### Community 70 - "Community 70"

Cohesion: 1.0
Nodes (0): 

### Community 71 - "Community 71"

Cohesion: 1.0
Nodes (0): 

### Community 72 - "Community 72"

Cohesion: 1.0
Nodes (0): 

### Community 73 - "Community 73"

Cohesion: 1.0
Nodes (1): Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background

### Community 74 - "Community 74"

Cohesion: 1.0
Nodes (1): Validate a multipart form's non-file fields against a Pydantic model.      Works

### Community 75 - "Community 75"

Cohesion: 1.0
Nodes (1): Verify admin credentials, enforcing the account-lockout policy.      Always take

### Community 76 - "Community 76"

Cohesion: 1.0
Nodes (1): Issued after a successful OTP verify (app/api/participant_auth.py).      Distinc

### Community 77 - "Community 77"

Cohesion: 1.0
Nodes (1): Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background

## Knowledge Gaps
- **53 isolated node(s):** `Validate a multipart form's non-file fields against a Pydantic model.      Works`, `Application-layer encryption for genuinely sensitive PII (7.8).      Not for fie`, `Sous-ensemble sans PII de SpeakerRead, pour les endpoints publics (liste + détai`, `Sous-ensemble sans PII de AmbassadorRead, pour les endpoints publics (liste + dé`, `Sous-ensemble sans PII de PartnerRead, pour l'endpoint public /api/partners.` (+48 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 60`** (2 nodes): `list_audit_logs()`, `admin_audit.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (2 nodes): `list_waitlist()`, `admin_waitlist.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (2 nodes): `test_health()`, `test_health.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `rate_limit.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Validate a multipart form's non-file fields against a Pydantic model.      Works`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Verify admin credentials, enforcing the account-lockout policy.      Always take`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `Issued after a successful OTP verify (app/api/participant_auth.py).      Distinc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.