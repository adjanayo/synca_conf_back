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

*(Les étapes suivantes seront ajoutées ici au fur et à mesure de leur implémentation.)*
