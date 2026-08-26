# Guide d'intégration Frontend — SYNCA CONF 2027 API

> État au 26/08/2026 : Phases 0-3 du `ROADMAP.md` terminées (bootstrap, modèle de données, auth/RBAC, endpoints publics de lecture). Les formulaires publics d'écriture (Phase 4) sont en cours — voir la section « Ce qui n'est pas encore disponible » plus bas.

## 1. Lancer le backend avec Docker

Prérequis : Docker + Docker Compose.

```bash
git clone <url-du-repo>
cd synca_conf_back
cp .env.example .env
docker compose up -d --build
```

Ça démarre 2 conteneurs : `app` (FastAPI, hot-reload activé) et `db` (MySQL 8.4). Le port hôte de l'API dans `docker-compose.yml` est **8010** (choisi pour éviter un conflit avec d'autres projets locaux sur 8000 — changez `"8010:8000"` dans `docker-compose.yml` si besoin).

Appliquer les migrations (tables + données de seed : rôles/permissions RBAC, fenêtres de campagne) :

```bash
docker compose exec app alembic upgrade head
```

Vérifier que tout tourne :

```bash
curl http://127.0.0.1:8010/health
# {"status":"ok"}
```

Documentation interactive (Swagger) tant que `ENVIRONMENT=local` (valeur par défaut de `.env.example`) :

```
http://127.0.0.1:8010/docs
```

Arrêter :

```bash
docker compose down          # garde les données
docker compose down -v       # supprime aussi le volume MySQL (repart de zéro)
```

## 2. CORS — connecter votre app frontend

Le backend autorise par défaut `http://localhost:3000` (Next.js) et `http://localhost:5173` (Vite). Si votre dev server tourne sur un autre port, ajoutez-le dans `.env` :

```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:4200
```

Puis redémarrez : `docker compose up -d --build`. Pas de wildcard `*` — seules les origines listées explicitement sont autorisées (choix de sécurité, voir `docs/SECURITY.md` à venir en Phase 9).

## 3. S'authentifier (espace admin)

Il n'y a pas encore de compte admin en base après un `alembic upgrade head` frais — seuls les rôles/permissions sont seedés, pas de compte utilisateur. Pour créer un premier compte `superadmin` en local :

```bash
docker compose exec app python3 -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models import AdminUser, Role
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        role = (await db.execute(select(Role).where(Role.name == 'superadmin'))).scalar_one()
        db.add(AdminUser(email='admin@synca.conf', password_hash=hash_password('ChangeMe123!'), role_id=role.id))
        await db.commit()
        print('Compte créé : admin@synca.conf / ChangeMe123!')

asyncio.run(main())
"
```

Puis :

```bash
curl -X POST http://127.0.0.1:8010/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@synca.conf","password":"ChangeMe123!"}'
```

Réponse :

```json
{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}
```

Utiliser `access_token` en header `Authorization: Bearer <token>` sur les routes protégées (ex. `PATCH /api/admin/roles/:id`). Expire après 15 min (`ACCESS_TOKEN_EXPIRE_MINUTES` dans `.env`) — pas encore d'endpoint `/refresh` (prévu avec le reste des routes admin, Phase 6).

⚠️ 5 échecs de connexion consécutifs verrouillent le compte 15 min (doublement à chaque échec suivant). Utile à savoir si vos tests E2E spamment le login avec un mauvais mot de passe.

## 4. Endpoints disponibles aujourd'hui (tous publics, sans auth)

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Ping |
| `GET` | `/api/days` | Jours de la conférence, triés par date |
| `GET` | `/api/sessions?day=&category=` | Programme, filtrable ; ne renvoie jamais une session non publique |
| `GET` | `/api/pass-types` | Types de billets actifs |
| `GET` | `/api/speakers?theme=&format=` | Speakers acceptés et publiés uniquement |
| `GET` | `/api/partners?level=` | Partenaires confirmés et publiés uniquement |
| `GET` | `/api/exhibitors` | Exposants confirmés et publiés uniquement |
| `GET` | `/api/faqs?category=` | FAQ, triée par `sort_order` |
| `GET` | `/api/campaign-windows` | Dates d'ouverture/fermeture de chaque étape (billetterie, call for speaker, etc.) — utile pour un compte à rebours frontend |

Les endpoints de liste (`sessions`, `speakers`, `partners`, `exhibitors`, `faqs`) acceptent `?limit=` (défaut 50, max 200) et `?offset=` (défaut 0).

Auth (protégés) :

| Méthode | Endpoint | Permission requise |
|---|---|---|
| `POST` | `/api/admin/login` | — |
| `PATCH` | `/api/admin/roles/:id` | `roles.manage` |

Le contrat exact (schémas de requête/réponse, codes d'erreur) est dans `/docs` (Swagger, générés depuis le code — toujours à jour).

## 5. Ce qui n'est pas encore disponible

- **Formulaires d'écriture** (`POST /api/register`, `/api/waitlist`, `/api/speakers/apply`, etc.) — Phase 4, en cours.
- **Paiement/billetterie** — Phase 5.
- **Backoffice complet** (gestion candidatures, dashboard, export CSV) — Phase 6.
- **Refresh token endpoint** — pas encore exposé, seul le login émet une paire access+refresh.
- **Upload de fichiers** (photo speaker, logo partenaire) — Phase 4.10.

Ne pas construire ces écrans côté frontend en pointant sur des routes qui n'existent pas encore — ils renverront `404`. Le suivi d'avancement précis est dans `ROADMAP.md` à la racine du repo (colonne Statut : ✅ = fait et testé, 🚧 = en cours, ⬜ = pas commencé).

## 6. Inspecter la base de données directement

```bash
docker compose exec db mysql -uroot -p"$MYSQL_ROOT_PASSWORD" syncaconf
```

(`MYSQL_ROOT_PASSWORD` est dans votre `.env`.) Utile pour vérifier ce qu'un formulaire a réellement écrit, ou insérer des données de test à la main pendant le dev frontend.

## 7. Retours attendus

Ce guide et l'API sont amenés à changer. Remontez en particulier :
- Un champ manquant ou mal typé dans une réponse (`GET /api/...`) par rapport à ce dont l'UI a besoin.
- Un filtre de liste manquant (ex. tri, recherche texte) qui bloquerait un écran.
- Un cas d'erreur mal géré (statut HTTP inattendu, message peu clair).
- Toute question sur le format d'un endpoint pas encore construit (Phase 4+) avant qu'on le fige côté backend — plus facile à changer maintenant qu'une fois consommé par l'UI.
