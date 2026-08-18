# SYNCA CONF 2027 — Sécurité Backend (Laravel API)

> Backend : Laravel 11+ · PHP 8.2+ · PostgreSQL · API REST

---

## 1. Authentification & Autorisation

### 1.1 Laravel Sanctum (API Tokens)

```bash
php artisan install:api
```

```php
// config/sanctum.php
return [
    'stateful'  => explode(',', env('SANCTUM_STATEFUL_DOMAINS', 'localhost,localhost:3000')),
    'guard'     => ['web', 'api'],
    'expiration' => env('SANCTUM_TOKEN_EXPIRATION', 1440), // 24h en minutes
];
```

```php
// app/Models/AdminUser.php
class AdminUser extends Authenticatable
{
    use HasApiTokens;

    protected $fillable = ['email', 'password', 'role'];
    protected $hidden   = ['password', 'remember_token'];

    protected function casts(): array
    {
        return [
            'password'   => 'hashed',
            'last_login' => 'datetime',
        ];
    }
}
```

### 1.2 Routes protégées par auth:sanctum

```php
// routes/api.php
Route::prefix('admin')->middleware(['auth:sanctum', 'throttle:admin'])->group(function () {
    Route::get('/registrations', [AdminController::class, 'registrations']);
    Route::patch('/speakers/{id}', [AdminSpeakerController::class, 'updateStatus']);
    Route::get('/stats', [AdminStatsController::class, 'index']);
});
```

### 1.3 Politiques d'accès (Policies)

```php
// app/Policies/SpeakerPolicy.php
class SpeakerPolicy
{
    public function updateStatus(AdminUser $user): bool
    {
        return in_array($user->role, ['superadmin', 'admin']);
    }

    public function export(AdminUser $user): bool
    {
        return $user->role === 'superadmin';
    }
}
```

```php
// app/Http/Controllers/Admin/AdminSpeakerController.php
public function updateStatus(Request $request, Speaker $speaker)
{
    Gate::authorize('update-status', AdminUser::class); // lance 403 si pas autorisé

    $request->validate(['status' => 'required|in:accepted,rejected,confirmed']);
    $speaker->update(['status' => $request->status]);

    return response()->json(['message' => 'Statut mis à jour']);
}
```

### 1.4 Middleware rôles admin

```php
// app/Http/Middleware/RoleMiddleware.php
class RoleMiddleware
{
    public function handle(Request $request, Closure $next, string ...$roles): Response
    {
        if (! $request->user() || ! in_array($request->user()->role, $roles)) {
            return response()->json(['message' => 'Accès interdit.'], 403);
        }
        return $next($request);
    }
}
```

```php
// bootstrap/app.php
->withMiddleware(function (Middleware $middleware) {
    $middleware->alias([
        'role' => \App\Http\Middleware\RoleMiddleware::class,
    ]);
});
```

---

## 2. Rate Limiting (Protection anti-brute-force)

```php
// app/Providers/AppServiceProvider.php
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Support\Facades\RateLimiter;

public function boot(): void
{
    RateLimiter::for('api', function (Request $request) {
        return Limit::perMinute(60)->by($request->ip());
    });

    RateLimiter::for('admin', function (Request $request) {
        return Limit::perMinute(30)->by($request->user()?->id ?: $request->ip());
    });

    RateLimiter::for('login', function (Request $request) {
        return Limit::perMinute(5)->by($request->input('email').'|'.$request->ip());
    });

    RateLimiter::for('forms', function (Request $request) {
        return Limit::perMinute(3)->by($request->input('email').'|'.$request->ip());
    });
}
```

```php
// routes/api.php
Route::post('/admin/login', [AuthController::class, 'login'])->middleware('throttle:login');
Route::post('/register', [RegistrationController::class, 'store'])->middleware('throttle:forms');
Route::post('/speakers/apply', [SpeakerController::class, 'store'])->middleware('throttle:forms');
Route::post('/ambassadors/apply', [AmbassadorController::class, 'store'])->middleware('throttle:forms');
Route::post('/partners/apply', [PartnerController::class, 'store'])->middleware('throttle:forms');
Route::post('/contact', [ContactController::class, 'store'])->middleware('throttle:forms');
```

