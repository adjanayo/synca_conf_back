Voici un README professionnel et prêt à l’emploi pour ton projet 

# Guide d'installation du projet

Ce document explique les étapes nécessaires pour installer et exécuter le projet après clonage du dépôt.

## Prérequis

Assurez-vous d’avoir installé les outils suivants sur votre machine :

* PHP ≥ 8.5 (ou version requise par le projet)
* Composer
* PostgreSQL (pgsql)
* Node.js & npm
* Serveur web (Apache ou Nginx)
* Extensions PHP requises :

  * xml
  * dom
  * pdo
  * pgsql
  * mbstring
  * curl

---

## 1. Cloner le projet

```bash
git clone <url-du-repo>
cd <nom-du-projet>
```

---

## 2. Installer les dépendances

### Backend (Laravel)

```bash
composer install
```

### Frontend (si Angular / JS)

```bash
npm install
```

---

## ⚙️ 3. Configuration de l’environnement

Copier le fichier `.env` :

```bash
cp .env.example .env
```

Configurer les variables dans `.env` :

```env
APP_NAME=synca_conf
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://localhost

DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=synca_db
DB_USERNAME=synca
DB_PASSWORD=synca
```

---

## 4. Générer la clé de l’application

```bash
php artisan key:generate
```

---

## 5. Mise en place de la base de données PostgreSQL

### Créer la base et l’utilisateur

Se connecter à PostgreSQL :

```bash
sudo -i -u postgres
psql
```

Puis exécuter :

```sql
CREATE DATABASE synca_db;
CREATE USER synca WITH PASSWORD 'synca';
GRANT ALL PRIVILEGES ON DATABASE synca_db TO synca;
```

---

## 6. Migration de la base de données

```bash
php artisan migrate
```

Optionnel (si seeders) :

```bash
php artisan db:seed
```

---

## 7. Lancer le projet

```bash
php artisan serve
```

Accéder à l’application :
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 8. Lancer le frontend (si applicable)

```bash
npm run dev
```

ou

```bash
npm run build
```

---

## Problèmes fréquents

### Extensions PHP manquantes

Installer :

```bash
sudo apt install php-xml php-pgsql
```

---

### Erreur "could not find driver"

👉 Installer PostgreSQL pour PHP :

```bash
sudo apt install php-pgsql
```

---

### Problème de permission

```bash
sudo chmod -R 775 storage bootstrap/cache
```
