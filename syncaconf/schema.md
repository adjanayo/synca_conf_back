# SYNCA CONF 2027 — Schéma Backend

> Conférence tech panafricaine · 18–20 Août 2027 · Dakar, Sénégal

---

## 1. Schéma Base de Données (PostgreSQL)

```sql
-- ── JOURS DE LA CONFÉRENCE ──
CREATE TABLE days (
    id          SERIAL PRIMARY KEY,
    date        DATE NOT NULL UNIQUE,
    label       VARCHAR(50) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ── SESSIONS / PROGRAMME ──
CREATE TABLE sessions (
    id          SERIAL PRIMARY KEY,
    day_id      INT NOT NULL REFERENCES days(id),
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    category    VARCHAR(50) NOT NULL CHECK (category IN ('panel','workshop','competition','keynote','lightning_talk','fireside_chat','b2b','job_fair','networking','after_party')),
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    room        VARCHAR(100),
    speaker_id  INT,
    is_public   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ── TYPES DE PASS ──
CREATE TABLE pass_types (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(50) NOT NULL UNIQUE,
    price         INT NOT NULL,
    description   TEXT,
    inclusions    TEXT,
    max_days      INT DEFAULT 3,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT NOW()
);

-- ── UTILISATEURS / PARTICIPANTS ──
CREATE TABLE users (
    id                  SERIAL PRIMARY KEY,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    gender              VARCHAR(20) CHECK (gender IN ('Homme','Femme','Autre')),
    email               VARCHAR(255) NOT NULL UNIQUE,
    email_verified      BOOLEAN DEFAULT FALSE,
    phone_whatsapp      VARCHAR(20) NOT NULL,
    country             VARCHAR(100) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    sector              VARCHAR(50) CHECK (sector IN ('Dev','Data','Design','Cybersec','Product','IA','Autre')),
    experience_level    VARCHAR(30) CHECK (experience_level IN ('Débutant','Junior','Senior','Expert')),
    linkedin_url        VARCHAR(255),
    portfolio_url       VARCHAR(255),
    special_needs       TEXT,
    heard_from          VARCHAR(100),
    gdpr_consent        BOOLEAN NOT NULL DEFAULT FALSE,
    newsletter_consent  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- ── PROFILS UTILISATEUR (multi-choix) ──
CREATE TABLE user_profiles (
    id        SERIAL PRIMARY KEY,
    user_id   INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile   VARCHAR(30) NOT NULL CHECK (profile IN ('Étudiant','Professionnel','Entrepreneur','Recruteur','Autre')),
    UNIQUE(user_id, profile)
);

-- ── CODES PROMO ──
CREATE TABLE promo_codes (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(50) NOT NULL UNIQUE,
    discount_pct    INT NOT NULL CHECK (discount_pct BETWEEN 0 AND 100),
    discount_fixed  INT,
    usage_limit     INT DEFAULT NULL,
    usage_count     INT DEFAULT 0,
    valid_from      DATE,
    valid_until     DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ── PAIEMENTS ──
CREATE TABLE payments (
    id              SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id),
    pass_type_id    INT NOT NULL REFERENCES pass_types(id),
    promo_code_id   INT REFERENCES promo_codes(id),
    amount_original INT NOT NULL,
    amount_paid     INT NOT NULL,
    currency        VARCHAR(10) DEFAULT 'XOF',
    payment_method  VARCHAR(30) NOT NULL CHECK (payment_method IN ('stripe','wave','orange_money','mtn','bank_transfer')),
    transaction_ref VARCHAR(255) UNIQUE,
    status          VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','completed','failed','refunded')),
    paid_at         TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ── BILLETS ──
CREATE TABLE tickets (
    id             SERIAL PRIMARY KEY,
    user_id        INT NOT NULL REFERENCES users(id),
    payment_id     INT UNIQUE REFERENCES payments(id),
    pass_type_id   INT NOT NULL REFERENCES pass_types(id),
    ticket_number  VARCHAR(20) NOT NULL UNIQUE,
    qr_code_hash   VARCHAR(255) NOT NULL UNIQUE,
    pdf_url        VARCHAR(255),
    is_scanned     BOOLEAN DEFAULT FALSE,
    scanned_at     TIMESTAMP,
    created_at     TIMESTAMP DEFAULT NOW()
);

-- ── LISTE D'ATTENTE ──
CREATE TABLE waitlist (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255) NOT NULL UNIQUE,
    notified    BOOLEAN DEFAULT FALSE,
    registered  BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ── SPEAKERS ──
CREATE TABLE speakers (
    id                    SERIAL PRIMARY KEY,
    first_name            VARCHAR(100) NOT NULL,
    last_name             VARCHAR(100) NOT NULL,
    title_role            VARCHAR(200) NOT NULL,
    company               VARCHAR(200),
    country               VARCHAR(100) NOT NULL,
    email                 VARCHAR(255) NOT NULL,
    phone_whatsapp        VARCHAR(20) NOT NULL,
    linkedin_url          VARCHAR(255),
    website_url           VARCHAR(255),
    photo_url             VARCHAR(255),
    intervention_format   VARCHAR(50) NOT NULL CHECK (intervention_format IN ('Keynote','Panel','Workshop','Lightning Talk','Fireside Chat')),
    intervention_title    VARCHAR(100) NOT NULL,
    theme                 VARCHAR(50) NOT NULL CHECK (theme IN ('IA','EdTech','Entrepreneuriat','Carrières','Impact','Cybersec')),
    summary               TEXT NOT NULL,
    audience_level        VARCHAR(20) CHECK (audience_level IN ('Débutant','Intermédiaire','Avancé','Tous')),
    language              VARCHAR(30) CHECK (language IN ('Français','Anglais','Bilingue','Autre')),
    past_experience       TEXT,
    video_link            VARCHAR(255),
    availability          VARCHAR(30) CHECK (availability IN ('Oui confirmé','Sous réserve','Besoin aide déplacement')),
    departure_city        VARCHAR(100),
    needs_accommodation   BOOLEAN DEFAULT FALSE,
    motivation            TEXT NOT NULL,
    video_consent         VARCHAR(30) CHECK (video_consent IN ('Oui sans restriction','Oui avec validation','Non')),
    gdpr_consent          BOOLEAN NOT NULL DEFAULT FALSE,
    status                VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','accepted','rejected','confirmed')),
    is_public             BOOLEAN DEFAULT FALSE,
    created_at            TIMESTAMP DEFAULT NOW()
);

ALTER TABLE sessions ADD CONSTRAINT fk_speaker FOREIGN KEY (speaker_id) REFERENCES speakers(id);

-- ── AMBASSADEURS ──
CREATE TABLE ambassadors (
    id                    SERIAL PRIMARY KEY,
    first_name            VARCHAR(100) NOT NULL,
    last_name             VARCHAR(100) NOT NULL,
    age                   INT NOT NULL,
    country               VARCHAR(100) NOT NULL,
    city                  VARCHAR(100) NOT NULL,
    email                 VARCHAR(255) NOT NULL,
    phone_whatsapp        VARCHAR(20) NOT NULL,
    current_profile       VARCHAR(30) CHECK (current_profile IN ('Étudiant','Professionnel','Créateur de contenu','Entrepreneur')),
    institution_company   VARCHAR(200),
    linkedin_url          VARCHAR(255),
    social_handles        TEXT,
    followers_range       VARCHAR(20) CHECK (followers_range IN ('<500','500-2K','2K-10K','+10K')),
    motivation            TEXT NOT NULL,
    mobilization_plan     TEXT NOT NULL,
    estimated_reach       VARCHAR(20) CHECK (estimated_reach IN ('5–10','10–25','25–50','+50')),
    previous_synca        BOOLEAN DEFAULT FALSE,
    preferred_channels    TEXT NOT NULL,
    availability_pre      VARCHAR(20) CHECK (availability_pre IN ('Oui','Non','Partielle')),
    gdpr_consent          BOOLEAN NOT NULL DEFAULT FALSE,
    promo_code_id         INT REFERENCES promo_codes(id),
    status                VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','accepted','rejected')),
    created_at            TIMESTAMP DEFAULT NOW()
);

-- ── NIVEAUX DE PARTENARIAT ──
CREATE TABLE partner_levels (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    price       INT NOT NULL,
    benefits    TEXT,
    sort_order  INT DEFAULT 0,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ── PARTENAIRES ──
CREATE TABLE partners (
    id                  SERIAL PRIMARY KEY,
    organization_name   VARCHAR(200) NOT NULL,
    sector              VARCHAR(50) NOT NULL CHECK (sector IN ('Tech/ESN','Fintech','Télécoms','Banque','ONG','Université','Médias','Autre')),
    country             VARCHAR(100) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    website_url         VARCHAR(255),
    contact_name        VARCHAR(200) NOT NULL,
    contact_position    VARCHAR(200) NOT NULL,
    contact_email       VARCHAR(255) NOT NULL,
    contact_phone       VARCHAR(20) NOT NULL,
    level_id            INT NOT NULL REFERENCES partner_levels(id),
    has_budget          VARCHAR(30) CHECK (has_budget IN ('Oui — budget précis','Oui — à discuter','Non — exploration')),
    objectives          TEXT NOT NULL,
    previous_sponsor    BOOLEAN DEFAULT FALSE,
    message             TEXT,
    heard_from          VARCHAR(100),
    gdpr_consent        BOOLEAN NOT NULL DEFAULT FALSE,
    status              VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','contacted','negotiating','confirmed','rejected')),
    logo_url            VARCHAR(255),
    is_public           BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ── FAQ ──
CREATE TABLE faq_categories (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE faqs (
    id           SERIAL PRIMARY KEY,
    category_id  INT NOT NULL REFERENCES faq_categories(id),
    question     TEXT NOT NULL,
    answer       TEXT NOT NULL,
    sort_order   INT DEFAULT 0,
    created_at   TIMESTAMP DEFAULT NOW()
);

-- ── CONTACT ──
CREATE TABLE contact_messages (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    subject     VARCHAR(255),
    message     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ── EXPOSANTS ──
CREATE TABLE exhibitors (
    id                    SERIAL PRIMARY KEY,
    organization_name     VARCHAR(200) NOT NULL,
    sector                VARCHAR(100) NOT NULL,
    country               VARCHAR(100) NOT NULL,
    city                  VARCHAR(100) NOT NULL,
    website_url           VARCHAR(255),
    contact_name          VARCHAR(200) NOT NULL,
    contact_position      VARCHAR(200) NOT NULL,
    contact_email         VARCHAR(255) NOT NULL,
    contact_phone         VARCHAR(20) NOT NULL,
    stand_type            VARCHAR(20) NOT NULL CHECK (stand_type IN ('Standard','Premium','Mutualisé')),
    reps_count            INT NOT NULL CHECK (reps_count >= 1),
    linked_partner_level  VARCHAR(50),
    products_services     TEXT NOT NULL,
    equipment_needs       TEXT,
    side_activities       TEXT,
    visuals_url           VARCHAR(255),
    payment_method        VARCHAR(50) CHECK (payment_method IN ('Virement bancaire','Mobile Money','Chèque','À définir avec l''équipe Synca')),
    rules_accepted        BOOLEAN NOT NULL DEFAULT FALSE,
    gdpr_consent          BOOLEAN NOT NULL DEFAULT FALSE,
    status                VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','contacted','negotiating','confirmed','rejected')),
    is_public              BOOLEAN DEFAULT FALSE,
    created_at            TIMESTAMP DEFAULT NOW()
);

-- ── FENÊTRES DE CAMPAGNE (dates début/fin par étape de lancement) ──
CREATE TABLE campaign_windows (
    id          SERIAL PRIMARY KEY,
    key         VARCHAR(30) NOT NULL UNIQUE CHECK (key IN ('call_for_speaker','ticketing','call_for_partner','call_for_ambassador','call_for_exhibitor')),
    start_at    TIMESTAMP NOT NULL,
    end_at      TIMESTAMP NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    CHECK (end_at > start_at)
);

-- ── ADMIN ──
CREATE TABLE admin_users (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        VARCHAR(30) DEFAULT 'editor' CHECK (role IN ('superadmin','admin','editor','support')),
    last_login  TIMESTAMP,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- INDEX
CREATE INDEX idx_sessions_day ON sessions(day_id);
CREATE INDEX idx_sessions_category ON sessions(category);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_tickets_user ON tickets(user_id);
CREATE INDEX idx_tickets_number ON tickets(ticket_number);
CREATE INDEX idx_speakers_status ON speakers(status);
CREATE INDEX idx_ambassadors_status ON ambassadors(status);
CREATE INDEX idx_partners_status ON partners(status);
CREATE INDEX idx_partners_level ON partners(level_id);
CREATE INDEX idx_exhibitors_status ON exhibitors(status);
CREATE INDEX idx_campaign_windows_key ON campaign_windows(key);
```

