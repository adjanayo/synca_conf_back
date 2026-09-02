# [FaqCategory & ContactMessage] Cluster

> 38 nodes · cohesion 0.08

## Key Concepts

- [hash_password()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/security.py#L37) (10 connections)
- [test_admin_panel.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L1) (9 connections)
- [request_otp()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/otp_service.py#L30) (8 connections)
- [make_admin()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L16) (8 connections)
- [validate_password_strength()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/security.py#L20) (7 connections)
- [create_admin_user()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_users.py#L59) (5 connections)
- [_to_read()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_users.py#L21) (5 connections)
- [main()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/cli/create_admin.py#L16) (5 connections)
- [verify_otp()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/otp_service.py#L60) (5 connections)
- [verify_password()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/security.py#L41) (5 connections)
- [update_admin_user()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_users.py#L100) (4 connections)
- [verify_login_code()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/participant_auth.py#L31) (4 connections)
- [grant_permission()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L31) (4 connections)
- [admin_users.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_users.py#L1) (4 connections)
- [security.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/security.py#L1) (4 connections)
- [otp_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/otp_service.py#L1) (4 connections)
- [test_security.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_security.py#L1) (4 connections)
- [ParticipantTokenOut](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L24) (3 connections)
- [InvalidOtpError](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/otp_service.py#L22) (3 connections)
- [WeakPasswordError](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/security.py#L16) (3 connections)
- [test_login_success_grants_access_to_a_permitted_view()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L88) (3 connections)
- [test_hash_and_verify_roundtrip()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_security.py#L11) (3 connections)
- [test_verify_wrong_password_fails()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_security.py#L17) (3 connections)
- [list_admin_users()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_users.py#L36) (2 connections)
- [_generate_code()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/otp_service.py#L26) (2 connections)
- *... and 13 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class ParticipantTokenOut {
        +auth.py()
    }
    class InvalidOtpError {
        +otp_service.py()
    }
    class WeakPasswordError {
        +security.py()
    }
```

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_users.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/admin_users.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/participant_auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/participant_auth.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/cli/create_admin.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/cli/create_admin.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/security.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/core/security.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/otp_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/otp_service.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_security.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_security.py)

## Audit Trail

- EXTRACTED: 86 (63%)
- INFERRED: 51 (37%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*