---

## 3. Validation des entrées (Form Requests)

Ne jamais faire confiance aux données utilisateur. Toujours utiliser des **Form Requests** dédiées.

```php
// app/Http/Requests/RegisterParticipantRequest.php
class RegisterParticipantRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true; // formulaire public
    }

    public function rules(): array
    {
        return [
            'first_name'        => 'required|string|max:100',
            'last_name'         => 'required|string|max:100',
            'gender'            => 'required|in:Homme,Femme,Autre',
            'email'             => 'required|email:rfc,dns|max:255|unique:users,email',
            'phone_whatsapp'    => 'required|string|max:20|regex:/^\+?[0-9]{7,15}$/',
            'country'           => 'required|string|max:100',
            'city'              => 'required|string|max:100',
            'profiles'          => 'required|array|min:1',
            'profiles.*'        => 'in:Étudiant,Professionnel,Entrepreneur,Recruteur,Autre',
            'sector'            => 'required|in:Dev,Data,Design,Cybersec,Product,IA,Autre',
            'experience_level'  => 'required|in:Débutant,Junior,Senior,Expert',
            'pass_type_id'      => 'required|exists:pass_types,id',
            'promo_code'        => 'nullable|string|max:50',
            'linkedin_url'      => 'nullable|url:https|max:255',
            'portfolio_url'     => 'nullable|url:https|max:255',
            'special_needs'     => 'nullable|string|max:500',
            'heard_from'        => 'nullable|string|max:100',
            'gdpr_consent'      => 'required|accepted',
            'newsletter_consent'=> 'boolean',
        ];
    }

    public function messages(): array
    {
        return [
            'gdpr_consent.accepted' => 'Vous devez accepter le traitement de vos données.',
            'email.unique'          => 'Cet email est déjà inscrit.',
            'profiles.min'          => 'Sélectionnez au moins un profil.',
        ];
    }
}
```

```php
// app/Http/Requests/ApplySpeakerRequest.php
class ApplySpeakerRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'first_name'          => 'required|string|max:100',
            'last_name'           => 'required|string|max:100',
            'title_role'          => 'required|string|max:200',
            'company'             => 'nullable|string|max:200',
            'country'             => 'required|string|max:100',
            'email'               => 'required|email:rfc,dns|max:255',
            'phone_whatsapp'      => 'required|string|max:20',
            'linkedin_url'        => 'nullable|url:https|max:255',
            'website_url'         => 'nullable|url:https|max:255',
            'photo'               => 'required|file|mimes:jpg,jpeg,png|min:1024|max:5120',
            'intervention_format' => 'required|in:Keynote,Panel,Workshop,Lightning Talk,Fireside Chat',
            'intervention_title'  => 'required|string|max:100',
            'theme'               => 'required|in:IA,EdTech,Entrepreneuriat,Carrières,Impact,Cybersec',
            'summary'             => 'required|string|max:3000',
            'audience_level'      => 'required|in:Débutant,Intermédiaire,Avancé,Tous',
            'language'            => 'required|in:Français,Anglais,Bilingue,Autre',
            'past_experience'     => 'nullable|string|max:3000',
            'video_link'          => 'nullable|url|max:255',
            'availability'        => 'required|in:Oui confirmé,Sous réserve,Besoin aide déplacement',
            'departure_city'      => 'nullable|string|max:100',
            'needs_accommodation' => 'boolean',
            'motivation'          => 'required|string|max:2250',
            'video_consent'       => 'required|in:Oui sans restriction,Oui avec validation,Non',
            'gdpr_consent'        => 'required|accepted',
        ];
    }
}
```

### Règle d'or : `$fillable` sur tous les modèles

