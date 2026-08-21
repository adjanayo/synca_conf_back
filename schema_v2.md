# SYNCA CONF 2027 — Schéma Backend v2

## Flux d'inscription

1. Formulaire rempli → ligne créée dans `pending_registrations` (statut `en_attente_paiement`) + `resume_token` généré → lien de reprise envoyé par email.
2. Paiement lancé → `payments` est lié à `pending_registrations` (le participant n'existe pas encore).
3. Paiement confirmé (webhook) → une ligne est créée dans `participants`, `pending_registrations.status` passe à `converti`, le `ticket` est généré.
4. Si la personne ne paie pas → elle revient via son token, on retrouve `pending_registrations`. Passé `token_expires_at`, le statut passe à `expire`.

---

## Admin (seul type de compte avec authentification)

```sql
CREATE TABLE admin_users (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        VARCHAR(30) DEFAULT 'editor' CHECK (role IN ('superadmin','admin','editor','support')),
    last_login  TIMESTAMP,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

## Jours de la conférence

```sql
CREATE TABLE days (
    id          SERIAL PRIMARY KEY,
    date        DATE NOT NULL UNIQUE,
    label       VARCHAR(50) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    updated_by  INT REFERENCES admin_users(id) --on peut l'enlever
);
```

## Types de pass

```sql
CREATE TABLE pass_types (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(50) NOT NULL UNIQUE,
    price        INT NOT NULL,
    description  TEXT,
    inclusions   TEXT,
    max_days     INT DEFAULT 3,
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW(),
    updated_by   INT REFERENCES admin_users(id)
);
```

## Niveaux de partenariat (type de partenariat : gold, bronze...)

```sql
CREATE TABLE partner_levels (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    price       INT NOT NULL,
    benefits    TEXT,
    sort_order  INT DEFAULT 0,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    updated_by  INT REFERENCES admin_users(id)
);
```

## Catégories FAQ

```sql
CREATE TABLE faq_categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    updated_by  INT REFERENCES admin_users(id)
);
```

## Codes promo

```sql
CREATE TABLE promo_codes (
    id            SERIAL PRIMARY KEY,
    code          VARCHAR(50) NOT NULL UNIQUE,
    discount_pct  INT NOT NULL CHECK (discount_pct BETWEEN 0 AND 100),
    usage_limit   INT DEFAULT NULL,
    usage_count   INT DEFAULT 0,
    valid_from    DATE,
    valid_until   DATE,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW(),
    updated_by    INT REFERENCES admin_users(id)
);
```

## Pré-inscriptions (avant paiement — pas encore un participant)

Une ligne ici représente un formulaire rempli mais pas encore payé. Le `resume_token` permet à la personne de revenir compléter son paiement plus tard, sans compte ni mot de passe (lien envoyé par email).

```sql
CREATE TABLE pending_registrations (
    id                  SERIAL PRIMARY KEY,
    resume_token        VARCHAR(64) NOT NULL UNIQUE,
    token_expires_at    TIMESTAMP NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    gender              VARCHAR(20) CHECK (gender IN ('Homme','Femme','Autre')),
    email               VARCHAR(255) NOT NULL UNIQUE,
    phone_whatsapp      VARCHAR(20) NOT NULL,
    country             VARCHAR(100) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    sector              VARCHAR(50) CHECK (sector IN ('Dev','Data','Design','Cybersec','Product','IA','Autre')),
    profile             VARCHAR(30) NOT NULL CHECK (profile IN ('Étudiant','Professionnel','Entrepreneur','Recruteur','Autre')) UNIQUE,
    profile_other       VARCHAR(100),

    experience_level    VARCHAR(30) CHECK (experience_level IN ('Débutant','Junior','Senior','Expert')),
    linkedin_url        VARCHAR(255),
    portfolio_url       VARCHAR(255),
    heard_from          VARCHAR(100) CHECK (heard_from IN ('Amis','WhatsApp','Autre')),
    special_needs       TEXT,
    gdpr_consent        BOOLEAN NOT NULL DEFAULT FALSE,
    newsletter_consent  BOOLEAN NOT NULL DEFAULT FALSE,
    pass_type_id        INT NOT NULL REFERENCES pass_types(id),
    promo_code_id       INT REFERENCES promo_codes(id),
    status              VARCHAR(20) NOT NULL DEFAULT 'en_attente_paiement'
                        CHECK (status IN ('en_attente_paiement','converti','expire')),
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);


