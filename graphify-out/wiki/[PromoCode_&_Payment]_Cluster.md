# [PromoCode & Payment] Cluster

> 68 nodes · cohesion 0.05

## Key Concepts

- [authenticate_admin()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L40) (14 connections)
- [decode_token()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L130) (11 connections)
- [make_admin()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_login.py#L19) (11 connections)
- [AdminAuth](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/admin/auth.py#L18) (10 connections)
- [auth_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L1) (10 connections)
- [Échange un refresh_token (long-lived) contre une nouvelle paire --     évite de](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/auth.py#L56) (9 connections)
- [InvalidTokenError](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L24) (9 connections)
- [UserRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/users.py#L13) (9 connections)
- **Exception** (7 connections)
- [TicketRead](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/tickets.py#L6) (7 connections)
- [auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L1) (7 connections)
- [test_admin_login.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_login.py#L1) (7 connections)
- [AccountLockedError](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L32) (6 connections)
- [InvalidCredentialsError](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L28) (6 connections)
- [login()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/auth.py#L27) (5 connections)
- [create_refresh_token()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L110) (5 connections)
- [TokenPair](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L9) (5 connections)
- [test_auth_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_auth_service.py#L1) (5 connections)
- [AdminMeOut](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py#L33) (4 connections)
- [build_admin_auth()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/admin/auth.py#L73) (4 connections)
- [SQLAdmin login backed by the same admin_users/Argon2id/lockout path     as POST](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/admin/auth.py#L19) (4 connections)
- [AccountDisabledError](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L36) (4 connections)
- [create_participant_token()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L114) (4 connections)
- [_create_token()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py#L89) (4 connections)
- [Accepts either credential: the legacy one-time `access_token` handed     out at](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/user_me.py#L23) (4 connections)
- *... and 43 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class AdminAuth {
        +auth.py()
        +.login()
        +.logout()
        +.authenticate()
    }
    class AdminLoginRequest {
        +auth.py()
    }
    class AdminMeOut {
        +auth.py()
    }
    class OtpRequestIn {
        +auth.py()
    }
    class OtpVerifyIn {
        +auth.py()
    }
    class RefreshRequest {
        +auth.py()
    }
    class AccountDisabledError {
        +auth_service.py()
    }
    class AccountLockedError {
        +auth_service.py()
    }
    class InvalidCredentialsError {
        +auth_service.py()
    }
    class InvalidTokenError {
        +auth_service.py()
    }
    class TokenPair {
        +auth.py()
    }
    class TicketRead {
        +tickets.py()
    }
    class RegisterResponse {
        +users.py()
    }
    class UserProfileRead {
        +users.py()
    }
    class UserRead {
        +users.py()
    }
    AdminAuth --> AccountLockedError
    AdminAuth --> InvalidCredentialsError
    AdminAuth --> InvalidTokenError
    AccountLockedError --> AdminAuth
    InvalidCredentialsError --> AdminAuth
    InvalidTokenError --> AdminAuth
    UserRead <|-- RegisterResponse
    RegisterResponse <|-- UserRead
```

## Relationships

- [[[authenticate_admin() & make_admin()] Cluster]] (23 shared connections)

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/admin/auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/admin/auth.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/admin/setup.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/admin/setup.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/auth.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/user_me.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/user_me.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/auth.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/tickets.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/tickets.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/users.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/schemas/users.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/auth_service.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_login.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_login.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_audit_log.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_audit_log.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_auth_service.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_auth_service.py)

## Audit Trail

- EXTRACTED: 153 (57%)
- INFERRED: 117 (43%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*