# Journal de dev — synca_conf_back

## TODO
- [ ] Corriger incompatibilité version pytest-asyncio (échec identifié lors du run de tests)
- [x] Vérifier flow signup côté API (erreur "service indisponible" vue côté front) — c'était un stub front statique, pas un bug back
- [x] `GET /api/admin/me` (débloquait la phase A4 RBAC UI côté front)

## Journal

### 2026-09-02
- Fait : implémentation auth OTP/JWT participant (otp.py, otp_service.py, participant_auth.py + modifs auth/auth_service/config/email_templates/user_me/main).
- Fait : migration Alembic déployée, tests ajoutés (test_participant_otp.py), lint corrigé dans auth_service.py.
- Fait : smoke tests curl passés (génération OTP + auth JWT), rate limiting vérifié, utilisateur superadmin créé.
- Fait : ajout `GET /api/admin/me` (rôle + permissions de l'admin connecté) — débloque A4 côté front ; test_admin_me.py ajouté ; smoke testé via curl (200 avec token, 401 sans).
- À suivre : incompatibilité pytest-asyncio pré-existante à corriger (bloque aussi l'exécution des nouveaux tests admin).
