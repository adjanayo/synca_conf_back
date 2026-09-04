# [require_open_campaign() & set_window()] Cluster

> 10 nodes · cohesion 0.33

## Key Concepts

- [verify_recaptcha()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/recaptcha.py#L9) (8 connections)
- [test_recaptcha.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_recaptcha.py#L1) (5 connections)
- [contact()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/forms.py#L152) (4 connections)
- [_mock_response()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_recaptcha.py#L17) (4 connections)
- [test_verify_recaptcha_accepts_good_score()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_recaptcha.py#L23) (3 connections)
- [test_verify_recaptcha_rejects_low_score()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_recaptcha.py#L38) (3 connections)
- [test_verify_recaptcha_rejects_unsuccessful_response()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_recaptcha.py#L55) (3 connections)
- [test_verify_recaptcha_skips_when_no_secret_configured()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_recaptcha.py#L11) (2 connections)
- [Verify a reCAPTCHA v3 token, raising 400 on failure.      Skipped entirely when](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/recaptcha.py#L10) (1 connections)
- [recaptcha.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/recaptcha.py#L1) (1 connections)

## Relationships

- [[[PassType & register_payload()] Cluster]] (1 shared connections)

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/forms.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/api/forms.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/recaptcha.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/recaptcha.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_recaptcha.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_recaptcha.py)

## Audit Trail

- EXTRACTED: 21 (62%)
- INFERRED: 13 (38%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*