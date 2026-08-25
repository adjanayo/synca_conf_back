# ROADMAP — SYNCA CONF 2027 Backend

> Backend seul (FastAPI + MySQL + RBAC + backoffice). Aucun scope frontend.
> Principe de sobriété : 3 conteneurs en production (FastAPI, MySQL, Caddy), aucun outil optionnel (pas d'Adminer/Mailpit/Sentry/Redis/Celery), une seule dépendance par besoin (PyJWT, argon2-cffi, loguru) — détail dans `syncaconf/planning_fastapi.md` §3.
> Document vivant : toute nouvelle portée ou correction de trajectoire se fait ici, avant implémentation (cf. `change-control`, `quality-engineer`).
> Statuts par étape : ⬜ `Not Started` / 🚧 `In Progress` / ✅ `Test Done`. Une étape ✅ `Test Done` ne se retouche que pour un vrai bug ou une demande explicite (voir `.claude/skills/change-control/SKILL.md`).
> Stack et coûts détaillés : `syncaconf/planning_fastapi.md`.

---

## Phase 0 — Bootstrap & tooling

| # | Étape | Livrable | Vérification | Statut |
|---|---|---|---|---|
| 0.1 | Structure repo `app/api`, `app/models`, `app/schemas`, `app/core`, `app/services`, `app/deps`, `tests/` | Squelette FastAPI qui démarre | `uvicorn app.main:app --reload` répond sur `/health` | ✅ Test Done |
| 0.2 | Docker Compose dev — **2 services seulement : FastAPI + MySQL 8.** Pas d'Adminer, pas de Mailpit : debug DB via `docker compose exec mysql mysql`, emails en dev loggés par `loguru` (backend console, pas d'envoi réel) | `docker-compose.yml` | `docker compose up` → 2 services healthy, aucun conteneur superflu | ✅ Test Done |
| 0.3 | Dockerfile multi-stage strict (`builder` → `python:3.12-slim` final), non-root, `requirements.txt` runtime séparé de `requirements-dev.txt`, `.dockerignore` | `Dockerfile`, `.dockerignore` | image finale < 200 Mo, `docker history` ne montre aucun compilateur/header résiduel | ✅ Test Done* |
| 0.4 | `docker-compose.yml` : `mem_limit` par service (app 600M / db 800M / caddy 100M en prod), logs `json-file` `max-size=10m,max-file=3` | `docker-compose.yml`, `docker-compose.prod.yml` | `docker stats` confirme les limites appliquées | ✅ Test Done |
| 0.5 | `.env.example` réécrit pour FastAPI/MySQL (pas Postgres/Redis/MinIO) | fichier à la racine | valeurs cohérentes avec `app/core/config.py` | ⬜ Not Started |
| 0.6 | Alembic init + première migration (tables vides) | `alembic/` | `alembic upgrade head` sans erreur | ✅ Test Done |
| 0.7 | CI GitHub Actions (lint + tests + scan image Trivy) | `.github/workflows/ci.yml` | pipeline vert sur push, 0 vulnérabilité `HIGH`/`CRITICAL` non traitée sur l'image buildée | 🚧 In Progress — vert localement, run GitHub à confirmer au push |
| 0.8 | Caddyfile (domaine, HTTPS auto, headers sécurité de base, reverse proxy vers `app`) | `Caddyfile` | `docker compose -f docker-compose.prod.yml up` sert en HTTPS avec cert valide | ⬜ Not Started |
| 0.9 | CD GitHub Actions : déploiement sur push `main` (SSH vers la VPS, `docker compose pull && up -d`) | `.github/workflows/deploy.yml` | déploiement effectif observé sur la VPS après un push | ⬜ Not Started |
| 0.10 | `TESTING.md` créé (statuts par étape, source de vérité pour `change-control`) | fichier racine | référencé par ce roadmap | ✅ Fait via `to_test.md` |

