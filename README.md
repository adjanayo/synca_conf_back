# SYNCA CONF 2027 — Backend

Backend de la conférence tech panafricaine SYNCA CONF 2027 (18–20 août 2027, Dakar).

Réécriture en cours : **FastAPI + MySQL + RBAC**, backoffice inclus, mono-tenant (pas de SaaS multi-client). Stack optimisée pour tourner sur une petite VPS à coût minimal (~4,30€/mois tout compris).

## Documentation

- [`ROADMAP.md`](ROADMAP.md) — plan de construction détaillé en 10 phases (backend uniquement, hors frontend), jusqu'à la checklist de lancement production
- [`syncaconf/planning_fastapi.md`](syncaconf/planning_fastapi.md) — architecture, stack technique, RBAC, coûts, tuning ressources et déploiement
- [`syncaconf/schema.md`](syncaconf/schema.md) — schéma fonctionnel des tables, formulaires et endpoints, adapté MySQL (inclut fenêtres de campagne `campaign_windows` et formulaire exposants)
- [`syncaconf/securite.md`](syncaconf/securite.md) — exigences sécurité de référence (rédigées pour une implémentation Laravel, à réadapter à FastAPI)
- [`syncaconf/Infos.md`](syncaconf/Infos.md) — contraintes métier (steps de lancement, tarification)
- [`CLAUDE.md`](CLAUDE.md) — règles projet pour les agents IA (stack, conventions, workflow)

## Stack

- FastAPI (async) + SQLAlchemy 2.0 + Alembic
- MySQL 8 (tuning : `innodb_buffer_pool_size=256M`, `max_connections=50` sur la VPS ciblée)
- RBAC relationnel maison (rôles/permissions, pas de Casbin)
- Backoffice : **SQLAdmin** (nativement SQLAlchemy — pas FastAPI-Admin, qui dépend de Tortoise ORM et aurait doublé les dépendances ORM)
- Billets PDF : `reportlab` (pur Python, pas de dépendances système comme weasyprint)
- Pas de Redis/Celery : `BackgroundTasks` FastAPI suffisant à cette échelle
- Déploiement cible : Hetzner CX11 (2 Go RAM) + Docker Compose (image `python:3.12-slim`, build multi-stage) + Caddy, 1 seul worker Uvicorn — détails dans `syncaconf/planning_fastapi.md`

## Statut

Phase de conception. Voir la checklist de validation dans `syncaconf/planning_fastapi.md` et le détail des phases dans `ROADMAP.md`.