```php
// app/Models/User.php
class User extends Model
{
    protected $fillable = [
        'first_name', 'last_name', 'gender', 'email', 'email_verified',
        'phone_whatsapp', 'country', 'city', 'sector', 'experience_level',
        'linkedin_url', 'portfolio_url', 'special_needs', 'heard_from',
        'gdpr_consent', 'newsletter_consent',
    ];

    protected $hidden = ['gdpr_consent']; // jamais exposé via API
}
```

---

## 4. Protection contre les injections SQL

**Eloquent utilise PDO + prepared statements par défaut.** Ne jamais utiliser `DB::raw()` avec des entrées utilisateur.

```php
// ❌ DANGEREUX
DB::select("SELECT * FROM users WHERE email = '{$request->email}'");

// ✅ OK — Eloquent
User::where('email', $request->email)->first();

// ✅ OK — Query Builder avec bindings
DB::select('SELECT * FROM users WHERE email = ?', [$request->email]);
```

---

## 5. CORS (Cross-Origin Resource Sharing)

```bash
php artisan config:publish cors
```

```php
// config/cors.php
return [
    'paths'                    => ['api/*', 'sanctum/csrf-cookie'],
    'allowed_methods'          => ['GET', 'POST', 'PATCH', 'OPTIONS'],
    'allowed_origins'          => [env('FRONTEND_URL', 'https://conf2027.sync-africa.com')],
    'allowed_origins_patterns' => [],
    'allowed_headers'          => ['Content-Type', 'X-Requested-With', 'Authorization', 'Accept'],
    'exposed_headers'          => [],
    'max_age'                  => 86400,
    'supports_credentials'     => true,
];
```

---

## 6. Headers de sécurité HTTP

```php
// app/Http/Middleware/SecurityHeaders.php
class SecurityHeaders
{
    public function handle(Request $request, Closure $next): Response
    {
        $response = $next($request);

        $response->headers->set('X-Frame-Options', 'DENY');
        $response->headers->set('X-Content-Type-Options', 'nosniff');
        $response->headers->set('X-XSS-Protection', '0');
        $response->headers->set('Referrer-Policy', 'strict-origin-when-cross-origin');
        $response->headers->set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
        $response->headers->set('X-Permitted-Cross-Domain-Policies', 'none');
        $response->headers->set('Cross-Origin-Resource-Policy', 'same-site');

        if (app()->isProduction()) {
            $response->headers->set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
        }

        $response->headers->set('Content-Security-Policy',
            "default-src 'none'; "
            . "connect-src 'self' https://api.stripe.com; "
            . "img-src 'self' https://res.cloudinary.com data:; "
            . "style-src 'self' 'unsafe-inline'; "
            . "script-src 'self'; "
            . "frame-ancestors 'none'; "
            . "form-action 'self'; "
        );

        return $response;
    }
}
```

```php
// bootstrap/app.php
->withMiddleware(function (Middleware $middleware) {
    $middleware->append(SecurityHeaders::class);
});
```

---

## 7. Sécurité des fichiers uploadés

```php
// app/Http/Controllers/SpeakerController.php
public function store(ApplySpeakerRequest $request): JsonResponse
{
    $validated = $request->validated();

    if ($request->hasFile('photo')) {
        $file = $request->file('photo');

        // Vérifier le type MIME réel (pas seulement l'extension)
        $allowedMimes = ['image/jpeg', 'image/png'];
        if (! in_array($file->getMimeType(), $allowedMimes)) {
            return response()->json(['message' => 'Type de fichier non autorisé.'], 422);
        }

        // Vérifier qu'il s'agit d'une vraie image
        if (! getimagesize($file->path())) {
            return response()->json(['message' => 'Fichier image invalide.'], 422);
        }

        // Stocker hors du document root public
        $path = $file->store('speakers/photos', 'cloudinary');
        $validated['photo_url'] = $path;
    }

    unset($validated['photo']);

    $speaker = Speaker::create($validated + ['status' => 'pending']);

    // Email accusé de réception
    Mail::to($speaker->email)->queue(new SpeakerAcknowledgement($speaker));

    return response()->json([
        'message'   => 'Candidature envoyée avec succès.',
        'speaker_id'=> $speaker->id,
    ], 201);
}
```