\* 0.3 : non-root confirmé, multi-stage confirmé (compilateurs présents uniquement dans le stage `builder`, jamais copiés dans `runtime`). Taille mesurée localement sur build natif arm64 (Mac dev) = 289 Mo, au-dessus de la cible car `python:3.12-slim` lui-même pèse ~205 Mo sur arm64. La cible de production est amd64 (Hetzner) où l'image officielle est nettement plus légère : la mesure définitive et bloquante se fait dans la CI (0.7), qui build pour `linux/amd64` et vérifie le seuil réel.

---

## Phase 1 — Modèle de données (MySQL)

Traduction de `syncaconf/schema.md` (écrit pour PostgreSQL) vers SQLAlchemy 2.0 / MySQL : `ENUM` natif MySQL au lieu de `CHECK`, `JSON` pour les champs multi-valeurs (`social_handles`), tailles `VARCHAR` conservées.

| # | Étape | Tables | Vérification | Statut |
|---|---|---|---|---|
| 1.1 | Référentiels | `days`, `pass_types`, `partner_levels`, `faq_categories` | migration + seed de test | ⬜ Not Started |
| 1.2 | Utilisateurs & profils | `users`, `user_profiles` | contrainte unicité email testée | ⬜ Not Started |
| 1.3 | Programme | `sessions` (FK `days`, `speakers` posé en 1.5) | filtre par jour/catégorie testé | ⬜ Not Started |
| 1.4 | Paiement & billetterie | `promo_codes`, `payments`, `tickets`, `waitlist` | FK et contraintes `status` testées | ⬜ Not Started |
| 1.5 | Candidatures | `speakers`, `ambassadors`, `partners`, `exhibitors` | workflow `status` (`pending→...`) testé | ⬜ Not Started |
| 1.6 | Contenu & contact | `faqs`, `contact_messages` | CRUD basique testé | ⬜ Not Started |
| 1.7 | RBAC | `roles`, `permissions`, `role_permissions`, `admin_users` (rôle relationnel, pas un `enum` unique sur la colonne) | seed des 4 rôles + permissions de base | ⬜ Not Started |
| 1.8 | Fenêtres de campagne | `campaign_windows` (`call_for_speaker`, `ticketing`, `call_for_partner`, `call_for_ambassador`, `call_for_exhibitor`), seed avec dates par défaut | `end_at > start_at` contraint et testé | ⬜ Not Started |
| 1.9 | Index | tous les index listés dans `schema.md` §1 | `EXPLAIN` sur requêtes chaudes (liste inscriptions, recherche email) | ⬜ Not Started |
| 1.10 | Modèles SQLAlchemy + schémas Pydantic pour toutes les tables ci-dessus | `app/models/*.py`, `app/schemas/*.py` | tests de sérialisation | ⬜ Not Started |

---

## Phase 2 — Auth & RBAC

| # | Étape | Détail | Vérification | Statut |
|---|---|---|---|---|
| 2.1 | Hash mots de passe : `argon2-cffi` (Argon2id) | `app/core/security.py` | test hash/verify | ⬜ Not Started |
| 2.2 | JWT access + refresh token : `PyJWT` | `app/services/auth_service.py` | test expiration, signature invalide rejetée | ⬜ Not Started |
| 2.3 | `POST /api/admin/login` | rate limit `slowapi` 5/min par email+IP | test brute-force bloqué | ⬜ Not Started |
| 2.4 | Dependency `require_permission(code)` | `app/deps/rbac.py` | test 403 si permission manquante | ⬜ Not Started |
| 2.5 | Endpoints RBAC admin (gestion rôles/permissions) | `PATCH /api/admin/roles/:id` | test superadmin seul autorisé | ⬜ Not Started |
| 2.6 | Audit log connexions (succès/échec) | table `audit_logs` + middleware | entrée créée à chaque login | ⬜ Not Started |

---

## Phase 3 — Endpoints publics (lecture)

