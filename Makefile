.PHONY: help up down restart build logs migrate seed admin curl-health swagger create-admin db-shell

DOCKER    := docker compose
APP       := $(DOCKER) exec app
DB        := $(DOCKER) exec db
API       := http://127.0.0.1:8010

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Lifecycle ──────────────────────────────────────────────

up: ## Lancer le backend (hot-reload)
	$(DOCKER) up -d --build
	@echo "\n  ✅ API : $(API)/docs\n"

down: ## Arrêter les conteneurs (données conservées)
	$(DOCKER) down

nuke: ## Arrêter ET supprimer le volume MySQL (reset total)
	$(DOCKER) down -v

restart: ## Redémarrer les conteneurs
	$(DOCKER) restart

logs: ## Afficher les logs en temps réel (Ctrl+C pour quitter)
	$(DOCKER) logs -f app

# ── Database ───────────────────────────────────────────────

migrate: ## Appliquer les migrations Alembic (tables + seed)
	$(APP) alembic upgrade head

db-shell: ## Ouvrir un shell MySQL sur la base syncaconf
	$(DB) mysql -uroot -p"$${MYSQL_ROOT_PASSWORD}" syncaconf

# ── Admin ──────────────────────────────────────────────────

create-admin: ## Créer un compte superadmin (admin@synca.conf / ChangeMe123!)
	$(APP) python3 -c "\
import asyncio; \
from app.core.database import AsyncSessionLocal; \
from app.core.security import hash_password; \
from app.models import AdminUser, Role; \
from sqlalchemy import select; \
async def main(): \
    async with AsyncSessionLocal() as db: \
        role = (await db.execute(select(Role).where(Role.name == 'superadmin'))).scalar_one(); \
        db.add(AdminUser(email='admin@synca.conf', password_hash=hash_password('ChangeMe123!'), role_id=role.id)); \
        await db.commit(); \
        print('Compte créé : admin@synca.conf / ChangeMe123!'); \
asyncio.run(main())"

login: ## Retourne un token admin (pour usage dans d'autres commandes)
	@curl -s -X POST $(API)/api/admin/login \
		-H "Content-Type: application/json" \
		-d '{"email":"admin@synca.conf","password":"ChangeMe123!"}'

# ── Quick checks ───────────────────────────────────────────

health: ## Vérifier que l'API répond
	@curl -s $(API)/health | python3 -m json.tool

swagger: ## Ouvrir Swagger dans le navigateur
	@open $(API)/docs

# ── Dev ────────────────────────────────────────────────────

build: ## Rebuild l'image Docker sans cache
	$(DOCKER) build --no-cache

shell: ## Shell dans le conteneur app (bash)
	$(APP) bash
