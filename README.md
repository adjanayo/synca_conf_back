# SYNCA CONF 2027 — Backend

Backend de la conférence tech panafricaine SYNCA CONF 2027 (18–20 août 2027, Dakar).

Réécriture en cours : **FastAPI + MySQL + RBAC**, backoffice inclus, mono-tenant (pas de SaaS multi-client).

## Documentation

- [`syncaconf/planning_fastapi.md`](syncaconf/planning_fastapi.md) — architecture, stack technique, RBAC, planning en sprints, coûts et option de déploiement
- [`syncaconf/schema.md`](syncaconf/schema.md) — schéma fonctionnel des tables, formulaires et endpoints (à adapter de PostgreSQL vers MySQL, voir plan)
- [`syncaconf/securite.md`](syncaconf/securite.md) — exigences sécurité de référence (rédigées pour une implémentation Laravel, à réadapter à FastAPI)
- [`syncaconf/Infos.md`](syncaconf/Infos.md) — contraintes métier (steps de lancement, tarification)
- [`CLAUDE.md`](CLAUDE.md) — règles projet pour les agents IA (stack, conventions, workflow)

## Stack

- FastAPI (async) + SQLAlchemy 2.0 + Alembic
- MySQL 8
- RBAC relationnel maison (rôles/permissions, pas de Casbin)
- Backoffice : FastAPI-Admin
- Déploiement cible : Hetzner CX11 + Docker Compose + Caddy (~4,30€/mois, détails dans `syncaconf/planning_fastapi.md`)

## Statut

Phase de conception. Voir la checklist de validation dans `syncaconf/planning_fastapi.md`.
