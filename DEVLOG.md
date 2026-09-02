# Journal de dev — synca_conf_back

## TODO
- [ ] Corriger incompatibilité version pytest-asyncio (échec identifié lors du run de tests)
- [ ] Vérifier flow signup côté API (erreur "service indisponible" vue côté front)

## Journal

### 2026-09-02
- Fait : implémentation auth OTP/JWT participant (otp.py, otp_service.py, participant_auth.py + modifs auth/auth_service/config/email_templates/user_me/main).
- Fait : migration Alembic déployée, tests ajoutés (test_participant_otp.py), lint corrigé dans auth_service.py.
- Fait : smoke tests curl passés (génération OTP + auth JWT), rate limiting vérifié, utilisateur superadmin créé.
- À suivre : incompatibilité pytest-asyncio pré-existante à corriger ; investiguer erreur signup remontée par le front.
