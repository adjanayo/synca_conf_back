# Journal de dev — synca_conf_back

## TODO
- [x] Corriger incompatibilité version pytest-asyncio (échec identifié lors du run de tests) — faux diagnostic initial, voir journal 2026-09-02 (suite)
- [x] Vérifier flow signup côté API (erreur "service indisponible" vue côté front) — c'était un stub front statique, pas un bug back
- [x] `GET /api/admin/me` (débloquait la phase A4 RBAC UI côté front)
- [x] `GET /api/admin/speakers` (débloquait la phase C1 modération côté front)
- [x] `GET /api/admin/ambassadors` (débloquait la phase C2 modération côté front)
- [x] `GET /api/admin/exhibitors` (débloquait la phase C4 modération côté front)
- [x] `GET /api/admin/partners` (débloquait la phase C3 modération côté front)
- [x] `GET /api/admin/audit-logs` (débloquait la phase E2 côté front)
- [x] Clé `event` sur `campaign_windows` (dates de l'événement pilotables au back-office)
- [x] Phase J3 : notification email waitlist à l'ouverture de la billetterie
- [x] `GET /api/partner-levels` (débloquait la phase M1 côté front — formulaire partenaire sans moyen de lister les paliers réels)
- [x] `GET/POST/PATCH /api/admin/promo-codes` + permission `promo_codes.manage` (débloquait la phase N côté front — aucun CRUD admin sur les codes promo)
- [x] Rappels waitlist récurrents après ouverture billetterie (demandé côté front, DEVLOG.md ligne 52 — pas de cron, boucle asyncio en tâche de fond)
- [x] `GET /api/event-settings` public (débloquait l'affichage nom/lieu événement depuis la DB côté front, existait déjà en admin mais pas en lecture publique)
- [x] Colonne `event_settings.year` nullable (débloquait l'affichage "Synca Conf &lt;année&gt;" pilotable depuis le dashboard, sans rien afficher si non définie)

## Journal

### 2026-09-02
- Fait : implémentation auth OTP/JWT participant (otp.py, otp_service.py, participant_auth.py + modifs auth/auth_service/config/email_templates/user_me/main).
- Fait : migration Alembic déployée, tests ajoutés (test_participant_otp.py), lint corrigé dans auth_service.py.
- Fait : smoke tests curl passés (génération OTP + auth JWT), rate limiting vérifié, utilisateur superadmin créé.
- Fait : ajout `GET /api/admin/me` (rôle + permissions de l'admin connecté) — débloque A4 côté front ; test_admin_me.py ajouté ; smoke testé via curl (200 avec token, 401 sans).
- Fait : ajout `GET /api/admin/speakers` (liste toutes les candidatures, filtres status/theme/format, gardé derrière `speakers.approve`) — manquait pour la modération C1 côté front, seul le PATCH existait ; smoke testé via curl (200 liste vide avec token, 401 sans).
- Fait : ajout `GET /api/admin/ambassadors` (liste toutes les candidatures ambassadeurs, filtres status/current_profile, gardé derrière `ambassadors.approve`) — manquait pour la modération C2 côté front, seul le PATCH existait ; smoke testé via curl (200 liste vide avec token, 401 sans).
- Fait : ajout `GET /api/admin/exhibitors` (liste tous les exposants, filtres status/stand_type, gardé derrière `exhibitors.manage`) — manquait pour la modération C4 côté front, seul le PATCH existait ; smoke testé via curl (200 liste vide avec token, 401 sans).
- Fait : ajout `GET /api/admin/partners` (liste tous les partenaires, filtres status/level_id, gardé derrière `partners.manage`) — manquait pour la modération C3 côté front, seul le PATCH existait ; smoke testé via curl (200 liste vide avec token, 401 sans).
- Fait : ajout `GET /api/admin/audit-logs` (liste des tentatives de connexion admin, filtres event/email/success, modèle `AuditLog` déjà existant et déjà rempli par `auth_service.py` mais sans endpoint de lecture) — débloque E2 côté front. Pas de code RBAC dédié dans les 8 permissions seedées, même situation que `GET /api/admin/contacts` : gardé par `get_current_admin` (tout admin authentifié) plutôt qu'une permission inventée ; smoke testé via TestClient (401 sans token).
- À suivre : incompatibilité pytest-asyncio pré-existante à corriger (bloque aussi l'exécution des nouveaux tests admin).

### 2026-09-02 (suite) — Phase F (qualité)
- Fait : investigation de l'échec de la suite de tests — ce n'était pas une incompatibilité pytest-asyncio (mauvais diagnostic initial) mais deux causes locales : `DB_HOST` par défaut vaut `db` (nom du service docker-compose, non résolvable hors conteneur — lancer les tests localement nécessite `DB_HOST=localhost`), et pollution de la DB dev partagée par des tests réels manuels faits en session (3 lignes `otp_codes` d'anciens smoke tests curl, nettoyées). En CI, aucune des deux ne se produit (`DB_HOST=127.0.0.1` déjà fixé dans `ci.yml`, DB MySQL fraîche à chaque run) — la suite y tournait déjà correctement.
- Fait : fix réel trouvé au passage — `tests/test_rbac.py` codait en dur l'email `admin@synca.conf`, qui est aussi la valeur par défaut d'`ADMIN_EMAIL` (bootstrap superadmin) ; collision garantie sur toute DB dev où le superadmin réel a été créé. Renommé en `rbac-test-admin@example.com`.
- Fait : `ruff check .` sur tout le repo (jusqu'ici vérifié seulement fichier par fichier) — 1 erreur trouvée (`B904` dans `app/cli/create_admin.py`, `raise SystemExit(1)` sans `from exc`), corrigée.
- Fait : suite complète verte — `244 passed`, `ruff check .` clean.

### 2026-09-02 (suite 3) — dates de l'événement pilotables au back-office
- Fait : `campaign_windows` ne couvrait que les fenêtres de candidature/billetterie (call_for_speaker, ticketing, call_for_partner, call_for_ambassador, call_for_exhibitor) — aucune fenêtre pour les dates de la conférence elle-même, qui étaient codées en dur côté front (`TARGET`/`PARAMETER.date`). Ajout d'une 6e clé `event` à l'enum `campaign_window_key` (migration `b1c2d3e4f5a6`, alter enum + seed `18-20 août 2027` d'après `syncaconf/Infos.md`) — réutilise toute la plomberie existante (CRUD admin `GET`/`PATCH /api/admin/campaign-windows`, lecture publique `GET /api/campaign-windows`) sans nouveau modèle ni endpoint.
- Fait : 4 tests mettaient en dur le compte/la liste des 5 fenêtres (`test_campaign_windows.py`, `test_public_campaign_windows.py`, `test_admin_campaign_windows.py`) — mis à jour pour 6. Suite verte : `244 passed`, `ruff check .` clean.

### 2026-09-02 (suite 4) — Phase J3 : notification waitlist à l'ouverture billetterie
- Fait : `PATCH /api/admin/campaign-windows/{key}` (`admin_campaign_windows.py`) détecte désormais la transition fermée→ouverte de la fenêtre `ticketing` (comparaison `is_open` avant/après la mise à jour, même définition que `require_open_campaign`) et déclenche en `BackgroundTasks` l'envoi d'un email à toute entrée `Waitlist` avec `notified=False`, puis les marque `notified=True`. Nouveau template `waitlist_ticketing_open_email()` dans `email_templates.py`. Pas de cron/scheduler dans le projet — le déclencheur est l'action admin qui bascule `is_active`, pas le franchissement de `start_at` en tâche de fond ; limite acceptée (documentée dans `ROADMAP_ADMIN.md` côté front).
- Fait : `ruff check` clean sur les 2 fichiers modifiés. Suite pytest non exécutable dans ce sandbox (ni en local — `DB_HOST=db` non résolvable hors conteneur — ni dans le conteneur `synca-dev-app` : échec `pytest-asyncio` `AssertionError` au setup, y compris sur des tests async préexistants non touchés ici, ex. `test_public_pass_types.py` — régression d'environnement CI/conteneur à investiguer séparément, pas causée par ce changement).
- À suivre : investiguer la régression pytest-asyncio dans le conteneur `synca-dev-app` (setup `AssertionError` sur tous les tests async, y compris ceux non touchés par cette session) — bloque toute vérification de test dans ce conteneur jusqu'à résolution.

### 2026-09-02 (suite 5) — Phase M côté front : ajout `GET /api/partner-levels`
- Fait : en branchant le formulaire partenaire front (`partenaires.tsx`) sur l'API réelle, découvert qu'aucun endpoint public ne liste les paliers de partenariat (`PartnerLevel`) — le formulaire n'avait donc aucun moyen d'obtenir un `level_id` réel (FK requise par `POST /api/partners/apply`), seulement des noms de palier codés en dur côté front sans lien avec la table. Ajouté `GET /api/partner-levels` (`app/api/public.py`, `PartnerLevelRead` déjà existant côté schémas admin, réutilisé tel quel), trié par `sort_order`, même pattern que `GET /api/pass-types`.
- Fait : `ruff check .` clean sur tout le repo après l'ajout. Pas de test ajouté (suite pytest toujours bloquée par la régression pytest-asyncio du conteneur, cf. entrée précédente) — endpoint non exercé par des tests automatisés dans ce sandbox, à couvrir quand la régression sera résolue.

### 2026-09-02 (suite 6) — Phase N côté front : CRUD admin `GET/POST/PATCH /api/admin/promo-codes`
- Fait : le modèle `PromoCode`, `POST /api/promo/validate` et la génération auto de code à l'acceptation d'un ambassadeur existaient déjà, mais aucun endpoint n'exposait de CRUD admin sur la table — impossible de créer/désactiver un code depuis le dashboard. Ajouté `app/api/admin_promo_codes.py` (`GET`/`POST`/`PATCH`, même patron que `admin_pass_types.py` : pas de DELETE dur, `is_active` seul pour désactiver, FK `payments.promo_code_id`/`ambassadors.promo_code_id` préservées). Schémas `PromoCodeCreate`/`PromoCodeUpdate` ajoutés (`app/schemas/payments.py`, `PromoCodeRead` déjà existant réutilisé).
- Fait : nouvelle permission `promo_codes.manage` (migration `c2d3e4f5a6b7`, seedée sur le rôle `superadmin` — même patron que `547ad7a3ad02`). Migration appliquée (`alembic upgrade head` réussi, `9c1e2f4a7b3d` → `c2d3e4f5a6b7`).
- Fait : `ruff check .` clean sur tout le repo. Pas de test ajouté (régression pytest-asyncio du conteneur toujours non résolue, cf. entrées précédentes).

### 2026-09-02 (suite 7) — rappels waitlist récurrents (scheduler asyncio)
- Fait : le TODO front demandait des rappels récurrents après l'ouverture de la billetterie (aujourd'hui, un seul email à l'ouverture, jamais de relance) — bloqué jusqu'ici par l'absence de scheduler/tâche périodique côté back. Pas de nouvelle dépendance (APScheduler) ajoutée pour ça — une simple boucle `asyncio` en tâche de fond (`app/main.py`, `lifespan`) suffit : elle se réveille toutes les `WAITLIST_REMINDER_CHECK_INTERVAL_MINUTES` (60 par défaut) et appelle `send_waitlist_reminders()` (`app/services/waitlist_reminder.py`).
- Fait : `send_waitlist_reminders()` relance un email (`waitlist_reminder_email()`, `email_templates.py`) à tout inscrit `registered=False` déjà notifié une première fois (`notified=True`) dont `last_notified_at` date de plus de `WAITLIST_REMINDER_INTERVAL_DAYS` (3 par défaut) — no-op si la fenêtre `ticketing` n'est pas ouverte. Nouvelle colonne `waitlist.last_notified_at` (migration `d3e4f5a6b7c8`), mise à jour aussi bien au premier envoi (`admin_campaign_windows.py::_notify_waitlist`) qu'aux rappels suivants.
- Fait : migration appliquée (`alembic upgrade head`, `c2d3e4f5a6b7` → `d3e4f5a6b7c8`), `ruff check .` clean, `python -c "import app.main"` sans erreur (vérifie le câblage `lifespan`). Pas de test ajouté (régression pytest-asyncio du conteneur toujours non résolue).

### 2026-09-02 (suite 8) — `GET /api/event-settings` public
- Fait : côté front, `EventSettings` (nom+lieu) existait déjà en base et déjà éditable au dashboard (`admin_event_settings.py`, Phase I) mais aucune route publique ne l'exposait — le site public affichait toujours des valeurs codées en dur (`data/parameter.ts`) au lieu de la table pilotée par l'admin. Ajouté `GET /api/event-settings` (`app/api/public.py`), même patron que `GET /api/admin/event-settings` mais sans `require_permission` (donnée publique par nature) — réutilise `EventSettingsRead`/`EventSettings` (`app/models/referentials.py`) tels quels, aucun nouveau modèle/migration.
- Fait : `ruff check app/api/public.py` clean. Pas de test ajouté (régression pytest-asyncio du conteneur toujours non résolue).

### 2026-09-02 (suite 9) — `event_settings.year` nullable
- Fait : demande front — le texte de marque "Synca Conf &lt;année&gt;" apparaît à plusieurs endroits du site public, codé en dur ; il fallait un champ dédié pilotable au dashboard, distinct des dates de l'événement (`campaign_windows.event`) qui existaient déjà. Ajouté colonne `event_settings.year` (`Integer`, nullable — migration `e4f5a6b7c8d9`), exposée dans `EventSettingsRead`/`EventSettingsUpdate` (`app/schemas/referentials.py`) et donc automatiquement dans `GET /api/event-settings` (public, suite 8) et `GET/PATCH /api/admin/event-settings`.
- Fait : `PATCH /api/admin/event-settings` (`admin_event_settings.py`) distingue "champ `year` absent du body" de "champ explicitement remis à `null`" via `body.model_fields_set` — contrairement à `name`/`venue` (toujours requis, jamais effacables), `year` doit pouvoir repasser à `null` depuis le dashboard pour que le front n'affiche plus d'année.
- Fait : migration appliquée (`alembic upgrade head`, `d3e4f5a6b7c8` → `e4f5a6b7c8d9`), `ruff check .` clean sur tout le repo. Pas de test ajouté (régression pytest-asyncio du conteneur toujours non résolue).
