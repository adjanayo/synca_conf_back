# create_access_token()

> God node · 47 connections · [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L104)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as create_access_token()
    participant P1 as refresh()
    participant P2 as authenticate_admin()
    participant P3 as AccountLockedError
    participant P4 as InvalidCredentialsError
    participant P5 as login()
    participant P6 as verify_password()
    participant P7 as AccountDisabledError
    participant P8 as AuditLog
    participant P9 as .login()
    participant P10 as test_successful_login_writes_audit_entry()
    participant P11 as test_failed_login_writes_audit_entry()
    participant P12 as test_locked_account_attempt_writes_audit_entry()
    participant P13 as test_account_locks_after_five_failed_attempts()
    participant P14 as decode_token()
    participant P15 as make_ticket()
    participant P16 as payment_webhook()
    participant P17 as test_webhook_increments_promo_usage_count_on_completion()
    participant P18 as create_admin_user()
    participant P19 as register()
    participant P20 as apply_as_speaker()
    participant P21 as apply_as_ambassador()
    participant P22 as apply_as_partner()
    participant P23 as apply_as_exhibitor()
    participant P24 as create_team_member()
    participant P25 as TokenPair
    participant P26 as create_refresh_token()
    participant P27 as create_payment()
    participant P28 as update_admin_user()
    participant P29 as make_user()
    participant P30 as create_ambassador_admin()
    participant P31 as contact()
    participant P32 as update_team_member()
    participant P33 as test_finalize_ticket_sets_pdf_url_and_sends_email()
    participant P34 as test_update_campaign_window_rejects_end_before_start()
    participant P35 as test_webhook_completes_payment_and_creates_ticket()
    participant P36 as test_webhook_failed_status_marks_payment_failed()
    participant P37 as test_webhook_rejects_transaction_ref_reused_on_other_payment()
    participant P38 as test_payment_default_status_pending()
    participant P39 as test_partner_negotiation_workflow()
    participant P40 as test_faq_crud_basic()
    participant P41 as create_day()
    participant P42 as create_session()
    participant P43 as create_speaker_admin()
    participant P44 as update_ambassador_status()
    participant P45 as create_partner_admin()
    participant P46 as create_exhibitor_admin()
    participant P47 as join_waitlist()
    participant P48 as subscribe_newsletter()
    participant P49 as update_campaign_window()
    participant P50 as create_faq_category()
    participant P51 as create_faq()
    participant P52 as create_partner_benefit()
    participant P53 as create_promo_code()
    participant P54 as create_pass_content()
    participant P55 as test_null_special_needs_stays_null()
    participant P56 as test_get_ambassador_detail()
    participant P57 as test_get_ambassador_detail_404_when_not_public()
    participant P58 as test_delete_me_anonymizes_and_revokes_token()
    participant P59 as test_get_speaker_detail()
    participant P60 as test_get_speaker_detail_404_when_not_public()
    participant P61 as test_speaker_default_status_pending_and_not_public()
    participant P62 as test_speaker_status_workflow_transition()
    participant P63 as test_ambassador_social_handles_json()
    participant P64 as test_exhibitor_default_status_and_public()
    participant P65 as test_contact_message_default_unread()
    participant P66 as update_day()
    participant P67 as update_session()
    participant P68 as update_speaker_status()
    participant P69 as update_partner_status()
    participant P70 as update_exhibitor_status()
    participant P71 as update_contact_read_status()
    participant P72 as update_faq_category()
    participant P73 as update_faq()
    participant P74 as update_partner_benefit()
    participant P75 as update_event_settings()
    participant P76 as update_promo_code()
    participant P77 as update_pass_content()
    participant P78 as test_stats_computed_from_payments_tickets_and_applications()
    participant P79 as test_admin_endpoint_limited_to_30_per_minute()
    participant P80 as _create_token()
    participant P81 as test_get_current_admin_valid_token()
    participant P82 as test_export_registrations_csv()
    participant P83 as test_export_payments_csv()
    participant P84 as test_export_registrations_neutralizes_csv_formula_injection()
    participant P85 as test_any_authenticated_admin_can_list_contacts()
    participant P86 as test_list_contacts_filters_by_is_read()
    participant P87 as test_superadmin_can_update_role_permissions()
    participant P88 as test_non_superadmin_forbidden()
    participant P89 as test_unknown_permission_code_rejected()
    participant P90 as test_speaker_accepted_publishes_it()
    participant P91 as test_speaker_rejected_stays_unpublished()
    participant P92 as test_speaker_update_forbidden_without_permission()
    participant P93 as test_speaker_update_rejects_invalid_status()
    participant P94 as test_ambassador_accepted()
    participant P95 as test_ambassador_accepted_twice_does_not_regenerate_promo_code()
    participant P96 as test_ambassador_update_forbidden_without_permission()
    participant P97 as test_partner_confirmed_publishes_it()
    participant P98 as test_partner_negotiating_stays_unpublished()
    participant P99 as test_partner_update_forbidden_without_permission()
    participant P100 as test_exhibitor_confirmed_publishes_it()
    participant P101 as test_exhibitor_update_forbidden_without_permission()
    participant P102 as test_list_registrations_returns_all_by_default()
    participant P103 as test_list_registrations_filters_by_status()
    participant P104 as test_list_registrations_respects_pagination_limit()
    participant P105 as test_me_returns_identity_role_and_permissions()
    participant P106 as test_list_campaign_windows_admin()
    participant P107 as test_list_campaign_windows_forbidden_without_permission()
    participant P108 as test_update_campaign_window_dates_and_is_active()
    participant P109 as test_update_campaign_window_unknown_key_404()
    participant P110 as test_update_campaign_window_forbidden_without_permission()
    participant P111 as test_export_registrations_forbidden_without_permission()
    participant P112 as test_export_payments_forbidden_without_permission()
    participant P113 as test_stats_forbidden_without_permission()
    participant P114 as test_stats_handles_no_completed_payments()
    participant P115 as test_speaker_update_404_for_unknown_id()
    participant P116 as test_access_token_round_trip()
    participant P117 as test_wrong_token_type_rejected()
    participant P118 as test_invalid_signature_rejected()
    participant P119 as test_list_registrations_forbidden_without_permission()
    P0->>+ P1: calls
    P1-->>- P0: return
    P1->>+ P0: calls
    P0-->>- P1: return
    P1->>+ P2: calls
    P2-->>- P1: return
    P2->>+ P1: calls
    P1-->>- P2: return
    P2->>+ P3: calls
    P3-->>- P2: return
    P2->>+ P4: calls
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
    P1->>+ P14: calls
    P14-->>- P1: return
    P1->>+ P15: calls
    P15-->>- P1: return
    P1->>+ P16: calls
    P16-->>- P1: return
    P1->>+ P17: calls
    P17-->>- P1: return
    P1->>+ P18: calls
    P18-->>- P1: return
    P1->>+ P19: calls
    P19-->>- P1: return
    P1->>+ P20: calls
    P20-->>- P1: return
    P1->>+ P21: calls
    P21-->>- P1: return
    P1->>+ P22: calls
    P22-->>- P1: return
    P1->>+ P23: calls
    P23-->>- P1: return
    P1->>+ P24: calls
    P24-->>- P1: return
    P1->>+ P25: calls
    P25-->>- P1: return
    P1->>+ P26: calls
    P26-->>- P1: return
    P1->>+ P27: calls
    P27-->>- P1: return
    P1->>+ P28: calls
    P28-->>- P1: return
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
    P1->>+ P44: calls
    P44-->>- P1: return
    P1->>+ P45: calls
    P45-->>- P1: return
    P1->>+ P46: calls
    P46-->>- P1: return
    P1->>+ P47: calls
    P47-->>- P1: return
    P1->>+ P48: calls
    P48-->>- P1: return
    P1->>+ P49: calls
    P49-->>- P1: return
    P1->>+ P50: calls
    P50-->>- P1: return
    P1->>+ P51: calls
    P51-->>- P1: return
    P1->>+ P52: calls
    P52-->>- P1: return
    P1->>+ P53: calls
    P53-->>- P1: return
    P1->>+ P54: calls
    P54-->>- P1: return
    P1->>+ P55: calls
    P55-->>- P1: return
    P1->>+ P56: calls
    P56-->>- P1: return
    P1->>+ P57: calls
    P57-->>- P1: return
    P1->>+ P58: calls
    P58-->>- P1: return
    P1->>+ P59: calls
    P59-->>- P1: return
    P1->>+ P60: calls
    P60-->>- P1: return
    P1->>+ P61: calls
    P61-->>- P1: return
    P1->>+ P62: calls
    P62-->>- P1: return
    P1->>+ P63: calls
    P63-->>- P1: return
    P1->>+ P64: calls
    P64-->>- P1: return
    P1->>+ P65: calls
    P65-->>- P1: return
    P1->>+ P66: calls
    P66-->>- P1: return
    P1->>+ P67: calls
    P67-->>- P1: return
    P1->>+ P68: calls
    P68-->>- P1: return
    P1->>+ P69: calls
    P69-->>- P1: return
    P1->>+ P70: calls
    P70-->>- P1: return
    P1->>+ P71: calls
    P71-->>- P1: return
    P1->>+ P72: calls
    P72-->>- P1: return
    P1->>+ P73: calls
    P73-->>- P1: return
    P1->>+ P74: calls
    P74-->>- P1: return
    P1->>+ P75: calls
    P75-->>- P1: return
    P1->>+ P76: calls
    P76-->>- P1: return
    P1->>+ P77: calls
    P77-->>- P1: return
    P0->>+ P78: calls
    P78-->>- P0: return
    P0->>+ P79: calls
    P79-->>- P0: return
    P0->>+ P5: calls
    P5-->>- P0: return
    P0->>+ P80: calls
    P80-->>- P0: return
    P0->>+ P81: calls
    P81-->>- P0: return
    P0->>+ P34: calls
    P34-->>- P0: return
    P0->>+ P82: calls
    P82-->>- P0: return
    P0->>+ P83: calls
    P83-->>- P0: return
    P0->>+ P84: calls
    P84-->>- P0: return
    P0->>+ P85: calls
    P85-->>- P0: return
    P0->>+ P86: calls
    P86-->>- P0: return
    P0->>+ P87: calls
    P87-->>- P0: return
    P0->>+ P88: calls
    P88-->>- P0: return
    P0->>+ P89: calls
    P89-->>- P0: return
    P0->>+ P90: calls
    P90-->>- P0: return
    P0->>+ P91: calls
    P91-->>- P0: return
    P0->>+ P92: calls
    P92-->>- P0: return
    P0->>+ P93: calls
    P93-->>- P0: return
    P0->>+ P94: calls
    P94-->>- P0: return
    P0->>+ P95: calls
    P95-->>- P0: return
    P0->>+ P96: calls
    P96-->>- P0: return
    P0->>+ P97: calls
    P97-->>- P0: return
    P0->>+ P98: calls
    P98-->>- P0: return
    P0->>+ P99: calls
    P99-->>- P0: return
    P0->>+ P100: calls
    P100-->>- P0: return
    P0->>+ P101: calls
    P101-->>- P0: return
    P0->>+ P102: calls
    P102-->>- P0: return
    P0->>+ P103: calls
    P103-->>- P0: return
    P0->>+ P104: calls
    P104-->>- P0: return
    P0->>+ P9: calls
    P9-->>- P0: return
    P0->>+ P105: calls
    P105-->>- P0: return
    P0->>+ P106: calls
    P106-->>- P0: return
    P0->>+ P107: calls
    P107-->>- P0: return
    P0->>+ P108: calls
    P108-->>- P0: return
    P0->>+ P109: calls
    P109-->>- P0: return
    P0->>+ P110: calls
    P110-->>- P0: return
    P0->>+ P111: calls
    P111-->>- P0: return
    P0->>+ P112: calls
    P112-->>- P0: return
    P0->>+ P113: calls
    P113-->>- P0: return
    P0->>+ P114: calls
    P114-->>- P0: return
    P0->>+ P115: calls
    P115-->>- P0: return
    P0->>+ P116: calls
    P116-->>- P0: return
    P0->>+ P117: calls
    P117-->>- P0: return
    P0->>+ P118: calls
    P118-->>- P0: return
    P0->>+ P119: calls
    P119-->>- P0: return