```

## Participants (créé uniquement après paiement confirmé)

```sql
CREATE TABLE participants (
    id                       SERIAL PRIMARY KEY,
    pending_registration_id  INT UNIQUE REFERENCES pending_registrations(id) ON DELETE SET NULL,
    first_name               VARCHAR(100) NOT NULL,
    last_name                VARCHAR(100) NOT NULL,
    gender                   VARCHAR(20) CHECK (gender IN ('Homme','Femme','Autre')),
    email                    VARCHAR(255) NOT NULL UNIQUE,
    email_verified           BOOLEAN DEFAULT FALSE,
    phone_whatsapp           VARCHAR(20) NOT NULL,
    country                  VARCHAR(100) NOT NULL,
    city                     VARCHAR(100) NOT NULL,
    sector                   VARCHAR(50) CHECK (sector IN ('Dev','Data','Design','Cybersec','Product','IA','Autre')),
    experience_level         VARCHAR(30) CHECK (experience_level IN ('Débutant','Junior','Senior','Expert')),
    linkedin_url             VARCHAR(255),
    portfolio_url            VARCHAR(255),
    heard_from                VARCHAR(100) CHECK (heard_from IN ('Amis','WhatsApp','Autre')),
    gdpr_consent              BOOLEAN NOT NULL DEFAULT FALSE,
    newsletter_consent        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at                TIMESTAMP DEFAULT NOW()
    -- Pas de mot de passe : aucun compte / connexion pour les participants.
);

CREATE TABLE participant_profiles (
    id              SERIAL PRIMARY KEY,
    participant_id  INT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    profile         VARCHAR(30) NOT NULL CHECK (profile IN ('Étudiant','Professionnel','Entrepreneur','Recruteur','Autre')),
    UNIQUE(participant_id, profile)
);
```

## Paiements (liés à la pré-inscription, pas encore au participant)

```sql
CREATE TABLE payments (
    id                       SERIAL PRIMARY KEY,
    pending_registration_id  INT NOT NULL REFERENCES pending_registrations(id),
    pass_type_id             INT NOT NULL REFERENCES pass_types(id),
    promo_code_id            INT REFERENCES promo_codes(id),
    amount_original          INT NOT NULL,
    amount_paid              INT NOT NULL,
    currency                 VARCHAR(10) DEFAULT 'XOF',
    payment_method           VARCHAR(30) NOT NULL CHECK (payment_method IN ('stripe','wave','orange_money','mtn','bank_transfer')),
    transaction_ref           VARCHAR(255) UNIQUE,
    status                    VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','completed','failed','refunded')),
    paid_at                   TIMESTAMP,
    created_at                TIMESTAMP DEFAULT NOW()
);
```

## Billets (générés uniquement une fois le participant créé)

```sql
CREATE TABLE tickets (
    id             SERIAL PRIMARY KEY,
    participant_id INT NOT NULL REFERENCES participants(id),
    payment_id     INT NOT NULL UNIQUE REFERENCES payments(id),
    pass_type_id   INT NOT NULL REFERENCES pass_types(id),
    ticket_number  VARCHAR(20) NOT NULL UNIQUE,
    qr_code_hash   VARCHAR(255) NOT NULL UNIQUE,
    pdf_url        VARCHAR(255),
    is_scanned     BOOLEAN DEFAULT FALSE,
    scanned_at     TIMESTAMP,
    created_at     TIMESTAMP DEFAULT NOW()
);
```

## Liste d'attente

```sql
CREATE TABLE waitlist (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255) NOT NULL UNIQUE,
    notified    BOOLEAN DEFAULT FALSE,
    registered  BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

## Sessions / programme

```sql
CREATE TABLE sessions_conf
 (
    id          SERIAL PRIMARY KEY,
    day_id      INT NOT NULL REFERENCES days(id),
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    category    VARCHAR(50) NOT NULL CHECK (category IN ('panel','workshop','competition','keynote','lightning_talk','fireside_chat','b2b','job_fair','networking','after_party')),
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    room        VARCHAR(100),
    speaker_id  INT,                                 -- FK ajoutée après création de speakers
    is_public   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    updated_by  INT REFERENCES admin_users(id),
    CHECK (end_time > start_time)
);
```