| # | Étape | Endpoint | Statut |
|---|---|---|---|
| 3.1 | Jours & programme | `GET /api/days`, `GET /api/sessions?day=&category=` | ⬜ Not Started |
| 3.2 | Pass | `GET /api/pass-types` | ⬜ Not Started |
| 3.3 | Speakers publics | `GET /api/speakers?theme=&format=` (filtre `is_public=true`) | ⬜ Not Started |
| 3.4 | Partenaires publics | `GET /api/partners?level=` (filtre `is_public=true`) | ⬜ Not Started |
| 3.5 | Exposants publics | `GET /api/exhibitors?public=true` (filtre `is_public=true`) | ⬜ Not Started |
| 3.6 | FAQ | `GET /api/faqs?category=` | ⬜ Not Started |
| 3.7 | Fenêtres de campagne | `GET /api/campaign-windows` (dates + statut, pour affichage frontend) | ⬜ Not Started |
| 3.8 | Pagination/tri commun | dependency partagée `app/deps/pagination.py` | ⬜ Not Started |

Vérification : tests pour chaque filtre + cas vide, et confirmation qu'aucune donnée `is_public=false` ne fuite.

---

## Phase 4 — Formulaires publics (écriture)

| # | Étape | Endpoint | Points d'attention |
|---|---|---|---|
| 4.1 | Waitlist | `POST /api/waitlist` | email unique, toujours ouvert (pas de fenêtre de campagne) |
| 4.2 | Inscription participant | `POST /api/register` | gardé par fenêtre `ticketing` (4.11), valide `pass_type_id` actif, `promo_code` si fourni, `gdpr_consent=true` obligatoire |
| 4.3 | Candidature speaker | `POST /api/speakers/apply` | gardé par fenêtre `call_for_speaker` (4.11), upload photo (MIME réel + `Pillow` pour vérifier que c'est une vraie image), `status=pending` |
| 4.4 | Candidature ambassadeur | `POST /api/ambassadors/apply` | gardé par fenêtre `call_for_ambassador` (4.11), si accepté plus tard → génération `promo_code` unique (Phase 6) |
| 4.5 | Candidature partenaire | `POST /api/partners/apply` | gardé par fenêtre `call_for_partner` (4.11), upload logo, workflow `pending→contacted→negotiating→confirmed|rejected` |
| 4.6 | Candidature exposant | `POST /api/exhibitors/apply` | gardé par fenêtre `call_for_exhibitor` (4.11), upload visuels, mêmes workflow/statuts que partenaires |
| 4.7 | Contact | `POST /api/contact` | reCAPTCHA v3 obligatoire |
| 4.8 | Newsletter | `POST /api/newsletter` | opt-in séparé, pas de doublon |
| 4.9 | reCAPTCHA v3 partagé | `app/services/recaptcha.py` | seuil score configurable (0.5 par défaut) |
| 4.10 | Upload fichiers → Backblaze B2 | `app/services/storage.py` | renommage UUID+timestamp, jamais le nom original |
| 4.11 | Dependency `require_open_campaign(key)` | `app/deps/campaign_windows.py` — vérifie `NOW() BETWEEN start_at AND end_at AND is_active=true` | 403 explicite hors fenêtre, testé fenêtre ouverte/fermée/désactivée |
| 4.12 | Emails transactionnels (Resend) | accusé réception, confirmation inscription | prod : envoi réel Resend ; dev : backend console `loguru` (email loggé, pas envoyé) — pas de conteneur SMTP de test |

---

## Phase 5 — Paiement & billetterie

| # | Étape | Détail |
|---|---|---|
| 5.1 | `POST /api/payments` | crée `payments.status=pending`, calcule remise promo |
| 5.2 | `POST /api/promo/validate` | vérifie actif, non expiré, non épuisé |
| 5.3 | Webhooks Stripe / Wave / Orange Money | vérification signature obligatoire (HMAC/secret), sinon 401 |
| 5.4 | Idempotence webhook | ne jamais traiter deux fois le même `transaction_ref` |
| 5.5 | Transaction atomique paiement + génération ticket | `DB.transaction()` équivalent SQLAlchemy (`async with session.begin()`) |
| 5.6 | Génération billet PDF + QR code | `qrcode` + `reportlab` (pur Python — pas de `weasyprint`, qui traîne Pango/Cairo/GDK-Pixbuf, trop lourd pour la VPS ciblée), upload B2 → `pdf_url` |
| 5.7 | Email billet | envoi post-génération |
| 5.8 | Logs paiement séparés | canal `payment` dédié (succès + échecs), rétention longue |

Vérification critique : test qu'un webhook rejoué (même `transaction_ref`) ne génère pas 2 tickets, test signature invalide → 401 + log `security`.

---

## Phase 6 — Backoffice admin (SQLAdmin, natif SQLAlchemy — voir `syncaconf/planning_fastapi.md` §2)

| # | Étape | Détail |
|---|---|---|
| 6.1 | Intégration SQLAdmin sur les modèles SQLAlchemy existants | vues CRUD auto pour `speakers`, `ambassadors`, `partners`, `exhibitors`, `contact_messages` |
| 6.2 | Actions custom workflow statut | `PATCH /api/admin/speakers/:id`, `/ambassadors/:id`, `/partners/:id`, `/exhibitors/:id` — protégées par `require_permission` |
| 6.3 | Génération auto `promo_code` à l'acceptation d'un ambassadeur | déclenché depuis l'action d'acceptation |
| 6.4 | Gestion des fenêtres de campagne | `GET /api/admin/campaign-windows`, `PATCH /api/admin/campaign-windows/:key` — modifier dates + `is_active`, réservé `superadmin`/`admin` |
| 6.5 | `GET /api/admin/stats` | dashboard : inscriptions, revenus, taux conversion promo, candidatures par statut |
| 6.6 | `GET /api/admin/registrations`, `/contacts` | listing filtrable/paginé |
| 6.7 | Export CSV (inscriptions, paiements) | réservé `superadmin` via `require_permission("export.data")` |
| 6.8 | Droit d'accès RGPD | `GET /api/user/me`, `DELETE /api/user/me` (anonymisation, pas suppression physique — conserve les tickets pour audit) |

---

## Phase 7 — Sécurité & durcissement

| # | Étape | Détail |
|---|---|---|
| 7.1 | CORS restreint au domaine frontend uniquement | `app/main.py` |
| 7.2 | Headers sécurité HTTP | CSP, HSTS (prod uniquement), X-Frame-Options, X-Content-Type-Options, Referrer-Policy — middleware Starlette custom |
| 7.3 | Rate limiting global + par endpoint sensible | `slowapi` : 60/min public, 30/min admin, 5/min login, 3/min formulaires publics |
| 7.4 | **Verrouillage documentation API en production** | voir section dédiée ci-dessous |
| 7.5 | Validation stricte de toutes les entrées | Pydantic v2 partout, aucun endpoint sans schéma de requête typé |
| 7.6 | Protection upload | MIME réel + vérif image, taille max (5 Mo photo, 10 Mo logo), stockage hors serveur web (B2) |
| 7.7 | Secrets | `.env` hors repo, jamais commité, utilisateur DB dédié à privilèges limités (pas root) |
| 7.8 | Chiffrement PII sensible si besoin | `cryptography.Fernet` sur champs identifiés (à confirmer selon champs réellement sensibles) |
| 7.9 | Revue sécurité | passer `security-review`/`security-hardening` sur le diff de chaque étape auth/paiement/PII avant `Test Done` |

### 7.4 — Documentation API non publique en production

Exigence explicite : `/docs`, `/redoc`, `/openapi.json` **ne doivent pas être accessibles à tout le monde en production**.

Approche retenue (coût zéro, cohérente avec `ENVIRONMENT` déjà prévu dans le config app) :
- `ENVIRONMENT=production` → FastAPI démarre avec `docs_url=None, redoc_url=None, openapi_url=None` (désactivation totale, personne n'y accède, même pas l'équipe depuis l'extérieur).
- `ENVIRONMENT=local`/`staging` → docs actives normalement pour le dev.
- Si l'équipe a quand même besoin de consulter les docs interactives en prod : les exposer sur un chemin non standard (`/internal/docs`) protégé par **Basic Auth au niveau Caddy** (`basicauth` directive, gratuit, pas de dépendance supplémentaire) plutôt que de les rouvrir publiquement. Par défaut : désactivées, à activer seulement si un besoin réel apparaît.
- La documentation complète du projet (Phase 9) ne dépend pas de `/docs` exposé — elle vit dans `docs/` versionné et n'est jamais servie publiquement.

---

## Phase 8 — Observabilité & exploitation

| # | Étape | Outil |
|---|---|---|
| 8.1 | Logs structurés séparés (`security`, `payment`, `app`) | `loguru` uniquement, rotation quotidienne (90j `security`, 365j `payment`) |

**Événements à logguer (8.1)** — table de référence pour l'implémentation :

| Événement | Canal | Niveau |
|---|---|---|
| Connexion admin réussie / échouée | `security` | `info` / `warning` |
| Création/modification d'un compte admin | `security` | `info` |
| Paiement réussi / échoué | `payment` | `info` / `warning` |
| Webhook signature invalide | `security` | `warning` |
| Rate limit déclenché | `security` | `warning` |
| 403 / 401 répétés | `security` | `warning` |
| Upload fichier échoué | `security` | `warning` |

| # | Étape | Outil |
|---|---|---|
| 8.2 | Erreurs applicatives | Couvertes par les logs `loguru` (8.1) — pas de Sentry, pas de SDK/service SaaS supplémentaire (voir `syncaconf/planning_fastapi.md` §3) |
| 8.3 | Monitoring uptime | UptimeRobot (gratuit) sur `/health` — seul service externe conservé, poll externe donc zéro empreinte sur la VPS |
| 8.4 | Backup MySQL automatisé | cron `mysqldump` quotidien → Backblaze B2, rétention 30j — seule donnée d'état réellement sur la VPS (fichiers déjà externalisés sur B2, voir 4.10) |
| 8.5 | Procédure de restauration testée **sur un hôte différent** | restaurer le dump B2 sur une VPS/conteneur MySQL neuf (pas la même instance) — c'est ça qui prouve que le backup est exploitable, pas juste qu'il existe |
| 8.6 | Alerting basique | webhook UptimeRobot → email ou canal notif |
| 8.7 | Tuning ressources VPS (2 Go RAM) | Uvicorn 1 worker, MySQL `innodb_buffer_pool_size=256M` + `max_connections=50`, zéro service superflu (Redis/Celery/Node/Adminer/Mailpit/Sentry) — détail dans `syncaconf/planning_fastapi.md` §3 |
| 8.8 | Limites mémoire + logs Docker bornés (vérifié : `docker stats` + `du -sh /var/lib/docker/containers/*` sous contrôle) | `mem_limit` par service (app 600M/db 800M/caddy 100M), `json-file` `max-size=10m,max-file=3` |
| 8.9 | Vérification mémoire sous charge | `docker stats` pendant un test de charge simulant un pic d'ouverture billetterie — pas de swap déclenché |
| 8.10 | **Dry-run migration vers un nouveau serveur** | provisionner une VPS Hetzner neuve, `git clone` + `docker compose up`, restaurer le dump B2 (8.5), copier `.env` depuis le gestionnaire de secrets (jamais depuis l'ancien serveur en clair), basculer le domaine — chronométré, pour connaître le temps d'indisponibilité réel avant d'en avoir besoin en urgence |

---

## Phase 9 — Documentation complète (livrable final)

Objectif : à la fin du projet, toute la connaissance nécessaire pour reprendre, exploiter ou auditer le backend existe en dehors de la tête de qui l'a codé. Rien de tout ça n'est exposé publiquement (voir 7.4).

| # | Document | Contenu | Chemin |
|---|---|---|---|
| 9.1 | Référence API | export OpenAPI figé (`openapi.json`) + guide de lecture, généré à chaque release | `docs/API.md`, `docs/openapi.json` |
| 9.2 | Modèle de données | schéma MySQL final (ERD texte ou image), différences vs `schema.md` d'origine | `docs/DATA_MODEL.md` |
| 9.3 | RBAC | matrice rôles × permissions, comment ajouter un rôle/permission | `docs/RBAC.md` |
| 9.4 | Sécurité | checklist reconstituée pour ce projet (remplace l'ancien `SECURITY_CHECKLIST.md` générique supprimé) — CORS, headers, rate limiting, upload, webhooks, RGPD | `docs/SECURITY.md` |
| 9.5 | Déploiement & migration serveur | runbook pas-à-pas : provisioning Hetzner, Docker Compose, Caddy, variables d'env, premier déploiement, rollback, **+ section dédiée "changer de serveur"** (provisioning nouvelle VPS, restauration MySQL depuis B2, où récupérer/régénérer chaque secret, bascule DNS + réémission cert Caddy, ordre des étapes pour minimiser la coupure) | `docs/DEPLOYMENT.md` |
| 9.6 | Exploitation / runbook incident | que faire si : webhook paiement en échec, DB down, backup corrompu, clé API expirée | `docs/RUNBOOK.md` |
| 9.7 | Variables d'environnement | référence complète de chaque variable, obligatoire/optionnelle, où l'obtenir | `docs/ENVIRONMENT.md` |
| 9.8 | Journal des décisions | pourquoi MySQL et pas Postgres, pourquoi RBAC maison et pas Casbin, pourquoi Hetzner et pas Railway — déjà amorcé dans `syncaconf/planning_fastapi.md`, à consolider ici | `docs/DECISIONS.md` |
| 9.9 | `README.md` racine tenu à jour | pointe vers tous les documents ci-dessus | racine |

Accès : `docs/` reste dans le repo Git (accès = accès repo, donc déjà restreint à l'équipe). Aucun de ces documents n'est publié sur un site accessible publiquement.

---

## Phase 10 — Checklist de lancement production

- [ ] Toutes les étapes des Phases 0-9 en `Test Done`
- [ ] `ENVIRONMENT=production`, docs API désactivées (7.4) confirmé par test manuel (`curl https://.../docs` → 404)
- [ ] CORS restreint au domaine réel du frontend
- [ ] Webhooks paiement testés en conditions réelles (sandbox → live)
- [ ] Backup MySQL vérifié fonctionnel + restauration testée **sur un hôte différent** (8.5)
- [ ] Dry-run migration vers un nouveau serveur effectué au moins une fois, temps d'indisponibilité mesuré (8.10)
- [ ] UptimeRobot actif et alertant réellement (test d'une fausse alerte)
- [ ] `docs/` complet et à jour (Phase 9)
- [ ] Domaine + certificat HTTPS (Caddy) validés
- [ ] Charge basique testée (nombre d'inscriptions attendu en pic d'ouverture billetterie)
- [ ] Ressources VPS confirmées sous le budget : 1 worker Uvicorn, `innodb_buffer_pool_size` réduit, `docker compose ps` = **exactement** FastAPI + MySQL + Caddy, rien de plus
- [ ] `mem_limit` actifs sur les 3 services, `docker stats` sous les seuils (§3 de `syncaconf/planning_fastapi.md`), logs Docker bornés (`max-size`/`max-file`)
- [ ] Image `app` en production < 200 Mo, aucune dépendance de build/dev résiduelle (`docker history synca-app:latest` propre)

---

## Notes de séquencement

- Frontend explicitement hors scope de ce roadmap — uniquement les endpoints et contrats de données que le frontend consommera.
- Ordre Phase 4 avant Phase 5 : les formulaires de candidature (speaker/ambassadeur/partenaire) n'ont pas de dépendance paiement, ils peuvent avancer en parallèle de la Phase 5 si plusieurs personnes travaillent dessus.
- Phase 9 (documentation) n'est pas repoussée à la toute fin dans la pratique : chaque phase alimente son document au fur et à mesure (ex. RBAC.md rempli dès la Phase 2, pas attendu jusqu'à la Phase 9) — la Phase 9 est le point de consolidation/relecture finale, pas le seul moment où on écrit.
