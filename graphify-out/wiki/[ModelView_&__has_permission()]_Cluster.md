# [ModelView & _has_permission()] Cluster

> 19 nodes · cohesion 0.16

## Key Concepts

- [test_admin_panel.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L1) (9 connections)
- [make_admin()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L16) (8 connections)
- [make_admin_with_role()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L10) (6 connections)
- [test_rbac_deps.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L1) (6 connections)
- [get_current_admin()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py#L14) (5 connections)
- [test_require_permission_granted()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L49) (5 connections)
- [test_get_current_admin_valid_token()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L26) (4 connections)
- [require_permission()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py#L42) (3 connections)
- [test_login_success_grants_access_to_a_permitted_view()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L88) (3 connections)
- [test_require_permission_denied_returns_403()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L63) (3 connections)
- [test_any_authenticated_admin_can_read_contact_messages()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L138) (2 connections)
- [test_login_wrong_password_is_rejected()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L105) (2 connections)
- [test_role_without_permission_gets_403_on_gated_view()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L122) (2 connections)
- [test_get_current_admin_invalid_token_raises_401()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L42) (2 connections)
- [test_get_current_admin_missing_token_raises_401()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L35) (2 connections)
- [rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py#L1) (2 connections)
- [client()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L68) (1 connections)
- [_dispose_global_engine()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L56) (1 connections)
- [test_unauthenticated_request_redirects_to_login()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py#L154) (1 connections)

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_admin_panel.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py)

## Audit Trail

- EXTRACTED: 48 (72%)
- INFERRED: 19 (28%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*