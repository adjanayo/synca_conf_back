.PHONY: help up down restart build logs migrate seed admin curl-health swagger create-admin db-shell backup restore migrate-export migrate-import

DOCKER    := docker compose
APP       := $(DOCKER) exec app
DB        := $(DOCKER) exec db
API       := http://127.0.0.1:8010
BACKUP_DIR := backups
STAMP      := $(shell date +%Y%m%d-%H%M%S)

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
	$(APP) python3 -m app.cli.create_admin

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

# ── Backup & migration ────────────────────────────────────

backup: ## Dump la base MySQL dans backups/ (horodaté)
	@mkdir -p $(BACKUP_DIR)
	$(DB) sh -c 'exec mysqldump -uroot -p"$$MYSQL_ROOT_PASSWORD" --single-transaction --routines --triggers syncaconf' > $(BACKUP_DIR)/syncaconf-$(STAMP).sql
	@echo "\n  ✅ Backup : $(BACKUP_DIR)/syncaconf-$(STAMP).sql\n"

restore: ## Restaurer un dump (usage: make restore FILE=backups/xxx.sql)
	@test -n "$(FILE)" || (echo "Usage: make restore FILE=backups/xxx.sql" && exit 1)
	cat $(FILE) | $(DB) sh -c 'exec mysql -uroot -p"$$MYSQL_ROOT_PASSWORD" syncaconf'
	@echo "\n  ✅ Restauré depuis $(FILE)\n"

migrate-export: backup ## Préparer une archive de migration (dump DB + .env) vers backups/
	@tar -czf $(BACKUP_DIR)/migration-$(STAMP).tar.gz -C $(BACKUP_DIR) syncaconf-$(STAMP).sql -C .. .env
	@echo "\n  ✅ Archive de migration : $(BACKUP_DIR)/migration-$(STAMP).tar.gz"
	@echo "     Copier ce fichier sur le nouveau serveur puis lancer 'make migrate-import ARCHIVE=...'\n"

migrate-import: ## Importer une archive de migration sur le nouveau serveur (usage: make migrate-import ARCHIVE=migration-xxx.tar.gz)
	@test -n "$(ARCHIVE)" || (echo "Usage: make migrate-import ARCHIVE=backups/migration-xxx.tar.gz" && exit 1)
	@mkdir -p $(BACKUP_DIR)/import-$(STAMP)
	tar -xzf $(ARCHIVE) -C $(BACKUP_DIR)/import-$(STAMP)
	@cp $(BACKUP_DIR)/import-$(STAMP)/.env .env
	$(MAKE) up
	$(MAKE) migrate
	$(DOCKER) up -d db
	@sleep 5
	cat $(BACKUP_DIR)/import-$(STAMP)/*.sql | $(DB) sh -c 'exec mysql -uroot -p"$$MYSQL_ROOT_PASSWORD" syncaconf'
	@echo "\n  ✅ Import terminé depuis $(ARCHIVE)\n"