## Speakers

```sql
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
    created_at            TIMESTAMP DEFAULT NOW(),
    updated_at            TIMESTAMP DEFAULT NOW(),
    updated_by            INT REFERENCES admin_users(id)
);

ALTER TABLE sessions_conf ADD CONSTRAINT fk_speaker FOREIGN KEY (speaker_id) REFERENCES speakers(id);
```

## Ambassadeurs

```sql
CREATE TABLE ambassadors (
    id                    SERIAL PRIMARY KEY,
    first_name            VARCHAR(100) NOT NULL,
    last_name             VARCHAR(100) NOT NULL,
    age                   INT NOT NULL CHECK (age >= 16),
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
    created_at            TIMESTAMP DEFAULT NOW(),
    updated_at            TIMESTAMP DEFAULT NOW(),
    updated_by            INT REFERENCES admin_users(id)
);
```

## Partenaires / sponsors

Le type de partenariat (Gold, Silver, Bronze...) est choisi via `level_id`, qui référence `partner_levels`. C'est ce champ qui alimente le menu déroulant "type de partenariat" dans le formulaire.

```sql
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
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    updated_by          INT REFERENCES admin_users(id)
);
```

## FAQ

```sql
CREATE TABLE faqs (
    id           SERIAL PRIMARY KEY,
    category_id  INT NOT NULL REFERENCES faq_categories(id),
    question     TEXT NOT NULL,
    answer       TEXT NOT NULL,
    sort_order   INT DEFAULT 0,
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW(),
    updated_by   INT REFERENCES admin_users(id)
);
```

## Contact

```sql
CREATE TABLE contact_messages (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    subject     VARCHAR(255),
    message     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    updated_by  INT REFERENCES admin_users(id)
);
```

## Statistiques / métriques (saisie manuelle par l'admin)

Pas de tracking automatique de clics dans ce schéma : l'admin saisit les chiffres (via Google Analytics, Plausible, etc.) une fois par jour ou par période, pour affichage dans le dashboard.

```sql
CREATE TABLE site_metrics (
    id          SERIAL PRIMARY KEY,
    metric_key  VARCHAR(100) NOT NULL,   -- ex: 'clics_billetterie', 'vues_programme', 'visiteurs_uniques'
    metric_date DATE NOT NULL,
    value       INT NOT NULL DEFAULT 0,
    note        TEXT,
    updated_at  TIMESTAMP DEFAULT NOW(),
    updated_by  INT REFERENCES admin_users(id),
    UNIQUE(metric_key, metric_date)
);
```

## Index

```sql
CREATE INDEX idx_sessions_conf_day ON sessions_conf(day_id);
CREATE INDEX idx_sessions_conf_category ON sessions_conf(category);

CREATE INDEX idx_pending_reg_email ON pending_registrations(email);
CREATE INDEX idx_pending_reg_token ON pending_registrations(resume_token);
CREATE INDEX idx_pending_reg_status ON pending_registrations(status);

CREATE INDEX idx_participants_email ON participants(email);

CREATE INDEX idx_payments_pending_reg ON payments(pending_registration_id);
CREATE INDEX idx_payments_status ON payments(status);

CREATE INDEX idx_tickets_participant ON tickets(participant_id);
CREATE INDEX idx_tickets_number ON tickets(ticket_number);

CREATE INDEX idx_speakers_status ON speakers(status);
CREATE INDEX idx_ambassadors_status ON ambassadors(status);
CREATE INDEX idx_partners_status ON partners(status);
CREATE INDEX idx_partners_level ON partners(level_id);

CREATE INDEX idx_site_metrics_key_date ON site_metrics(metric_key, metric_date);

```


## 1. Formulaires publics (aucune authentification)

### 1.1 Pré-inscription billetterie
Alimente `pending_registrations` + `pending_registration_profiles`.