---

## 2. Diagramme

```
days ──< sessions >── speakers

pass_types ──< payments ──< tickets
                │
promo_codes ────┘
                │
users ──────────┘
  │
  └──< user_profiles

partner_levels ──< partners

faq_categories ──< faqs

waitlist | ambassadors | contact_messages | admin_users | exhibitors

campaign_windows (indépendante — une ligne par étape : call_for_speaker,
                   ticketing, call_for_partner, call_for_ambassador,
                   call_for_exhibitor)
```

---

## 3. Tous les formulaires (côté backend)

### A. Formulaire Inscription Participant
**Endpoint:** `POST /api/register`
**Table:** `users` + `user_profiles`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `first_name` | string(100) | — | ✓ |
| `last_name` | string(100) | — | ✓ |
| `gender` | enum | `Homme` / `Femme` / `Autre` | ✓ |
| `email` | email | unique, format email | ✓ |
| `phone_whatsapp` | string(20) | format international | ✓ |
| `country` | string(100) | — | ✓ |
| `city` | string(100) | — | ✓ |
| `profiles` | array[enum] | min 1, valeurs : `Étudiant`, `Professionnel`, `Entrepreneur`, `Recruteur`, `Autre` | ✓ |
| `sector` | enum | `Dev`, `Data`, `Design`, `Cybersec`, `Product`, `IA`, `Autre` | ✓ |
| `experience_level` | enum | `Débutant`, `Junior`, `Senior`, `Expert` | ✓ |
| `pass_type_id` | int | FK vers `pass_types` | ✓ |
| `promo_code` | string(50) | optionnel, validé si fourni | ✗ |
| `linkedin_url` | url | format URL | ✗ |
| `portfolio_url` | url | format URL | ✗ |
| `special_needs` | text | — | ✗ |
| `heard_from` | string(100) | — | ✗ |
| `gdpr_consent` | boolean | doit être `true` | ✓ |
| `newsletter_consent` | boolean | — | ✓ |

