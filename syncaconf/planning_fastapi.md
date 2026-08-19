# SYNCA CONF 2027 — Planning Backend FastAPI (RBAC + Backoffice + MySQL)

> Backend mono-tenant, hors frontend. Principe directeur : le strict nécessaire, rien d'optionnel, coût minimal. Détail des phases : `ROADMAP.md`.

---

## 1. Stack technique

| Composant | Choix |
|---|---|
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| DB | MySQL 8 |
| Validation | Pydantic v2 |
| Auth | JWT via **PyJWT** |
| Hash mots de passe | **argon2-cffi** (Argon2id) |
| RBAC | Rôles/permissions maison en table pivot (§2) — pas de Casbin |
| Backoffice | **SQLAdmin** — natif SQLAlchemy (§2) |
| PDF billet | `reportlab` (pur Python) |
| Upload fichiers | Backblaze B2 (S3-compatible, free tier 10 Go) |
| Emails | Resend (free tier 3000/mois) ; dev = log console via `loguru`, aucun envoi réel |
| Paiement | Stripe + Wave/Orange Money (webhooks signés) |
| Jobs async | `BackgroundTasks` FastAPI — pas de Redis/Celery |
| Rate limiting | `slowapi` (en mémoire) |
| Logs | **loguru** |
| Tests | pytest + pytest-asyncio + httpx AsyncClient |
| Reverse proxy / HTTPS | Caddy |
| Conteneurisation | Docker multi-stage, `python:3.12-slim`, non-root (§3) |
| Monitoring | UptimeRobot (poll externe, zéro empreinte VPS) |

**Production : 3 conteneurs, exactement — `app` (FastAPI), `db` (MySQL), `caddy`.** Aucun outil de debug/monitoring supplémentaire ne tourne en continu (pas d'Adminer, Mailpit, Sentry, Redis).

---

## 2. RBAC & Backoffice (décidé)

```
roles (id, name)               -- superadmin, admin, editor, support
permissions (id, code)         -- speakers.approve, partners.manage, payments.view...
role_permissions (role_id, permission_id)
admin_users (id, email, password_hash, role_id, ...)
```

- Dependency FastAPI `require_permission("speakers.approve")` sur chaque route admin.
- Backoffice : **SQLAdmin**, pas FastAPI-Admin — celui-ci dépend de Tortoise ORM, incompatible avec la stack SQLAlchemy (aurait fait tourner deux ORM en parallèle). SQLAdmin réutilise directement les modèles existants, un seul service à héberger, pas de SPA séparée.

---

## 3. Déploiement & ressources (décidé)

**Hetzner CX11 (2 vCPU, 2 Go RAM, ~3,29€/mois) + Docker Compose + Caddy.**

| Service | Tier | Coût |
|---|---|---|
| VPS Hetzner CX11 | 2 Go RAM | ~3,29 €/mois |
| Backblaze B2 | Free tier 10 Go | 0 € |
| Resend | Free tier 3000/mois | 0 € |
| UptimeRobot | Free | 0 € |
| GitHub Actions | Free tier | 0 € |
| Domaine | — | ~1 €/mois amorti |
| **Total** | | **~4,30 €/mois** |

### Tuning VPS (2 Go RAM)

- Uvicorn : **1 seul worker** (pas de Gunicorn multi-worker).
- MySQL : `innodb_buffer_pool_size=256M`, `max_connections=50`.
- Aucun service superflu (Redis, Celery, Node — SQLAdmin est rendu server-side par FastAPI).

### Images & conteneurs Docker

- Build **multi-stage strict** : stage `builder` compile les wheels, stage final `python:3.12-slim` ne copie que le nécessaire — aucun compilateur/header dans l'image livrée.
- `requirements.txt` (runtime) séparé de `requirements-dev.txt` — les deps de dev/test ne sont jamais installées dans l'image finale.
- `.dockerignore` (`.git/`, `tests/`, `docs/`, `__pycache__/`, `.venv/`), `pip install --no-cache-dir`, utilisateur **non-root**, versions d'image épinglées (jamais `latest`).
- Cible : image `app` < 200 Mo.
- `mem_limit` par service : `app` 600 Mo, `db` 800 Mo, `caddy` 100 Mo (~1,5 Go contraints sur 2 Go dispo, marge pour l'OS).
- Logs Docker bornés (`json-file`, `max-size=10m`, `max-file=3`) ; rotation applicative `loguru` (90j `security`, 365j `payment`).

---

## Checklist de validation

- [x] MySQL + mono-tenant confirmé (`CLAUDE.md` à jour)
- [x] RBAC maison (pas de Casbin), backoffice SQLAdmin (pas de FastAPI-Admin/SPA)
- [x] Déploiement Hetzner CX11 + Docker Compose + Caddy — ~4,30€/mois tout compris
- [x] Une seule dépendance par besoin : PyJWT, argon2-cffi, loguru, reportlab, slowapi
- [x] 3 conteneurs en prod, pas un de plus (pas d'Adminer/Mailpit/Sentry/Redis/Celery/Coolify)
- [x] Image Docker multi-stage < 200 Mo, non-root, versions épinglées
- [x] `mem_limit` par conteneur + logs Docker bornés
