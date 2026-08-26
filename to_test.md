# TO_TEST — SYNCA CONF 2027 Backend

> Checklist de test manuel, étape par étape, en miroir de `ROADMAP.md`.
> Statut par étape : `[ ]` à tester / `[x]` validé.

---

## Phase 0 — Bootstrap & tooling

### 0.1 — Structure repo + squelette FastAPI

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

1. Tests automatisés :
   ```bash
   pytest tests/test_health.py -v
   ```
   → attendu : `1 passed`.

2. Démarrage réel du serveur :
   ```bash
   uvicorn app.main:app --reload
   ```
   → dans un autre terminal :
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   → attendu : `{"status":"ok"}`.

3. Docs actives en dev (`ENVIRONMENT=local` par défaut) :
   ```bash
   curl -o /dev/null -s -w "%{http_code}\n" http://127.0.0.1:8000/docs
   ```
   → attendu : `200`.

4. Docs désactivées en production (vérification anticipée de 7.4) :
   ```bash
   ENVIRONMENT=production uvicorn app.main:app --port 8001 &
   curl -o /dev/null -s -w "%{http_code}\n" http://127.0.0.1:8001/docs
   ```
   → attendu : `404`.

- [x] 0.1 validé — `pytest` vert, serveur répond sur `/health`, `/docs` conditionnel à `ENVIRONMENT`.

---

### 0.2 — Docker Compose dev (FastAPI + MySQL 8, 2 services seulement)

```bash
cp .env.example .env   # si pas déjà fait
docker compose up -d --build
```

