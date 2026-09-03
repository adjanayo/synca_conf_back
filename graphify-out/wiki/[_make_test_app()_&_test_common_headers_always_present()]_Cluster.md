# [_make_test_app() & test_common_headers_always_present()] Cluster

> 9 nodes · cohesion 0.44

## Key Concepts

- [require_open_campaign()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/campaign_windows.py#L11) (6 connections)
- [test_campaign_window_deps.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py#L1) (6 connections)
- [set_window()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py#L11) (5 connections)
- [test_open_window_allows()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py#L24) (3 connections)
- [test_window_already_closed_forbidden()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py#L56) (3 connections)
- [test_window_deactivated_forbidden_even_within_dates()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py#L73) (3 connections)
- [test_window_not_yet_started_forbidden()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py#L39) (3 connections)
- [test_missing_window_forbidden()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py#L90) (2 connections)
- [campaign_windows.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/campaign_windows.py#L1) (1 connections)

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/campaign_windows.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/deps/campaign_windows.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_campaign_window_deps.py)

## Audit Trail

- EXTRACTED: 22 (69%)
- INFERRED: 10 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*