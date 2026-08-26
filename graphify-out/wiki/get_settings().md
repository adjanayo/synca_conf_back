# get_settings()

> God node · 15 connections · [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/config.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/config.py#L88)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as get_settings()
    participant P1 as upload_file()
    participant P2 as validate_is_real_image()
    participant P3 as UploadRejectedError
    participant P4 as test_validate_is_real_image_accepts_real_image()
    participant P5 as test_validate_is_real_image_rejects_fake_image()
    participant P6 as apply_as_speaker()
    participant P7 as Speaker
    participant P8 as parse_multipart_form()
    participant P9 as apply_as_partner()
    participant P10 as generate_and_upload_ticket_pdf()
    participant P11 as test_upload_file_rejects_disallowed_content_type()
    participant P12 as test_upload_file_success_never_uses_original_filename()
    participant P13 as test_upload_file_respects_custom_max_bytes()
    participant P14 as _generate_key()
    participant P15 as test_upload_file_rejects_oversized_file()
    participant P16 as test_upload_file_rejects_fake_image_bytes()
    participant P17 as test_upload_file_pdf_skips_image_validation()
    participant P18 as verify_recaptcha()
    participant P19 as payment_webhook()
    participant P20 as send_email()
    participant P21 as configure_logging()
    participant P22 as build_admin_auth()
    participant P23 as Settings
    participant P24 as _client()
    participant P25 as test_expired_token_rejected()
    participant P26 as .process_bind_param()
    participant P27 as .process_result_value()
    participant P28 as db_session()
    participant P29 as upgrade()
    participant P30 as downgrade()
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
    P1->>+ P3: calls
    P3-->>- P1: return
    P3->>+ P1: calls
    P1-->>- P3: return
    P3->>+ P2: calls
    P2-->>- P3: return
    P1->>+ P6: calls
    P6-->>- P1: return
    P6->>+ P1: calls
    P1-->>- P6: return
    P6->>+ P7: calls
    P7-->>- P6: return
    P6->>+ P8: calls
    P8-->>- P6: return
    P1->>+ P9: calls
    P9-->>- P1: return
    P1->>+ P10: calls
    P10-->>- P1: return
    P1->>+ P11: calls
    P11-->>- P1: return
    P1->>+ P12: calls
    P12-->>- P1: return
    P1->>+ P13: calls
    P13-->>- P1: return
    P1->>+ P14: calls
    P14-->>- P1: return
    P1->>+ P15: calls
    P15-->>- P1: return
    P1->>+ P16: calls
    P16-->>- P1: return
    P1->>+ P17: calls
    P17-->>- P1: return
    P0->>+ P18: calls
    P18-->>- P0: return
    P0->>+ P19: calls
    P19-->>- P0: return
    P0->>+ P20: calls
    P20-->>- P0: return
    P0->>+ P21: calls
    P21-->>- P0: return
    P0->>+ P22: calls
    P22-->>- P0: return
    P0->>+ P23: calls
    P23-->>- P0: return
    P0->>+ P24: calls
    P24-->>- P0: return
    P0->>+ P25: calls
    P25-->>- P0: return
    P0->>+ P26: calls
    P26-->>- P0: return
    P0->>+ P27: calls
    P27-->>- P0: return
    P0->>+ P28: calls
    P28-->>- P0: return
    P0->>+ P29: calls
    P29-->>- P0: return
    P0->>+ P30: calls
    P30-->>- P0: return
```

## Connections by Relation

### calls
- [[upload_file()]] `INFERRED`
- [[verify_recaptcha()]] `INFERRED`
- [[payment_webhook()]] `INFERRED`
- [[send_email()]] `INFERRED`
- [[configure_logging()]] `INFERRED`
- [[build_admin_auth()]] `INFERRED`
- [[Settings]] `EXTRACTED`
- [[_client()]] `INFERRED`
- [[test_expired_token_rejected()]] `INFERRED`
- [[.process_bind_param()]] `INFERRED`
- [[.process_result_value()]] `INFERRED`
- [[db_session()]] `INFERRED`
- [[upgrade()]] `INFERRED`
- [[downgrade()]] `INFERRED`

### contains
- [[config.py]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*