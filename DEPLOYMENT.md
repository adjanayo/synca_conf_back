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

## Frontend Vercel — CORS et durcissement prod

Le frontend (`synca_conf_front`) est déployé sur Vercel, séparément de ce
backend (Hetzner + Docker Compose + Caddy). Checklist à traiter **avant** la
mise en prod, aucune n'est du code :

1. **`CORS_ORIGINS`** (`.env` prod, jamais commité) — remplacer les valeurs
   dev (`http://localhost:3000,http://localhost:5173`) par le(s) domaine(s)
   Vercel réel(s), ex. `https://syncaconf2027.com,https://www.syncaconf2027.com`.
   Décider explicitement si les URLs de preview Vercel (`*.vercel.app`,
   différentes à chaque déploiement) doivent aussi appeler l'API — si oui il
   faut soit lister un sous-ensemble fixe, soit accepter qu'elles ne
   fonctionnent pas contre la prod (recommandé : previews contre un backend
   de staging séparé, pas contre la prod). Toujours **sans wildcard** (voir
   `security-hardening` SKILL : "wildcard-free by design").
2. **`RECAPTCHA_SECRET_KEY`** — absent de `.env.example`, et
   `app/services/recaptcha.py` **désactive silencieusement** la vérification
   si la clé est vide (comportement voulu en dev/CI). En prod, une clé
   manquante désactive la protection anti-bot des formulaires publics
   **sans aucune erreur visible** — vérifier explicitement sa présence dans
   le `.env` de prod avant le déploiement, ce n'est pas rattrapable après coup
   sans y repenser.
3. **Rotation des secrets** — `JWT_SECRET_KEY` et `FERNET_KEY` du
   `.env.example` sont des valeurs de dev ; en générer de nouvelles pour la
   prod (commandes en commentaire dans `app/core/config.py`) avant le premier
   déploiement, jamais réutiliser les valeurs dev.
4. **Le frontend doit pointer sur l'API en HTTPS uniquement**
   (`VITE_API_URL` sur Vercel = domaine derrière Caddy, jamais l'IP du VPS en
   HTTP direct).
5. **CORS n'est pas la ligne de défense principale** — CORS bloque les
   appels navigateur cross-origin, pas un `curl`/script tiers qui appelle
   l'API directement. La vraie protection contre l'abus direct de l'API
   reste le rate limiting (`app/core/rate_limit.py`), reCAPTCHA (point 2) et
   la validation stricte des entrées (Pydantic) — ne pas considérer une
   whitelist CORS correcte comme suffisante à elle seule.

## Rappel sécurité du conteneur

Le vrai périmètre de confiance est le **daemon Docker du VPS**. Qui peut
exécuter `docker compose run/exec` sur ce host peut créer un admin, lire les
secrets du `.env`, ou accéder en base. Assure-toi que **seuls des
administrateurs de confiance** ont accès au VPS / au socket Docker. Un
conteneur ne peut pas être "sécurisé" contre quelqu'un qui possède le host.