| Champ formulaire | Colonne | Contrainte |
|---|---|---|
| Prénom | `first_name` | requis |
| Nom | `last_name` | requis |
| Genre | `gender` | select : Homme / Femme / Autre |
| Email | `email` | requis, unique tant que le statut est `en_attente_paiement` |
| WhatsApp | `phone_whatsapp` | requis |
| Pays | `country` | requis |
| Ville | `city` | requis |
| Secteur | `sector` | select |
| Niveau d'expérience | `experience_level` | select |
| Profil(s) | table liée `pending_registration_profiles` | checkboxes, multi-choix |
| LinkedIn | `linkedin_url` | optionnel |
| Portfolio | `portfolio_url` | optionnel |
| Comment tu nous as connus | `heard_from` | select |
| Besoins spécifiques | `special_needs` | texte libre, optionnel |
| Type de pass | `pass_type_id` | select, requis (rempli depuis `pass_types` actifs) |
| Code promo | `promo_code_id` | champ texte → résolu en id côté backend |
| Consentement RGPD | `gdpr_consent` | checkbox, requis (bloque la soumission si non coché) |
| Newsletter | `newsletter_consent` | checkbox, optionnel |

**Logique backend :**
- Si un `pending_registrations` actif (`en_attente_paiement`) existe déjà pour cet email → mise à jour de la ligne existante (upsert), on renvoie le même `resume_token`, pas de doublon.
- Sinon → création, génération d'un `resume_token` aléatoire (ex. `crypto.randomBytes(32).toString('hex')`), `token_expires_at = now + 7 jours`, email envoyé avec le lien `/reprendre-inscription?token=...`.

### 1.2 Reprise d'inscription
Aucun champ à saisir : la page envoie le token et reçoit les données déjà remplies pour pré-remplir le formulaire et relancer le paiement.

### 1.3 Paiement
- Formulaire minimal (choix du moyen de paiement) → crée une ligne `payments` liée à `pending_registration_id`.
- Redirection vers le prestataire (Stripe / Wave / Orange Money / MTN / virement).
- **Webhook** du prestataire → met à jour `payments.status`, et si `completed` :
  1. copie les données de `pending_registrations` vers une nouvelle ligne `participants` (+ `participant_profiles`) ;
  2. passe `pending_registrations.status` à `converti` ;
  3. crée le `ticket` (numéro + QR code) et déclenche l'email de confirmation.

### 1.4 Candidature Speaker
Alimente `speakers` (statut `pending` à la création).

Champs : identité, entreprise, pays, contacts, `intervention_format`, `intervention_title`, `theme`, `summary`, `audience_level`, `language`, expérience passée, lien vidéo, disponibilité, ville de départ, besoin d'hébergement, motivation, consentement vidéo, RGPD.

### 1.5 Candidature Ambassadeur
Alimente `ambassadors` (statut `pending`).

Champs : identité, âge (≥16), pays/ville, contacts, profil actuel, institution/entreprise, réseaux sociaux, tranche d'abonnés, motivation, plan de mobilisation, portée estimée, participation antérieure, canaux préférés, disponibilité, RGPD.

### 1.6 Candidature Partenaire / Sponsor
Alimente `partners` (statut `pending`).

| Champ formulaire | Colonne | Contrainte |
|---|---|---|
| Nom de l'organisation | `organization_name` | requis |
| Secteur | `sector` | select |
| Pays / ville | `country` / `city` | requis |
| Site web | `website_url` | optionnel |
| Nom du contact | `contact_name` | requis |
| Poste du contact | `contact_position` | requis |
| Email / téléphone contact | `contact_email` / `contact_phone` | requis |
| **Type de partenariat** | `level_id` | **select obligatoire**, options chargées depuis `partner_levels` (Gold, Silver, Bronze...) |
| Budget disponible | `has_budget` | select |
| Objectifs | `objectives` | texte libre, requis |
| Sponsor précédent | `previous_sponsor` | checkbox |
| Message | `message` | optionnel |
| Comment ils nous ont connus | `heard_from` | optionnel |
| RGPD | `gdpr_consent` | requis |

### 1.7 Contact
Alimente `contact_messages` : nom, email, sujet, message.

### 1.8 Liste d'attente
Alimente `waitlist` : email uniquement.

---

## 2. Formulaires / actions back-office (authentifié `admin_users`)

