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

*(Les étapes suivantes seront ajoutées ici au fur et à mesure de leur implémentation.)*