```

## Connections by Relation

### calls
- [[refresh()]] `INFERRED`
- [[test_stats_computed_from_payments_tickets_and_applications()]] `INFERRED`
- [[test_admin_endpoint_limited_to_30_per_minute()]] `INFERRED`
- [[login()]] `INFERRED`
- [[_create_token()]] `EXTRACTED`
- [[test_get_current_admin_valid_token()]] `INFERRED`
- [[test_update_campaign_window_rejects_end_before_start()]] `INFERRED`
- [[test_export_registrations_csv()]] `INFERRED`
- [[test_export_payments_csv()]] `INFERRED`
- [[test_export_registrations_neutralizes_csv_formula_injection()]] `INFERRED`
- [[test_any_authenticated_admin_can_list_contacts()]] `INFERRED`
- [[test_list_contacts_filters_by_is_read()]] `INFERRED`
- [[test_superadmin_can_update_role_permissions()]] `INFERRED`
- [[test_non_superadmin_forbidden()]] `INFERRED`
- [[test_unknown_permission_code_rejected()]] `INFERRED`
- [[test_speaker_accepted_publishes_it()]] `INFERRED`
- [[test_speaker_rejected_stays_unpublished()]] `INFERRED`
- [[test_speaker_update_forbidden_without_permission()]] `INFERRED`
- [[test_speaker_update_rejects_invalid_status()]] `INFERRED`
- [[test_ambassador_accepted()]] `INFERRED`

### contains
- [[auth_service.py]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*