- **Connexion admin** : email + mot de passe → session/JWT.
- **Gestion référentiels** (CRUD) : `days`, `pass_types`, `partner_levels`, `faq_categories`, `promo_codes`.
- **Gestion programme** : créer/modifier une session de conférence dans `sessions_conf` (jour, titre, catégorie, horaires, salle, speaker).
- **Traitement des candidatures** : formulaire de validation pour `speakers`, `ambassadors`, `partners` — changer `status` (`pending` → `accepted`/`confirmed`/`rejected`), avec `updated_by` = l'admin connecté. Pour un ambassadeur accepté, génération automatique d'un `promo_code` lié.
- **Gestion FAQ** : CRUD `faqs` par catégorie.
- **Messages de contact** : liste + marquer comme lu (`is_read`).
- **Suivi participants/tickets/paiements** : lecture seule, recherche par email/numéro de ticket, réémission de billet si besoin.
- **Saisie des statistiques** : formulaire simple pour ajouter/modifier une ligne `site_metrics` (clé de métrique, date, valeur, note).

---

## 3. Résumé des endpoints

### Public

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/registrations` | Créer ou mettre à jour une pré-inscription |
| GET | `/api/registrations/resume/:token` | Récupérer une pré-inscription via son token |
| POST | `/api/payments` | Initier un paiement pour une pré-inscription |
| POST | `/api/payments/webhook` | Webhook du prestataire de paiement |
| GET | `/api/tickets/:ticketNumber` | Vérifier/afficher un billet (QR code) |
| POST | `/api/speakers/apply` | Soumettre une candidature speaker |
| POST | `/api/ambassadors/apply` | Soumettre une candidature ambassadeur |
| POST | `/api/partners/apply` | Soumettre une candidature partenaire |
| POST | `/api/contact` | Envoyer un message de contact |
| POST | `/api/waitlist` | S'inscrire à la liste d'attente |
| GET | `/api/program` | Programme public (sessions + speakers confirmés) |
| GET | `/api/speakers` | Liste des speakers publics |
| GET | `/api/partners` | Liste des partenaires publics |
| GET | `/api/faqs` | Liste des FAQ par catégorie |
| GET | `/api/pass-types` | Types de pass actifs et tarifs |
| POST | `/api/promo-codes/validate` | Vérifier la validité d'un code promo |

### Admin (authentifié)

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/admin/auth/login` | Connexion admin |
| POST | `/api/admin/auth/logout` | Déconnexion |
| GET/POST/PUT/DELETE | `/api/admin/days` | Gestion des jours |
| GET/POST/PUT/DELETE | `/api/admin/pass-types` | Gestion des types de pass |
| GET/POST/PUT/DELETE | `/api/admin/partner-levels` | Gestion des niveaux de partenariat |
| GET/POST/PUT/DELETE | `/api/admin/faq-categories` | Gestion des catégories FAQ |
| GET/POST/PUT/DELETE | `/api/admin/faqs` | Gestion des FAQ |
| GET/POST/PUT/DELETE | `/api/admin/promo-codes` | Gestion des codes promo |
| GET/POST/PUT/DELETE | `/api/admin/sessions` | Gestion du programme |
| GET | `/api/admin/speakers` | Liste des candidatures speakers |
| PATCH | `/api/admin/speakers/:id/status` | Valider / rejeter une candidature speaker |
| GET | `/api/admin/ambassadors` | Liste des candidatures ambassadeurs |
| PATCH | `/api/admin/ambassadors/:id/status` | Valider / rejeter (génère un promo code si accepté) |
| GET | `/api/admin/partners` | Liste des candidatures partenaires |
| PATCH | `/api/admin/partners/:id/status` | Valider / rejeter une candidature partenaire |
| GET | `/api/admin/participants` | Liste des participants (lecture) |
| GET | `/api/admin/tickets` | Liste des billets (lecture) |
| GET | `/api/admin/payments` | Liste des paiements (lecture) |
| GET | `/api/admin/contact-messages` | Liste des messages de contact |
| PATCH | `/api/admin/contact-messages/:id/read` | Marquer un message comme lu |
| GET/POST/PUT | `/api/admin/site-metrics` | Consulter / saisir les statistiques manuelles |


