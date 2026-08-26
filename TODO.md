# TO DOs will be here



- [x] All the pictures and files will be available on the production server itself — note only, no code change; storage stays on Backblaze B2 (4.10)
- [x] Work on the email templates (html base) — `app/services/email_templates.py`, wired into `forms.py`/`ticket_finalization.py`
- [x] Work on ticket pdf template (not full a4 - heigh 5cm - width 21cm) — `app/services/ticket_pdf.py`, 210x50mm strip
- [x] ticket can be downloaded on the web page or from the email (idor vuln check) — `GET /api/user/me/tickets` scoped to bearer token's own `user_id`, no `{id}` param; B2 `pdf_url` is UUID-keyed (not enumerable)
- [x] Add the security points on the endpoints for the frontend part — `FRONTEND_INTEGRATION.md` §7
- [x] Update the frontend integration file and the documentations witht the right contents — added §6 (participant self-service: `/user/me`, `/user/me/tickets`), §7 (security), renumbered §8-12
- [x] Did we have the email for the speakers, the tickets, the partners, the ambassadors, the exibitors ??? — yes, all 5 + registration send HTML confirmation emails (`email_templates.py`)
- [x] I wand to see the template of the ticket — sent as `ticket_test.pdf` earlier in session