### Règles fichiers upload :

| Règle | Valeur |
|-------|--------|
| Taille max | 5 Mo (photo), 10 Mo (logo partenaire) |
| Extensions autorisées | jpg, jpeg, png uniquement |
| Vérification MIME | `getimagesize()` + `finfo` |
| Stockage | Cloudinary / S3 (jamais sur le serveur web) |
| Renommage | UUID + timestamp (jamais le nom original) |

---

## 8. Sécurité des paiements

```php
// app/Services/PaymentService.php
class PaymentService
{
    public function createPayment(User $user, PassType $pass, ?PromoCode $promoCode): array
    {
        $amount = $pass->price;

        if ($promoCode) {
            $this->validatePromoCode($promoCode);
            $amount = $this->applyDiscount($pass->price, $promoCode);
        }

        $payment = Payment::create([
            'user_id'         => $user->id,
            'pass_type_id'    => $pass->id,
            'promo_code_id'   => $promoCode?->id,
            'amount_original' => $pass->price,
            'amount_paid'     => $amount,
            'status'          => 'pending',
        ]);

        return [
            'payment_id'     => $payment->id,
            'amount'         => $amount,
            'currency'       => 'XOF',
            'callback_url'   => route('payments.callback', ['payment' => $payment->id]),
        ];
    }

    public function handleWebhook(string $payload, string $signature): void
    {
        // Vérifier la signature du webhook (Stripe, CinetPay, etc.)
        if (! $this->verifyWebhookSignature($payload, $signature)) {
            Log::warning('Webhook signature invalide', ['ip' => request()->ip()]);
            abort(401, 'Signature invalide.');
        }

        $data = json_decode($payload, true);

        $payment = Payment::where('transaction_ref', $data['reference'])->firstOrFail();

        if ($payment->status !== 'pending') {
            Log::warning('Webhook reçu pour un paiement déjà traité', ['payment_id' => $payment->id]);
            return;
        }

        if ($data['status'] === 'success') {
            DB::transaction(function () use ($payment) {
                $payment->update(['status' => 'completed', 'paid_at' => now()]);

                // Génération billet
                $ticket = TicketService::generate($payment);

                // Email billet
                Mail::to($payment->user->email)->queue(new TicketMail($ticket));
            });
        } else {
            $payment->update(['status' => 'failed']);
        }
    }
}
```

### Checklist paiement :

- [ ] Stripe webhook signing secret vérifié à chaque callback
- [ ] CinetPay / Wave / Orange Money : vérifier signature HMAC
- [ ] Idempotence : ne jamais traiter 2x le même paiement
- [ ] `DB::transaction()` pour atomicité paiement + ticket
- [ ] Logs de toutes les tentatives (succès + échecs)
- [ ] Cartes bancaires jamais stockées (Stripe tokenise tout)

---

## 9. Protection anti-spam (reCAPTCHA v3)

```php
// app/Rules/Recaptcha.php
class Recaptcha implements ValidationRule
{
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $response = Http::asForm()->post('https://www.google.com/recaptcha/api/siteverify', [
            'secret'   => config('services.recaptcha.secret_key'),
            'response' => $value,
            'remoteip' => request()->ip(),
        ]);

        $result = $response->json();

        if (! $result['success'] || $result['score'] < 0.5) {
            $fail('Validation reCAPTCHA échouée.');
        }
    }
}
```

```php
// app/Http/Requests/ContactRequest.php
public function rules(): array
{
    return [
        'name'     => 'required|string|max:200',
        'email'    => 'required|email:rfc,dns|max:255',
        'subject'  => 'nullable|string|max:255',
        'message'  => 'required|string|max:5000',
        'captcha'  => ['required', 'string', new Recaptcha],
    ];
}
```