**Logique métier :**
- Ouvert uniquement pendant la fenêtre `campaign_windows.key = 'ticketing'` (voir §5bis) — avant/après → `403`, formulaire caché côté frontend, page waitlist affichée
- Vérifier si `pass_type_id` est valide et actif
- Si `promo_code` fourni → valider (existe, actif, non épuisé, dans dates valides) → calculer réduction
- Après validation → rediriger vers paiement
- Envoi email de confirmation avec lien de vérification

---

### B. Formulaire Paiement
**Endpoint:** `POST /api/payments`
**Tables:** `payments` → `tickets`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `user_id` | int | FK `users`, doit avoir un `pass_type_id` non payé | ✓ |
| `payment_method` | enum | `stripe`, `wave`, `orange_money`, `mtn`, `bank_transfer` | ✓ |
| `promo_code_id` | int | FK `promo_codes` (repris de l'inscription) | ✗ |

**Logique métier :**
- Créer une entrée `payments` avec `status = pending`
- Rediriger vers la passerelle de paiement correspondante
- Webhook callback → `status = completed` → générer `ticket`
- Génération PDF billet avec QR code → upload → `pdf_url`
- Envoi email billet au participant

---

### C. Formulaire Candidature Speaker
**Endpoint:** `POST /api/speakers/apply`
**Table:** `speakers`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `first_name` | string(100) | — | ✓ |
| `last_name` | string(100) | — | ✓ |
| `title_role` | string(200) | — | ✓ |
| `company` | string(200) | — | ✗ |
| `country` | string(100) | — | ✓ |
| `email` | email | format email | ✓ |
| `phone_whatsapp` | string(20) | — | ✓ |
| `linkedin_url` | url | — | ✗ |
| `website_url` | url | — | ✗ |
| `photo` | file | JPG/PNG, min 1MB, fond neutre | ✓ |
| `intervention_format` | enum | `Keynote`, `Panel`, `Workshop`, `Lightning Talk`, `Fireside Chat` | ✓ |
| `intervention_title` | string(100) | max 100 caractères | ✓ |
| `theme` | enum | `IA`, `EdTech`, `Entrepreneuriat`, `Carrières`, `Impact`, `Cybersec` | ✓ |
| `summary` | text | max 200 mots | ✓ |
| `audience_level` | enum | `Débutant`, `Intermédiaire`, `Avancé`, `Tous` | ✓ |
| `language` | enum | `Français`, `Anglais`, `Bilingue`, `Autre` | ✓ |
| `past_experience` | text | — | ✗ |
| `video_link` | url | YouTube, Vimeo, Drive | ✗ |
| `availability` | enum | `Oui confirmé`, `Sous réserve`, `Besoin aide déplacement` | ✓ |
| `departure_city` | string(100) | — | ✗ |
| `needs_accommodation` | boolean | — | ✗ |
| `motivation` | text | max 150 mots | ✓ |
| `video_consent` | enum | `Oui sans restriction`, `Oui avec validation`, `Non` | ✓ |
| `gdpr_consent` | boolean | doit être `true` | ✓ |

**Logique métier :**
- Ouvert uniquement pendant la fenêtre `campaign_windows.key = 'call_for_speaker'` (voir §5bis) — sinon `403`
- Upload photo vers Cloudinary/S3 → `photo_url`
- `status = pending` par défaut
- Envoi accusé de réception automatique par email
- Back-office : admin peut accepter/rejeter → `status = accepted|rejected`
- Si accepté → `is_public = true` (apparaît sur la page /speakers) — indépendant de la fenêtre de campagne : l'annonce publique peut se faire à tout moment (cf. `Infos.md`)

---

### D. Formulaire Candidature Ambassadeur
**Endpoint:** `POST /api/ambassadors/apply`
**Table:** `ambassadors`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `first_name` | string(100) | — | ✓ |
| `last_name` | string(100) | — | ✓ |
| `age` | int | ≥ 16 | ✓ |
| `country` | string(100) | — | ✓ |
| `city` | string(100) | — | ✓ |
| `email` | email | format email | ✓ |
| `phone_whatsapp` | string(20) | — | ✓ |
| `current_profile` | enum | `Étudiant`, `Professionnel`, `Créateur de contenu`, `Entrepreneur` | ✓ |
| `institution_company` | string(200) | — | ✗ |
| `linkedin_url` | url | — | ✗ |
| `social_handles` | object | `{ instagram?, x?, tiktok? }` | ✗ |
| `followers_range` | enum | `<500`, `500-2K`, `2K-10K`, `+10K` | ✓ |
| `motivation` | text | max 150 mots | ✓ |
| `mobilization_plan` | text | max 100 mots | ✓ |
| `estimated_reach` | enum | `5–10`, `10–25`, `25–50`, `+50` | ✗ |
| `previous_synca` | boolean | — | ✓ |
| `preferred_channels` | array[enum] | min 1 : `WhatsApp`, `Instagram`, `LinkedIn`, `TikTok`, `Email`, `Campus` | ✓ |
| `availability_pre` | enum | `Oui`, `Non`, `Partielle` | ✓ |
| `gdpr_consent` | boolean | doit être `true` | ✓ |

**Logique métier :**
- Ouvert uniquement pendant la fenêtre `campaign_windows.key = 'call_for_ambassador'` (voir §5bis) — sinon `403`
- `status = pending` par défaut
- Si accepté → générer `promo_code` unique → lier `promo_code_id`
- Envoi kit digital (visuels, textes, code promo)
- L'ambassadeur partage son code → les inscriptions avec son code sont traçables

---

### E. Formulaire Partenaire / Sponsor
**Endpoint:** `POST /api/partners/apply`
**Table:** `partners`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `organization_name` | string(200) | — | ✓ |
| `sector` | enum | `Tech/ESN`, `Fintech`, `Télécoms`, `Banque`, `ONG`, `Université`, `Médias`, `Autre` | ✓ |
| `country` | string(100) | — | ✓ |
| `city` | string(100) | — | ✓ |
| `website_url` | url | — | ✗ |
| `contact_name` | string(200) | — | ✓ |
| `contact_position` | string(200) | — | ✓ |
| `contact_email` | email | format email | ✓ |
| `contact_phone` | string(20) | — | ✓ |
| `level_id` | int | FK `partner_levels` | ✓ |
| `has_budget` | enum | `Oui — budget précis`, `Oui — à discuter`, `Non — exploration` | ✓ |
| `objectives` | array[enum] | min 1 : `Recrutement`, `Visibilité`, `B2B`, `Lancement produit`, `Impact social`, `Autre` | ✓ |
| `previous_sponsor` | boolean | — | ✓ |
| `message` | text | — | ✗ |
| `heard_from` | string(100) | — | ✗ |
| `gdpr_consent` | boolean | doit être `true` | ✓ |

**Logique métier :**
- Ouvert uniquement pendant la fenêtre `campaign_windows.key = 'call_for_partner'` (voir §5bis) — sinon `403`
- `status = pending` par défaut
- Envoi automatique email confirmation + dossier sponsoring PDF + lien calendly
- Back-office : workflow `pending` → `contacted` → `negotiating` → `confirmed|rejected`
- Si `confirmed` + logo uploadé → `is_public = true`

---

### F. Formulaire Exposant (Espace Exposition)
**Endpoint:** `POST /api/exhibitors/apply`
**Table:** `exhibitors`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `organization_name` | string(200) | — | ✓ |
| `sector` | string(100) | — | ✓ |
| `country` | string(100) | — | ✓ |
| `city` | string(100) | — | ✓ |
| `website_url` | url | — | ✗ |
| `contact_name` | string(200) | — | ✓ |
| `contact_position` | string(200) | — | ✓ |
| `contact_email` | email | format email | ✓ |
| `contact_phone` | string(20) | — | ✓ |
| `stand_type` | enum | `Standard`, `Premium`, `Mutualisé` | ✓ |
| `reps_count` | int | ≥ 1 | ✓ |
| `linked_partner_level` | string(50) | palier de sponsoring associé, le cas échéant | ✗ |
| `products_services` | text | produits/services à présenter | ✓ |
| `equipment_needs` | array[enum] | `Électricité`, `Mobilier`, `Écran/TV`, `Wifi`, `Signalétique dédiée` | ✗ |
| `side_activities` | array[enum] | `Masterclass`, `Panel/table ronde`, `Side event`, `Présentation de solution` | ✗ |
| `visuals_url` | url | lien logo/visuels (Drive, WeTransfer…) | ✗ |
| `payment_method` | enum | `Virement bancaire`, `Mobile Money`, `Chèque`, `À définir avec l'équipe Synca` | ✗ |
| `rules_accepted` | boolean | doit être `true` (règlement espace exposition) | ✓ |
| `gdpr_consent` | boolean | doit être `true` | ✓ |

**Logique métier :**
- Ouvert uniquement pendant la fenêtre `campaign_windows.key = 'call_for_exhibitor'` (voir §5bis) — sinon `403`
- `status = pending` par défaut
- Envoi automatique email confirmation
- Back-office : workflow `pending` → `contacted` → `negotiating` → `confirmed|rejected`
- Si `confirmed` + visuels fournis → `is_public = true`

---

### G. Formulaire Liste d'Attente
**Endpoint:** `POST /api/waitlist`
**Table:** `waitlist`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `email` | email | unique, format email | ✓ |

**Logique métier :**
- Toujours ouvert (pas de fenêtre de campagne — c'est justement le mécanisme utilisé avant l'ouverture de `ticketing`)
- Ajouter à la waitlist
- Quand `campaign_windows.key = 'ticketing'` démarre → envoi email à tous les `notified = false` → passer `notified = true`
- Si l'utilisateur s'inscrit → `registered = true`

---

### H. Formulaire Contact
**Endpoint:** `POST /api/contact`
**Table:** `contact_messages`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `name` | string(200) | — | ✓ |
| `email` | email | format email | ✓ |
| `subject` | string(255) | — | ✗ |
| `message` | text | — | ✓ |
| `captcha` | string | reCAPTCHA token | ✓ |

---

### I. Formulaire Newsletter (page d'accueil)
**Endpoint:** `POST /api/newsletter`
**Table:** `users.newsletter_consent` ou table dédiée

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `email` | email | format email | ✓ |

---

### J. Formulaire Connexion Admin (Back-office)
**Endpoint:** `POST /api/admin/login`
**Table:** `admin_users`

| Champ | Type | Validation | Obligatoire |
|-------|------|-----------|:----------:|
| `email` | email | doit exister dans `admin_users` | ✓ |
| `password` | string | vérifié avec bcrypt/argon2 | ✓ |

---

## 4. Récapitulatif Endpoints API

| Méthode | Endpoint | Fonction |
|---------|----------|----------|
| `GET` | `/api/days` | Jours de la conférence |
| `GET` | `/api/sessions?day=&category=` | Programme filtrable |
| `GET` | `/api/pass-types` | Liste des pass disponibles |
| `GET` | `/api/speakers?theme=&format=` | Speakers publics (filtrés) |
| `GET` | `/api/partners?level=` | Partenaires publics |
| `GET` | `/api/exhibitors?public=true` | Exposants publics |
| `GET` | `/api/faqs?category=` | FAQ |
| `GET` | `/api/campaign-windows` | Fenêtres de campagne actives/à venir (pour affichage frontend) |
| `POST` | `/api/waitlist` | Inscription liste d'attente |
| `POST` | `/api/register` | Inscription participant (ouvert seulement si fenêtre `ticketing` active) |
| `POST` | `/api/payments` | Initier paiement |
| `POST` | `/api/payments/webhook` | Callback paiement |
| `POST` | `/api/promo/validate` | Valider un code promo |
| `POST` | `/api/speakers/apply` | Candidature speaker (ouvert seulement si fenêtre `call_for_speaker` active) |
| `POST` | `/api/ambassadors/apply` | Candidature ambassadeur (ouvert seulement si fenêtre `call_for_ambassador` active) |
| `POST` | `/api/partners/apply` | Candidature partenaire (ouvert seulement si fenêtre `call_for_partner` active) |
| `POST` | `/api/exhibitors/apply` | Candidature exposant (ouvert seulement si fenêtre `call_for_exhibitor` active) |
| `POST` | `/api/contact` | Formulaire contact |
| `POST` | `/api/newsletter` | Inscription newsletter |
| `POST` | `/api/admin/login` | Connexion admin |
| `GET` | `/api/admin/registrations` | Liste inscriptions (admin) |
| `GET` | `/api/admin/speakers` | Liste candidatures speakers |
| `PATCH` | `/api/admin/speakers/:id` | Accepter/rejeter speaker |
| `GET` | `/api/admin/ambassadors` | Liste ambassadeurs |
| `PATCH` | `/api/admin/ambassadors/:id` | Accepter/rejeter ambassadeur |
| `GET` | `/api/admin/partners` | Liste partenaires |
| `PATCH` | `/api/admin/partners/:id` | Mettre à jour statut partenaire |
| `GET` | `/api/admin/exhibitors` | Liste exposants |
| `PATCH` | `/api/admin/exhibitors/:id` | Mettre à jour statut exposant |
| `GET` | `/api/admin/contacts` | Messages contact |
| `GET` | `/api/admin/stats` | Dashboard stats |
| `GET` | `/api/admin/campaign-windows` | Liste des fenêtres de campagne |
| `PATCH` | `/api/admin/campaign-windows/:key` | Modifier `start_at`/`end_at`/`is_active` d'une fenêtre |

---

## 5. Règles métier globales

1. **Ouverture billetterie :** Le formulaire d'inscription est caché avant une date configurable. Une page d'attente avec compteur + waitlist est affichée.
2. **Code promo :** Un code promo peut être créé par un admin ou généré automatiquement pour un ambassadeur accepté. Réduction en % ou montant fixe.
3. **Génération billet :** Déclenchée automatiquement après `payment.status = completed`. PDF avec QR code unique + envoi email.
4. **Workflow validation :** Speakers, ambassadeurs, partenaires, exposants suivent un pipeline `pending → accepted/rejected` (ou `pending → contacted → negotiating → confirmed/rejected` pour partenaires/exposants) via le back-office admin.
5. **Protection formulaires :** reCAPTCHA sur tous les formulaires publics. RGPD obligatoire.
6. **Emails transactionnels :**
   - Inscription : confirmation + vérification email
   - Speaker/Ambassadeur/Partenaire/Exposant : accusé de réception
   - Paiement : confirmation + billet PDF
   - Waitlist : notification ouverture
7. **Upload fichiers :** Photos speakers → Backblaze B2. Logos partenaires/visuels exposants → Backblaze B2. Billets PDF → stockage sécurisé.

---

## 5bis. Fenêtres de campagne (dates début/fin)

D'après `Infos.md`, le lancement du projet suit des étapes successives, dont cinq ont une fenêtre temporelle propre (début **et** fin) qui contrôle l'ouverture du formulaire public correspondant :

| `campaign_windows.key` | Formulaire gardé | Étape (`Infos.md`) |
|---|---|---|
| `call_for_speaker` | `POST /api/speakers/apply` | Call for speaker |
| `ticketing` | `POST /api/register` | Lancement de la billetterie |
| `call_for_partner` | `POST /api/partners/apply` | Call for partner |
| `call_for_ambassador` | `POST /api/ambassadors/apply` | Call for ambassador |
| `call_for_exhibitor` | `POST /api/exhibitors/apply` | Call for exhibitor |

**Règles :**
- Chaque endpoint concerné vérifie `NOW() BETWEEN start_at AND end_at AND is_active = true` avant d'accepter la soumission ; hors fenêtre → `403` avec message explicite (`"Cette candidature n'est pas encore ouverte"` / `"Cette candidature est clôturée"`).
- `is_active` est un coupe-circuit manuel indépendant des dates (permet de fermer une campagne en urgence sans changer `end_at`).
- `GET /api/campaign-windows` expose les fenêtres (dates + statut) publiquement pour que le frontend affiche compte à rebours / état "à venir" / "fermé" — sans exposer de données sensibles.
- L'étape « Lancement du site » (première étape de `Infos.md`) n'a pas de fenêtre dédiée : c'est la mise en ligne elle-même, pas un formulaire.
- **L'annonce publique** (`is_public = true` sur `speakers`/`partners`/`exhibitors`) est **indépendante** de la fenêtre de campagne : un admin peut rendre un speaker/partenaire public à tout moment après acceptation, même après la fermeture de l'appel à candidatures (cf. `Infos.md` : "l'annonce des speakers et partenaires a tout moment").
- Les fenêtres sont gérées par le back-office (`PATCH /api/admin/campaign-windows/:key`), réservé aux rôles `superadmin`/`admin`.
