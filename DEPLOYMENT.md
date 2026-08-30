# Deployment — Bootstrap du compte admin (prod)

Ce document explique comment créer le premier superadmin **en production**.

## Principe

`app/cli/create_admin.py` est **exclu de l'image de production** (via
`.dockerignore`). Le script reste disponible dans la source (et dans l'image
de dev), mais n'est **pas** embarqué dans l'image `runtime` déployée sur le VPS.

Raison : c'est un levier d'administration (création d'un compte superadmin),
pas du code exposé par l'API. On applique le principe du moindre privilège —
l'image de prod ne contient que le code nécessaire au fonctionnement de l'API.

Le bootstrap se fait donc **ponctuellement**, depuis une machine de management
ou un conteneur jetable avec accès au réseau de la base — jamais via la
fonctionnalité de l'API elle-même.

## Avant de commencer

### 1. Variables d'environnement (dans `.env` sur le VPS, jamais commitées)

Le script lit `ADMIN_EMAIL` et `ADMIN_PASSWORD` depuis les settings (qui se
nourrissent du `.env`). Ces variables n'ont **aucune valeur par défaut** : le
script refuse de tourner si elles manquent.

```
ADMIN_EMAIL=superadmin@mon-domaine.com
ADMIN_PASSWORD=<mot de passe fort généré>
```

> ⚠️ **Politique de mot de passe** (voir `security-hardening` SKILL) :
> - minimum **12 caractères**
> - au moins une **minuscule**, une **majuscule**, un **chiffre**, un **symbole**
> - le script refusera (exit 1) un mot de passe qui ne les respecte pas
> - hachage **Argon2id** (via `hash_password`)

Génère un mot de passe fort, par exemple :
```
openssl rand -base64 18
```

### 2. Base de données à jour

Les tables `roles`, `admin_users` doivent exister. Applique les migrations si
ce n'est pas déjà fait.

## Créer le compte admin en prod

### Option A — Conteneur jetable (recommandé)

À partir du dossier du projet sur la machine de déploiement, avec `.env` chargé :

```bash
# depuis le VPS, dans le dossier du projet
docker compose run --rm app python3 -m app.cli.create_admin
```

`docker compose run --rm` crée un conteneur **temporaire** (non persistant),
qui partage le réseau compose et lit le même `.env`. Il ne modifie pas les
conteneurs qui tournent.

### Option B — Depuis une machine de management (hors conteneur)

Si tu préfères ne pas lancer de conteneur : le script n'est qu'un client de la
base. Depuis une machine avec Python et un accès réseau vers la DB MySQL :

```bash
# définit les variables utilisées par les settings
export ADMIN_EMAIL=superadmin@mon-domaine.com
export ADMIN_PASSWORD='<mot de passe fort>'
# pointe vers la base — voir app/core/config.py (database_url)
export DB_HOST=<ip-de-la-db>
export MYSQL_USER=syncaconf
export MYSQL_PASSWORD=<mot de passe app>
export MYSQL_DATABASE=syncaconf

python -m app.cli.create_admin
```

> Le conteneur `db` de production ne publie **aucun port** sur l'hôte (seul
> Caddy est internet-facing). L'accès se fait donc depuis le réseau interne
> compose (Option A) ou via un tunnel SSH contrôlé (Option B).

## Vérification

- Le script affiche `Compte créé : <email>`.
- Connecte-toi sur l'admin avec l'email + le mot de passe définis dans `.env`.
- **Change le mot de passe après le premier login** si nécessaire.

## Post-bootstrap

- Le `ADMIN_PASSWORD` reste dans `.env` tant que tu en as besoin
  (ré-exécution). Pour limiter la surface, retire-le ou vide-le une fois le
  compte créé — le script échouera proprement si on le relance sans lui.
- L'image de prod ne contient **pas** `app/cli/` : vérifiable avec
  `docker compose exec app ls app/cli` (doit retourner introuvable).

## Rappel sécurité du conteneur

Le vrai périmètre de confiance est le **daemon Docker du VPS**. Qui peut
exécuter `docker compose run/exec` sur ce host peut créer un admin, lire les
secrets du `.env`, ou accéder en base. Assure-toi que **seuls des
administrateurs de confiance** ont accès au VPS / au socket Docker. Un
conteneur ne peut pas être "sécurisé" contre quelqu'un qui possède le host.
