# [form_fields() & make_png_bytes()] Cluster

> 10 nodes · cohesion 0.36

## Key Concepts

- [make_admin_with_role()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L10) (6 connections)
- [test_rbac_deps.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L1) (6 connections)
- [get_current_admin()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py#L14) (5 connections)
- [test_require_permission_granted()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L49) (5 connections)
- [test_get_current_admin_valid_token()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L26) (4 connections)
- [require_permission()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py#L42) (3 connections)
- [test_require_permission_denied_returns_403()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L63) (3 connections)
- [test_get_current_admin_invalid_token_raises_401()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L42) (2 connections)
- [test_get_current_admin_missing_token_raises_401()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py#L35) (2 connections)
- [rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py#L1) (2 connections)

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/rbac.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_rbac_deps.py)

## Audit Trail

- EXTRACTED: 22 (58%)
- INFERRED: 16 (42%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*