---

## 10. Variables d'environnement (`.env`)

```bash
# .env (jamais commité — ajouter .env à .gitignore)
APP_ENV=production
APP_DEBUG=false
APP_URL=https://conf2027.sync-africa.com

DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=synca_conf
DB_USERNAME=app_user           # jamais root/superuser
DB_PASSWORD=XXXXXXXXXXXXXXXX

SANCTUM_TOKEN_EXPIRATION=1440

FRONTEND_URL=https://conf2027.sync-africa.com

STRIPE_KEY=pk_live_XXXXXXXXXXXX
STRIPE_SECRET=sk_live_XXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXX

CINETPAY_API_KEY=XXXXXXXXXXXX
CINETPAY_SECRET=XXXXXXXXXXXX

CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

MAIL_MAILER=resend
RESEND_API_KEY=re_XXXXXXXXXXXX

RECAPTCHA_SITE_KEY=XXXXXXXXXXXX
RECAPTCHA_SECRET_KEY=XXXXXXXXXXXX
```

```bash
# php artisan env:encrypt (Laravel 9+)
php artisan env:encrypt --key=$(php artisan key:generate --show)
# Génère .env.encrypted → seul le fichier encrypté est commité (pas .env)
```

---

## 11. Logging & Monitoring

```php
// config/logging.php
'channels' => [
    'security' => [
        'driver'  => 'daily',
        'path'    => storage_path('logs/security.log'),
        'level'   => env('LOG_LEVEL', 'warning'),
        'days'    => 90,
    ],
    'payment' => [
        'driver'  => 'daily',
        'path'    => storage_path('logs/payment.log'),
        'level'   => 'info',
        'days'    => 365,
    ],
];
```

```php
// app/Http/Middleware/AuditLog.php
class AuditLog
{
    public function handle(Request $request, Closure $next): Response
    {
        if ($request->is('api/admin/*') && $request->user()) {
            Log::channel('security')->info('Admin action', [
                'user_id'  => $request->user()->id,
                'email'    => $request->user()->email,
                'method'   => $request->method(),
                'url'      => $request->fullUrl(),
                'ip'       => $request->ip(),
                'user_agent' => $request->userAgent(),
            ]);
        }

        return $next($request);
    }
}
```

### Événements à logguer :

| Événement | Canal | Niveau |
|-----------|-------|--------|
| Connexion admin réussie | `security` | `info` |
| Connexion admin échouée | `security` | `warning` |
| Création/modification admin | `security` | `info` |
| Paiement réussi | `payment` | `info` |
| Paiement échoué | `payment` | `warning` |
| Webhook signature invalide | `security` | `warning` |
| Rate limit déclenché | `security` | `warning` |
| 403 / 401 répétés | `security` | `warning` |
| Upload fichier échoué | `security` | `warning` |

---

## 12. RGPD & Protection des données

```php
// app/Models/User.php
protected static function booted(): void
{
    // Anonymisation automatique après X mois d'inactivité (à planifier en cron)
    static::addGlobalScope('active', function (Builder $builder) {
        // Ne jamais exposer les données supprimées/anonymisées
    });
}
```

### Checklist conformité :

- [ ] Bandeau cookies + consentement explicite (RGPD)
- [ ] Case `gdpr_consent` obligatoire sur tous les formulaires
- [ ] Politique de confidentialité accessible depuis le footer
- [ ] Droit d'accès : endpoint `/api/user/me` pour récupérer ses données
- [ ] Droit à l'oubli : endpoint `DELETE /api/user/me` pour suppression
- [ ] Données personnelles jamais vendues à des tiers
- [ ] Chiffrement des données sensibles en base (`$casts` avec `encrypted`)
- [ ] HTTPS obligatoire sur toutes les pages

