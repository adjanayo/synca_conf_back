# [form_fields() & open_call_for_partner()] Cluster

> 13 nodes · cohesion 0.23

## Key Concepts

- [make_ticket()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_ticket_finalization.py#L10) (8 connections)
- [finalize_ticket()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_finalization.py#L14) (8 connections)
- [test_ticket_finalization.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_ticket_finalization.py#L1) (5 connections)
- [generate_and_upload_ticket_pdf()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_pdf.py#L96) (4 connections)
- [_render_ticket_pdf()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_pdf.py#L34) (4 connections)
- [test_finalize_ticket_is_idempotent_when_already_finalized()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_ticket_finalization.py#L102) (3 connections)
- [test_finalize_ticket_sets_pdf_url_and_sends_email()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_ticket_finalization.py#L68) (3 connections)
- [ticket_pdf.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_pdf.py#L1) (3 connections)
- [test_finalize_ticket_noops_on_missing_ticket()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_ticket_finalization.py#L127) (2 connections)
- [Generate the ticket's PDF+QR, upload it, and email it.      Runs as a Background](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_finalization.py#L15) (2 connections)
- [_render_qr_png()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_pdf.py#L27) (2 connections)
- [_use_test_session()](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_ticket_finalization.py#L55) (1 connections)
- [ticket_finalization.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_finalization.py#L1) (1 connections)

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_finalization.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_finalization.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_pdf.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/app/services/ticket_pdf.py)
- [/Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_ticket_finalization.py](file:///Users/kodjododjango/Downloads/dev_projects/synca_conf_back/tests/test_ticket_finalization.py)

## Audit Trail

- EXTRACTED: 28 (61%)
- INFERRED: 18 (39%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*