1. Vérifier que seuls 2 services tournent, tous les deux `healthy`/`running` :
   ```bash
   docker compose ps
   ```
   → attendu : `app` et `db` uniquement (pas d'Adminer/Mailpit/Sentry/Redis).

2. Santé de l'app à travers le conteneur :
   ```bash
   curl http://127.0.0.1:8010/health
   ```
   → attendu : `{"status":"ok"}`.
   (Port hôte `8010` choisi pour éviter les conflits avec d'autres projets locaux sur `8000` — configurable dans `docker-compose.yml`.)

3. Logs sans erreur :
   ```bash
   docker compose logs app --tail 50
   ```
   → attendu : aucune erreur au démarrage.

4. Nettoyage :
   ```bash
   docker compose down
   ```

- [x] 0.2 validé — `docker compose up` démarre exactement 2 services (`app`, `db`), `db` healthy avant que `app` ne démarre (`depends_on: condition: service_healthy`), `/health` répond à travers le conteneur.

---

### 0.3 — Dockerfile multi-stage strict

```bash
docker build --target runtime -t synca-app:runtime .
docker run --rm synca-app:runtime id
docker history synca-app:runtime --no-trunc
docker images synca-app:runtime --format "{{.Size}}"
```

1. `id` dans le conteneur → attendu : `uid=999(app) gid=999(app)`, jamais root.
2. `docker history` → aucun `gcc`/`build-essential` ajouté par **notre** Dockerfile dans le stage final (le stage `builder` seul les installe, jamais copié dans `runtime`).
3. Taille : la mesure bloquante se fait en CI sur `linux/amd64` (cible de production réelle) — voir job `image-size` dans `.github/workflows/ci.yml` (0.7). Une build locale sur Mac arm64 n'est pas représentative (le `python:3.12-slim` de base pèse déjà ~205 Mo sur arm64 contre nettement moins sur amd64).

- [x] 0.3 validé (non-root + multi-stage confirmés localement ; seuil de taille vérifié en CI amd64, voir 0.7).

---

### 0.4 — `mem_limit` + logs bornés (docker-compose.prod.yml)

> En local, si les ports 80/443 sont déjà pris par un autre projet, mapper temporairement `caddy` sur `8080:80`/`8443:443` dans un `docker-compose.override.yml` (déjà dans `.gitignore`, jamais commité) — remettre `80:80`/`443:443` avant tout déploiement réel.

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker stats --no-stream --format "{{.Name}} {{.MemUsage}}"
```

1. Attendu : `app` plafonné à 600MiB, `db` à 800MiB, `caddy` à 100MiB (colonne "MemUsage / Limit").
2. `curl` à travers Caddy (ou le port override en local) → `{"status":"ok"}`.
3. `docker compose -f docker-compose.prod.yml logs caddy --tail 20` → reverse proxy actif, pas d'erreur bloquante (le warning "no automatic HTTPS" est normal tant que `DOMAIN` n'est pas un vrai domaine public, voir 0.8).
4. Nettoyage : `docker compose -f docker-compose.prod.yml down`.

- [x] 0.4 validé — 3 services (`app`/`db`/`caddy`) démarrent avec les `mem_limit` corrects et logs `json-file` bornés (`max-size=10m,max-file=3`), `/health` accessible via Caddy.

---

### 0.5 — `.env.example` aligné avec `app/core/config.py`

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt   # sqlalchemy[asyncio], asyncmy, alembic ajoutés
pytest tests/test_health.py -v
python3 -c "from app.core.config import get_settings; print(get_settings().database_url)"
```

1. Attendu : `pytest` toujours vert (config DB n'affecte pas `/health`).
2. `database_url` construit correctement : `mysql+asyncmy://syncaconf:change-me-app@db:3306/syncaconf` (valeurs par défaut = celles de `.env.example`).
3. Rebuild Docker pour confirmer qu'`asyncmy` (extension C) compile dans le stage `builder` :
   ```bash
   docker compose build app --no-cache
   ```
   → attendu : build vert, pas d'erreur de compilation.

- [x] 0.5 validé — `.env.example` et `Settings` cohérents, `asyncmy`/`sqlalchemy`/`alembic` installés et buildables en conteneur.

---

### 0.6 — Alembic init + première migration (vide)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1   # depuis l'hôte, le port MySQL du conteneur est publié sur 3306
alembic upgrade head
```

1. Attendu : `Running upgrade  -> <rev>, initial (empty)`, aucune erreur.
2. Vérifier la table de suivi Alembic :
   ```bash
   docker compose exec db mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "USE syncaconf; SHOW TABLES;"
   ```
   → attendu : `alembic_version`.
3. Réversibilité :
   ```bash
   alembic downgrade base && alembic upgrade head
   ```
   → attendu : les deux sans erreur.
4. `docker compose build app` → toujours vert avec `cryptography` ajouté (requis par `asyncmy` pour `caching_sha2_password`, l'auth par défaut de MySQL 8).
5. Nettoyage : `docker compose down`.

- [x] 0.6 validé — pipeline Alembic (async, `mysql+asyncmy`) fonctionnel de bout en bout contre un vrai MySQL 8.4.

---

### 0.7 — CI GitHub Actions (lint + tests + scan image Trivy)

Reproduction locale de `.github/workflows/ci.yml` :

```bash
source .venv/bin/activate
ruff check .
docker compose up -d db
export DB_HOST=127.0.0.1
alembic upgrade head
pytest -v
docker compose down
```

→ attendu : `ruff` sans violation, migration verte, `1 passed`.

Vérification propre à la CI (nécessite un push, `ubuntu-latest` = amd64 natif) :
1. Job `lint-and-test` : service MySQL 8.4 éphémère, mêmes étapes que ci-dessus.
2. Job `image-scan` : build `--target runtime` sur runner amd64 (la mesure de taille fiable, contrairement au Mac arm64 local, cf. 0.3), échoue si > 200 Mo, puis scan Trivy (`HIGH`/`CRITICAL` non corrigés → échec du pipeline).
3. Sur GitHub : `Actions` → dernier run sur `dev` → les deux jobs verts.

- [x] 0.7 validé — historique des allers-retours CI :
  1. Run 1 : image 266 Mo (base `python:3.12-slim`) → corrigé en passant à `python:3.12-alpine` + retrait `uvicorn[standard]` + suppression `pip`/`setuptools` du stage `runtime`.
  2. Run 2 : image 144 Mo ✓, mais Trivy bloque sur 2 CVE `HIGH` (`starlette` 0.52.1, SSRF/vol credentials NTLM via UNC + limites `request.form()` ignorées) — `fastapi==0.128.8` plafonnait `starlette<1.0.0`. Root cause : `pip index versions` (pip système obsolète 21.2.4) donnait des numéros de version périmés pour `fastapi`/`starlette`/`uvicorn` etc. → revérifié via l'API PyPI JSON (`pypi.org/pypi/<pkg>/json`), bien plus fiable.
  3. Correctif : `fastapi==0.141.1` (accepte `starlette>=0.46.0`, sans plafond) + `starlette==1.6.0` épinglé explicitement + `uvicorn==0.52.4`, `pydantic-settings==2.15.0`, `alembic==1.19.1`, `pytest==9.1.1`, `pytest-asyncio==1.4.0`. Revalidé en local (`ruff`, `pytest`, `docker compose up` + `/health`).
  - **Leçon retenue** : pour toute vérification de version future sur ce projet, utiliser `curl https://pypi.org/pypi/<pkg>/json | jq .info.version`, pas `pip index versions` sur ce Mac (pip système trop ancien).

---

### 0.8 — Caddyfile (headers sécurité, reverse proxy, HTTPS auto)

```bash
docker run --rm -e DOMAIN=":80" \
  -v "$(pwd)/Caddyfile:/etc/caddy/Caddyfile:ro" \
  caddy:2.11.4-alpine caddy validate --config /etc/caddy/Caddyfile
```
→ attendu : `Valid configuration`.

```bash
docker compose -f docker-compose.prod.yml up -d --build
curl -sI http://127.0.0.1/health   # ou le port mappé localement si 80/443 déjà pris
```

1. Attendu : `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` tous présents ; pas de header `Server` (retiré via `-Server`) ; `Via: 1.1 Caddy` (normal, ne fuite pas de version).
2. `curl http://.../health` (GET, pas HEAD) → `{"status":"ok"}`.
3. **HTTPS avec certificat valide (Let's Encrypt automatique) : non testable en local.** Caddy n'émet un certificat que pour un domaine public résolvable avec le port 443 accessible depuis Internet — nécessite le vrai déploiement VPS (`DOMAIN=votredomaine.com` dans `.env` de prod). À vérifier lors du premier déploiement réel (voir 0.9/checklist Phase 10) : `curl -I https://votredomaine.com/health` → certificat valide, pas d'avertissement navigateur.
4. Nettoyage : `docker compose -f docker-compose.prod.yml down`.

- [x] 0.8 validé pour tout ce qui est testable sans domaine public/VPS réel (syntaxe, headers, reverse proxy). Le test HTTPS/certificat réel reste une vérification de déploiement, pas de dev local — inscrit dans la checklist Phase 10.

---

### 0.9 — CD GitHub Actions (déploiement sur push `main`)

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"
```
→ attendu : pas d'erreur (YAML valide).

**Non testable sans VPS réel** — nécessite avant tout premier déploiement :
1. Une VPS provisionnée (Hetzner CX11, voir `syncaconf/planning_fastapi.md` §3) avec le repo cloné dans `/opt/synca-conf-back` et un `.env` de prod en place.
2. Trois secrets GitHub configurés (`Settings → Environments → production`) : `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` (clé privée dédiée, jamais la clé perso).
3. Un push sur `main` déclenche le job → vérifier sur la VPS : `docker compose -f docker-compose.prod.yml ps` montre les 3 services à jour, `curl https://votredomaine.com/health` répond après coup.

- [x] 0.9 validé pour ce qui est testable maintenant (YAML valide, secrets/script cohérents avec `docker-compose.prod.yml`). Le déploiement réel reste à vérifier au premier `push` sur `main`, une fois la VPS provisionnée — inscrit dans la checklist Phase 10.

---

## Phase 1 — Modèle de données

### 1.1 — Référentiels (`days`, `pass_types`, `partner_levels`, `faq_categories`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_referentials.py -v
```

1. Attendu : migration appliquée, `3 passed` (unicité `date` sur `days` testée via `IntegrityError`, défauts `PassType.max_days=3`/`is_active=True` vérifiés, insertion `PartnerLevel`/`FaqCategory` basique).
2. Réversibilité : `alembic downgrade base && alembic upgrade head` → sans erreur.
3. `docker compose down` pour nettoyer.

- [x] 1.1 validé.

---

### 1.2 — Utilisateurs & profils (`users`, `user_profiles`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_users.py -v
```
→ attendu : `2 passed` (unicité `email` testée, unicité `(user_id, profile)` testée).

- [x] 1.2 validé.

---

### 1.3 — Programme (`sessions`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_sessions.py -v
```
→ attendu : `1 passed` (filtre par `day_id` + `category` testé).

Note technique (à surveiller sur toutes les prochaines migrations) : le `downgrade()` auto-généré par Alembic tente parfois de `DROP INDEX` sur un index qui porte encore une FK — MySQL refuse. Correctif appliqué : `downgrade()` fait un simple `op.drop_table(...)` (qui gère lui-même FK + index), plutôt que les `drop_index` individuels générés automatiquement.

- [x] 1.3 validé.

---

### 1.4 — Paiement & billetterie (`promo_codes`, `payments`, `tickets`, `waitlist`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_payments.py -v
```
→ attendu : `4 passed` (FK invalide rejetée, `status` par défaut `pending`, un seul ticket par paiement (`UniqueConstraint(payment_id)`), unicité `waitlist.email`).

- [x] 1.4 validé.

---

### 1.5 — Candidatures (`speakers`, `ambassadors`, `partners`, `exhibitors`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_applications.py -v
```
→ attendu : `6 passed` (statut par défaut `pending`/`is_public=False`, transition de workflow speaker (`pending→accepted`+`is_public=True`), `social_handles` JSON round-trip, FK `partners.level_id` invalide rejetée, workflow partenaire complet `pending→contacted→negotiating→confirmed`, exposant par défaut `pending`/non public).

Vérifie aussi que la FK `sessions.speaker_id → speakers.id` (posée en attente depuis 1.3) a bien été ajoutée : `alembic check` → `No new upgrade operations detected.`

- [x] 1.5 validé.

---

### 1.6 — Contenu & contact (`faqs`, `contact_messages`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_content.py -v
```
→ attendu : `2 passed` (CRUD complet `Faq` — create/read/update/delete — et `ContactMessage.is_read=False` par défaut).

- [x] 1.6 validé.

---

### 1.7 — RBAC (`roles`, `permissions`, `role_permissions`, `admin_users`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
docker compose exec db mysql -uroot -p"$MYSQL_ROOT_PASSWORD" \
  -e "USE syncaconf; SELECT name FROM roles; SELECT COUNT(*) FROM permissions; SELECT COUNT(*) FROM role_permissions;"
pytest tests/test_rbac.py -v
```
→ attendu : 4 rôles (`superadmin`, `admin`, `editor`, `support`), 8 permissions de base seedées par la migration, `superadmin` lié aux 8 (le détail fin des permissions par rôle sera affiné en Phase 2). `2 passed`.

- [x] 1.7 validé.

---

### 1.8 — Fenêtres de campagne (`campaign_windows`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_campaign_windows.py -v
```
→ attendu : `2 passed` (5 fenêtres seedées avec des dates placeholder — à ajuster via le back-office en Phase 6.4 —, contrainte `end_at > start_at` rejette une mise à jour invalide avec `DBAPIError` (MySQL renvoie une `OperationalError` pour un `CHECK` violé, pas une `IntegrityError`)).

- [x] 1.8 validé.

---

### 1.9 — Index (`schema.md` §1)

Tous les index listés dans `schema.md` §1 ont déjà été posés au fil des migrations 1.1-1.8 (`index=True`/`unique=True` sur les colonnes concernées : `users.email`, `sessions.day_id`/`category`, `payments.user_id`/`status`, `tickets.user_id`/`ticket_number`, `speakers`/`ambassadors`/`partners`/`exhibitors.status`, `partners.level_id`, `campaign_windows.key`). Cette étape est une vérification, pas une nouvelle migration.

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
docker compose exec db mysql -uroot -p"$MYSQL_ROOT_PASSWORD" syncaconf -e "
EXPLAIN SELECT * FROM users WHERE email = 'x@example.com';
EXPLAIN SELECT * FROM payments WHERE status = 'pending';
EXPLAIN SELECT * FROM sessions WHERE day_id = 1 AND category = 'workshop';
"
```
→ attendu : colonne `key` renseignée (`ix_users_email`, `ix_payments_status`, `ix_sessions_category`/`ix_sessions_day_id`), jamais `type=ALL` (full scan) sur ces requêtes. Avec au moins une ligne en table, une recherche par égalité sur une colonne `UNIQUE` (`email`, `ticket_number`) doit donner `type=const`.

- [x] 1.9 validé — tous les index présents et effectivement utilisés par l'optimiseur MySQL.

---

### 1.10 — Schémas Pydantic pour toutes les tables

```bash
source .venv/bin/activate
pytest tests/test_schemas.py -v
```
→ attendu : `11 passed` — un schéma `*Read` (Pydantic v2, `from_attributes=True`) par table de la Phase 1, validé par sérialisation depuis une instance ORM construite en mémoire (pas besoin de DB pour ce test, contrairement aux autres). Vérifie notamment que `AdminUserRead` n'expose jamais `password_hash`.

Suite complète (avec DB, base fraîche pour éviter tout résidu d'une vérification manuelle précédente) :
```bash
docker compose up -d db
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/ -v
```
→ attendu : `34 passed`.

⚠️ Si des tests échouent avec des erreurs `Duplicate entry` sur des valeurs comme `'Standard'`, c'est un résidu de données insérées manuellement (ex. session `mysql -e "INSERT ..."` pour un `EXPLAIN`) qui persiste dans le volume `mysql_data` même après `docker compose down` (sans `-v`, le volume survit). Nettoyer avec `docker compose down -v` puis remigrer.

- [x] 1.10 validé — Phase 1 (modèle de données) complète.

---

## Phase 2 — Auth & RBAC

### 2.1 — Hash mots de passe (Argon2id via `argon2-cffi`)

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/test_security.py -v
docker compose build app
```
→ attendu : `2 passed` (hash différent du mot de passe en clair, vérification correcte accepte/rejette), build Docker toujours vert avec `argon2-cffi` (extension C compilée dans le stage `builder` alpine).

- [x] 2.1 validé.

---

### 2.2 — JWT access + refresh (`PyJWT`)

```bash
source .venv/bin/activate
pytest tests/test_auth_service.py -v
```
→ attendu : `5 passed`, aucun warning (`JWT_SECRET_KEY` par défaut ≥ 32 octets pour HS256). Couvre : round-trip access/refresh, rejet d'un token du mauvais type, rejet d'un token expiré, rejet d'une signature invalide.

- [x] 2.2 validé.

---

### 2.3 — `POST /api/admin/login` (rate limit IP + verrouillage compte)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_admin_login.py -v
```
→ attendu : `5 passed` — connexion réussie renvoie une paire de tokens, mot de passe erroné **et** email inconnu renvoient le **même** `401 "Email ou mot de passe incorrect."` (anti-énumération, hash factice comparé même si le compte n'existe pas), 6ᵉ requête/minute depuis la même IP → `429`, 5 échecs consécutifs sur le même compte → `AccountLockedError` même avec le bon mot de passe ensuite.

⚠️ Amendement de portée (voir ROADMAP.md 2.3) : le rate limit `slowapi` 0.1.x ne peut pas combiner IP+email (son `key_func` n'est pas awaité), donc il est appliqué **par IP seule** ; la protection par compte est assurée séparément par le verrouillage (`app/services/auth_service.py`), qui lui est bien par email.

Vérification via conteneur :
```bash
docker compose up -d --build
curl -X POST http://127.0.0.1:8010/api/admin/login -H "Content-Type: application/json" -d '{"email":"ghost@synca.conf","password":"x"}'
```
→ attendu : `{"detail":"Email ou mot de passe incorrect."}`.

- [x] 2.3 validé.

---

### 2.4 — Dependency `require_permission(code)`

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_rbac_deps.py -v
```
→ attendu : `5 passed` — `get_current_admin` résout un token valide, rejette (401) un token absent/invalide ; `require_permission(code)` laisse passer si le rôle a la permission (via `role_permissions`), renvoie 403 sinon.

En passant : `tests/test_auth_service.py::test_invalid_signature_rejected` était flaky (le dernier caractère base64url d'une signature JWT ne change pas toujours les octets décodés après un flip) — corrigé pour altérer le caractère du milieu de la signature à la place. Vérifié stable sur 5 runs répétés.

- [x] 2.4 validé.

---

### 2.5 — Endpoints RBAC admin (`PATCH /api/admin/roles/:id`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_admin_rbac.py -v
```
→ attendu : `4 passed` — un `superadmin` (permission `roles.manage`, seedée en 1.7) peut remplacer les permissions d'un rôle ; un admin sans cette permission → `403` ; requête non authentifiée → `401` ; code de permission inconnu dans le body → `400`.

- [x] 2.5 validé.

---

### 2.6 — Audit log connexions (`audit_logs`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_audit_log.py -v
```
→ attendu : `3 passed` — une entrée `audit_logs` créée à chaque tentative de connexion : succès (`success=True`, IP enregistrée), échec (`success=False`), et compte verrouillé (chacune des 5 tentatives + la 6ᵉ bloquée par le verrou = 6 entrées, toutes `success=False`).

Note d'implémentation : journalisation faite directement dans `authenticate_admin()` (qui connaît l'issue métier), pas via un middleware Starlette générique qui ne verrait qu'un statut HTTP sans le détail (compte verrouillé / mauvais mot de passe / email inconnu).

- [x] 2.6 validé — Phase 2 (Auth & RBAC) complète.

---

## Phase 3 — Endpoints publics (lecture)

### 3.1 — Jours & programme (`GET /api/days`, `GET /api/sessions?day=&category=`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_public_program.py -v
```
→ attendu : `4 passed` — `/api/days` trié par date (et cas vide), `/api/sessions` filtré par `day`+`category` **et** ne renvoie jamais une session `is_public=false`, cas vide géré.

Dépendance de pagination partagée (`app/deps/pagination.py`, `limit`/`offset`) introduite ici car `/api/sessions` en a besoin ; réutilisée par tous les endpoints de liste suivants (3.3-3.6) — formalisée/testée isolément en 3.8.

- [x] 3.1 validé.

---

### 3.2 — Pass (`GET /api/pass-types`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_public_pass_types.py -v
```
→ attendu : `2 passed` (les pass `is_active=false` ne fuitent jamais, cas vide géré).

- [x] 3.2 validé.

---

### 3.3 — Speakers publics (`GET /api/speakers?theme=&format=`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_public_speakers.py -v
```
→ attendu : `2 passed` (filtre `theme`+`format` combiné, un speaker `is_public=false` ne fuite jamais même s'il correspond aux filtres ; cas vide géré).

- [x] 3.3 validé.

---

### 3.4 — Partenaires publics (`GET /api/partners?level=`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_public_partners.py -v
```
→ attendu : `2 passed` (filtre `level`, exclusion des partenaires `is_public=false`, cas vide).

- [x] 3.4 validé.

---

### 3.5 — Exposants publics (`GET /api/exhibitors`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_public_exhibitors.py -v
```
→ attendu : `2 passed` (exclusion des exposants `is_public=false`, cas vide). `is_public=true` est appliqué sans condition — pas de mode "afficher les privés" sur un endpoint public.

- [x] 3.5 validé.

---

### 3.6 — FAQ (`GET /api/faqs?category=`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_public_faqs.py -v
```
→ attendu : `2 passed` (filtre par `category`, tri par `sort_order`, cas vide).

- [x] 3.6 validé.

---

### 3.7 — Fenêtres de campagne (`GET /api/campaign-windows`)

```bash
docker compose up -d db
source .venv/bin/activate
export DB_HOST=127.0.0.1
alembic upgrade head
pytest tests/test_public_campaign_windows.py -v
```
→ attendu : `1 passed` (les 5 fenêtres seedées en 1.8 sont exposées, triées par `start_at`). Rien de sensible dans cette table — pas de filtrage nécessaire.

- [x] 3.7 validé.

---

*(Les étapes suivantes seront ajoutées ici au fur et à mesure de leur implémentation.)*
