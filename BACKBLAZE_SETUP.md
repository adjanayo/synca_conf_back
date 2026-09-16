# Stockage fichiers — MinIO (défaut) + B2 (alternative)

Sans stockage fonctionnel, tout formulaire avec upload de fichier (photo
speaker, photo ambassadeur, logo partenaire, visuel exposant, photo membre
hackathon) échoue (503 "service de stockage indisponible").

## Backend par défaut : MinIO auto-hébergé

`STORAGE_BACKEND=minio` (défaut, dev **et** prod) — MinIO tourne dans son
propre conteneur (`docker-compose.yml` / `docker-compose.prod.yml`), avec un
volume Docker **nommé** (pas un bind-mount disque). Même code S3
(`app/services/storage.py`, `boto3`) que pour B2 — seuls l'endpoint et les
identifiants changent.

Pourquoi MinIO plutôt que B2 en défaut : rendre un bucket **public** en
lecture (nécessaire pour que les URLs de photos/logos s'affichent sur le
site) est un simple appel API gratuit sur MinIO auto-hébergé, alors que sur
le compte B2 utilisé pour ce projet c'est une fonctionnalité payante. Le
backend crée et rend le bucket public automatiquement au démarrage
(`ensure_minio_bucket_ready()`, appelé dans le `lifespan` de `app/main.py`) —
rien à faire manuellement.

**Dev** : le backend parle à MinIO en direct sur le réseau Docker interne
(`MINIO_ENDPOINT_URL=http://minio:9000`) et les fichiers sont servis via le
port hôte publié (`MINIO_PUBLIC_URL=http://localhost:9010`). Console web
MinIO : `make minio-console` (identifiants = `MINIO_ROOT_USER`/
`MINIO_ROOT_PASSWORD` du `.env`).

**Prod** : aucun port MinIO n'est publié sur l'hôte (`docker-compose.prod.yml`)
— Caddy route les requêtes fichiers en interne (`Caddyfile`, préfixe
`/<MINIO_BUCKET_NAME>/*` → `minio:9000`), donc `MINIO_PUBLIC_URL=https://<domaine>`.

Variables (`.env`, voir `.env.example`) :
```
STORAGE_BACKEND=minio
MINIO_ROOT_USER=<utilisateur admin>
MINIO_ROOT_PASSWORD=<mot de passe admin, généré aléatoirement>
MINIO_ENDPOINT_URL=http://minio:9000
MINIO_ACCESS_KEY=<= MINIO_ROOT_USER>
MINIO_SECRET_KEY=<= MINIO_ROOT_PASSWORD>
MINIO_BUCKET_NAME=synca-dev   # synca-prod sur le serveur Contabo
MINIO_PUBLIC_URL=http://localhost:9010   # https://<domaine> en prod
```

## Fallback sans conteneur : stockage local (`STORAGE_BACKEND=local`)

Écrit directement sur disque (`./uploads`, monté dans le conteneur `app`) et
sert les fichiers via `/uploads` (mount `StaticFiles`, `app/main.py`). Aucun
conteneur ni compte externe requis — utile pour CI/tests, mais plus le mode
actif par défaut nulle part.

## Alternative : Backblaze B2 (`STORAGE_BACKEND=b2`)

Gardé au cas où un compte B2 avec bucket public gratuit devient disponible.

⚠️ **Rendre un bucket B2 public peut être payant** selon le compte (le
toggle de visibilité a nécessité une vérification carte bancaire sur le
compte utilisé pour ce projet) — vérifier avant de basculer dessus.

### 1. Compte + buckets
1. Créer un compte sur https://www.backblaze.com/ (B2 Cloud Storage).
2. Créer **deux buckets** — un par environnement (`synca-dev`, `synca-prod`)
   — publics en lecture, puisque les URLs générées sont servies directement
   au front.
3. Dans "App Keys", générer une Application Key **par bucket** (accès limité
   à son propre bucket, sans `namePrefix` restrictif — sinon les objets
   générés par `_generate_key()` ne matcheront pas le préfixe et tout upload
   échouera en `AccessDenied`). Noter tout de suite l'`applicationKeyId` et
   l'`applicationKey` — cette dernière n'est affichée qu'une seule fois.

### 2. Variables
```
B2_ENDPOINT_URL=https://s3.<region>.backblazeb2.com
B2_KEY_ID=<applicationKeyId du bucket>
B2_APPLICATION_KEY=<applicationKey du bucket>
B2_BUCKET_NAME=<synca-dev ou synca-prod>
B2_PUBLIC_URL=<url publique du bucket ou du CDN devant>
```
- `B2_ENDPOINT_URL` et la région : visibles sur la page du bucket dans le
  dashboard B2 (ex. `https://s3.eu-central-003.backblazeb2.com`).
- `B2_PUBLIC_URL` : l'URL "Friendly URL" du bucket donnée par Backblaze, ou
  un domaine CDN si un CDN est mis devant le bucket.

## Redémarrer et vérifier

```
cd synca_conf_back
docker compose up -d
```

Soumettre un formulaire avec photo (ex. candidature speaker) et confirmer
qu'il n'y a plus de 503 et que la photo est bien accessible à l'URL renvoyée.
