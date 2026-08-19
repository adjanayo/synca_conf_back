# SYNCA CONF 2027 — Planning Backend FastAPI (RBAC + Backoffice + MySQL)

> Réécriture du backend (Laravel/PostgreSQL → FastAPI/MySQL)

---

## ⚠️ Écarts à trancher avant de lancer

- Docs sources (`schema.md`, `securite.md`) sont écrites pour **Laravel + PostgreSQL**. `CLAUDE.md` du projet impose aussi PostgreSQL + isolation multi-tenant (`SET LOCAL app.current_tenant`).
- Demande actuelle : **MySQL**, site d'événement mono-tenant (pas de SaaS multi-client ici).
- Plan ci-dessous : **FastAPI + MySQL + RBAC classique (pas de tenant isolation)**. À trancher : mettre à jour `CLAUDE.md` en conséquence, sinon il reste en contradiction avec le stack réel.

---

## 1. Stack technique

| Composant | Choix |
|---|---|
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) + Alembic (migrations) |
| DB | MySQL 8 |
| Validation | Pydantic v2 |
| Auth | JWT (access + refresh) via `python-jose` / `authlib` |
| RBAC | Rôles/permissions maison en table pivot (décidé — voir §2) |
| Backoffice | **SQLAdmin** (décidé — voir §2, révisé) |
| Génération PDF billet | `reportlab` (pur Python, pas de dépendances système) |
| Upload fichiers | Backblaze B2 (compatible S3, tier gratuit 10 Go) |
| Emails | Resend (tier gratuit 3000/mois) |
| Paiement | Stripe + Wave/Orange Money (webhooks signés) |
| Queue/async jobs | FastAPI `BackgroundTasks` — pas de Redis/Celery, aucun service supplémentaire à faire tourner |
| Rate limiting | `slowapi` (clone Flask-Limiter pour FastAPI, en mémoire — pas de backend Redis requis) |
| Tests | pytest + pytest-asyncio + httpx AsyncClient |
| Reverse proxy / HTTPS | Caddy (auto Let's Encrypt, gratuit, léger) |
| Conteneurisation | Docker multi-stage build, image `python:3.12-slim` |
| Monitoring | UptimeRobot (gratuit) + Sentry (tier gratuit 5k events/mois) |

---

## 2. Modèle RBAC (décidé)

Plutôt que rôle unique en `enum` sur `admin_users` (comme dans `securite.md`), RBAC relationnel maison — **pas de Casbin** : à cette échelle (4 rôles), Casbin ajoute une dépendance et une courbe d'apprentissage pour zéro bénéfice réel, et n'a aucun coût d'infra propre de toute façon donc le seul gain de l'écarter est la simplicité/temps de dev.

```
roles (id, name)               -- superadmin, admin, editor, support
permissions (id, code)         -- speakers.approve, partners.manage, payments.view...
role_permissions (role_id, permission_id)
admin_users (id, email, password_hash, role_id, ...)
```

- Dependency FastAPI `require_permission("speakers.approve")` réutilisable sur chaque route admin.

### Backoffice — révisé : SQLAdmin (pas FastAPI-Admin)

Décision initiale (FastAPI-Admin) corrigée après vérification de sa dépendance réelle : **FastAPI-Admin est bâti sur Tortoise ORM**, pas SQLAlchemy. L'utiliser aurait fait tourner deux ORM en parallèle dans la même app (SQLAlchemy pour l'API, Tortoise pour l'admin) — plus de dépendances installées, plus de RAM consommée, deux façons différentes de parler à MySQL à maintenir. Contraire à l'objectif de minimiser les ressources.

**[SQLAdmin](https://github.com/aminalaee/sqladmin)** retenu à la place : admin interface conçue nativement pour SQLAlchemy + Starlette/FastAPI. Mêmes bénéfices que la décision initiale (un seul service à builder/héberger, pas de SPA séparée, pas d'hébergement statique additionnel) sans le coût du double-ORM — elle réutilise directement les modèles SQLAlchemy déjà écrits pour l'API.

---

## 3. Planning de conception (8 sprints, ~1 semaine chacun — ajustable selon disponibilité)

### Sprint 0 — Setup (2-3j)
- Repo, structure FastAPI (`app/api`, `app/models`, `app/schemas`, `app/core`, `app/services`)
- Docker Compose (FastAPI + MySQL + Adminer pour debug)
- CI basique (lint + tests) via GitHub Actions
- Alembic init

### Sprint 1 — Modèles & migrations
- Traduire `schema.md` (PostgreSQL) → modèles SQLAlchemy MySQL (attention: `ENUM` MySQL natif au lieu de `CHECK`, `JSON` pour `social_handles`, `TEXT`/`VARCHAR` limites identiques)
- Migrations Alembic pour toutes les tables (days, sessions, pass_types, users, promo_codes, payments, tickets, waitlist, speakers, ambassadors, partners, faqs, contact_messages, admin_users, roles, permissions)

### Sprint 2 — Auth & RBAC
- JWT login admin (`/api/admin/login`) + refresh token
- Dependencies RBAC (`require_permission`)
- Rate limiting login (`slowapi`, 5/min)
- Hash password: `passlib[bcrypt]` ou `argon2-cffi`

### Sprint 3 — Endpoints publics (lecture)
- `/api/days`, `/api/sessions`, `/api/pass-types`, `/api/speakers`, `/api/partners`, `/api/faqs`
- Filtres/pagination

### Sprint 4 — Formulaires publics (écriture)
- `/api/register`, `/api/waitlist`, `/api/contact`, `/api/newsletter`
- `/api/speakers/apply`, `/api/ambassadors/apply`, `/api/partners/apply`
- Validation Pydantic stricte + reCAPTCHA v3 + upload photo/logo (validation MIME réelle)
- Emails transactionnels (accusé réception, confirmation)

### Sprint 5 — Paiement & billetterie
- `/api/payments` (init) + `/api/payments/webhook` (vérif signature, idempotence)
- Génération ticket (QR code + PDF avec `reportlab` — pur Python, pas de Pango/Cairo comme weasyprint) après `status=completed`
- `/api/promo/validate`

### Sprint 6 — Backoffice admin (SQLAdmin)
- CRUD statuts (speakers/ambassadors/partners/exhibitors: pending→accepted/rejected/confirmed) via vues SQLAdmin sur les modèles SQLAlchemy existants
- `/api/admin/stats` dashboard
- Audit log des actions admin (table `audit_logs` + middleware)

### Sprint 7 — Sécurité & durcissement
- Headers sécurité (middleware CSP/HSTS/X-Frame-Options via `starlette` middleware custom)
- CORS restreint au domaine frontend
- RGPD: `/api/user/me` GET + DELETE (anonymisation)
- Logs séparés (security.log, payment.log) — `structlog` ou `loguru`

### Sprint 8 — Tests, déploiement, monitoring
- Suite pytest (auth, RBAC, paiement, webhooks)
- Déploiement (voir §4)
- Sentry (erreurs) + uptime monitor
- Backup MySQL automatisé (cron `mysqldump` → S3/B2)

---

## 4. Déploiement (décidé — coût minimal)

**Hetzner CX11 (2 Go RAM, ~3,29€/mois) + Docker Compose + Caddy**, sans Coolify.

Pourquoi ce changement vs une première option avec Coolify :
- Coolify consomme lui-même une part significative de la RAM d'une petite VPS — en le retirant, la CX11 (moitié moins chère que la CX22) suffit.
- **Caddy** remplace Nginx + Coolify pour le HTTPS : reverse proxy + certificats Let's Encrypt automatiques, config minimale, gratuit.
- Déploiement via **GitHub Actions** (SSH + `docker compose pull && up -d`) — gratuit (minutes CI incluses dans le tier gratuit GitHub).
- MySQL en conteneur sur la même VPS, backup quotidien (`mysqldump` → Backblaze B2).

| Service | Tier retenu | Coût |
|---|---|---|
| VPS Hetzner CX11 | 2 vCPU, 2 Go RAM | ~3,29 €/mois |
| Stockage fichiers (Backblaze B2) | Free tier 10 Go + 1 Go/jour egress | 0 € |
| Emails (Resend) | Free tier 3000/mois | 0 € |
| Monitoring uptime (UptimeRobot) | Free | 0 € |
| Erreurs (Sentry) | Free tier 5k events/mois | 0 € |
| CI/CD (GitHub Actions) | Free tier | 0 € |
| Nom de domaine | — | ~8-12 €/an (~1 €/mois amorti) |
| **Total** | | **~4,30 €/mois** |

Si le trafic dépasse ces free tiers (peu probable pour un seul événement), seul un palier payant Backblaze/Resend serait à absorber — coûts marginaux, pas de refonte d'archi nécessaire.

Options écartées et pourquoi :
- Railway/Render : ~15-25$/mois pour une config équivalente — 5x plus cher, sans gain fonctionnel ici.
- Fly.io : free tier limité et moins prévisible que Hetzner à budget fixe.
- Coolify : confort d'UI de déploiement, mais coûte de la RAM qu'on préfère garder pour l'appli sur une petite VPS.

### Tuning ressources sur la CX11 (2 Go RAM) — pour ne pas swapper/OOM

- **Uvicorn : 1 seul worker** (`--workers 1`), pas de Gunicorn multi-worker — le trafic d'un événement (pics ponctuels d'inscription, pas de charge continue) ne justifie pas plus, et chaque worker supplémentaire duplique la mémoire de l'app.
- **MySQL** : `innodb_buffer_pool_size=256M` (au lieu du défaut souvent proportionnel à la RAM totale), `max_connections=50` — largement suffisant pour un backend mono-instance, évite qu'InnoDB réserve trop de mémoire par défaut.
- **Image Docker multi-stage** (`python:3.12-slim` en base, dépendances de build jetées dans le stage final) — image plus petite = moins de RAM/disque au démarrage, déploiements plus rapides.
- **Pas de service applicatif superflu** : ni Redis, ni Celery worker, ni Node.js pour un build de backoffice — SQLAdmin est rendu server-side par FastAPI lui-même.
- Marge RAM restante sur 2 Go avec ce tuning : confortable pour Caddy + OS + pics ponctuels (webhooks paiement, génération PDF).

---

## Checklist de validation

- [x] MySQL confirmé — `CLAUDE.md` mis à jour (PostgreSQL/multi-tenant retiré)
- [x] RBAC maison (table pivot) retenu — pas de Casbin
- [x] Backoffice: **SQLAdmin** retenu (révisé depuis FastAPI-Admin — incompatibilité ORM, voir §2) — pas de SPA dédiée
- [x] Déploiement : Hetzner CX11 + Docker Compose + Caddy (sans Coolify) — ~4,30€/mois tout compris
- [x] Ressources : 1 worker Uvicorn, MySQL `innodb_buffer_pool_size` réduit, image Docker multi-stage, zéro service superflu (pas de Redis/Celery)