```php
// app/Http/Controllers/UserController.php
public function deleteMyData(Request $request): JsonResponse
{
    $user = $request->user();

    // Anonymiser plutôt que supprimer (garder les tickets pour audit)
    $user->update([
        'first_name'       => 'ANONYME',
        'last_name'        => 'ANONYME',
        'email'            => 'deleted_'.$user->id.'@anonymised.local',
        'phone_whatsapp'   => null,
        'linkedin_url'     => null,
        'portfolio_url'    => null,
        'special_needs'    => null,
        'email_verified'   => false,
    ]);

    Log::channel('security')->info('Compte anonymisé', ['user_id' => $user->id]);

    return response()->json(['message' => 'Vos données ont été supprimées.']);
}
```

---

## 13. Déploiement sécurisé

```bash
# Checklist déploiement
php artisan config:cache        # Cache config (pas de lecture .env à chaque requête)
php artisan route:cache         # Cache routes (plus rapide + pas de réflexion)
php artisan event:cache         # Cache events
php artisan view:cache          # Cache views (si Blade utilisé pour emails)

# Permissions fichiers
chmod -R 755 storage bootstrap/cache
chmod -R 775 storage/logs storage/framework

# .env jamais accessible depuis le web
# → document root pointe vers public/, pas la racine Laravel

# Cron pour tâches planifiées
* * * * * php /path/to/artisan schedule:run >> /dev/null 2>&1
```

```nginx
# nginx.conf — règles de sécurité
server {
    listen 443 ssl http2;
    server_name conf2027.sync-africa.com;

    # Désactiver les méthodes HTTP non utilisées
    if ($request_method !~ ^(GET|POST|PATCH|OPTIONS)$) {
        return 405;
    }

    # Bloquer l'accès aux fichiers sensibles
    location ~ /\.(?!well-known).* {
        deny all;
    }

    location ~ (\.env|composer\.json|composer\.lock|package\.json|yarn\.lock) {
        deny all;
    }

    # Toutes les requêtes passent par index.php
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # PHP-FPM
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;

        # Limiter la taille des requêtes
        client_max_body_size 10M;
    }
}
```

---

## 14. Récapitulatif — Checklist sécurité

### Avant mise en production :

- [ ] `APP_DEBUG=false` confirmé
- [ ] `APP_ENV=production` confirmé
- [ ] `APP_KEY` générée (32 caractères aléatoires)
- [ ] CORS restreint au domaine frontend uniquement
- [ ] Sanctum configuré avec expiration des tokens
- [ ] Rate limiting actif sur tous les endpoints publics
- [ ] reCAPTCHA v3 sur tous les formulaires publics
- [ ] Form Requests validant toutes les entrées
- [ ] `$fillable` défini sur tous les modèles (pas de `$guarded = []`)
- [ ] `$hidden` défini pour exclure `password`, `remember_token`, etc.
- [ ] Headers sécurité HTTP (CSP, HSTS, X-Frame-Options...)
- [ ] Webhooks paiement avec vérification de signature
- [ ] Fichiers uploadés vérifiés (MIME + `getimagesize()`)
- [ ] Stockage fichiers hors document root (Cloudinary/S3)
- [ ] `.env` encrypté ou hors repo — jamais de secrets dans le code
- [ ] Base de données : utilisateur dédié avec privilèges limités
- [ ] HTTPS forcé (HSTS activé)
- [ ] Logs sécurité et paiement séparés
- [ ] Backup automatique de la DB (quotidien)
- [ ] Cron `schedule:run` actif
- [ ] Nginx : méthodes HTTP limitées, fichiers sensibles bloqués

### Surveillance continue :

- [ ] Monitoring uptime (Oh Dear, Better Uptime)
- [ ] Alertes erreurs (Sentry, Flare)
- [ ] Dashboard logs (si possible)
- [ ] Tests de sécurité automatisés (CI/CD)
- [ ] Revue des logs sécurité hebdomadaire
