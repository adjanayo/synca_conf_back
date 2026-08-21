<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Http\Requests\StoreRegistrationRequest;
use App\Models\PendingRegistration;
use App\Models\PromoCode;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Str;

class PendingRegistrationController extends Controller
{
    //
     public function store(StoreRegistrationRequest $request): JsonResponse
    {
        $validated = $request->validated();
        $profiles  = $validated['profiles'];
        unset($validated['profiles'], $validated['recaptcha_token'], $validated['website_confirm']);

        // Code promo : résolu par code, jamais l'id envoyé directement par le client
        $promoCode = null;
        if (! empty($validated['promo_code'])) {
            $promoCode = PromoCode::where('code', $validated['promo_code'])
                ->where('is_active', true)
                ->where(function ($q) {
                    $q->whereNull('valid_until')->orWhere('valid_until', '>=', now());
                })
                ->first();
        }
        unset($validated['promo_code']);
        $validated['promo_code_id'] = $promoCode?->id;

        [$registration, $plainToken] = DB::transaction(function () use ($validated, $profiles) {
            $existing = PendingRegistration::where('email', $validated['email'])
                ->where('status', 'en_attente_paiement')
                ->lockForUpdate()
                ->first();

            $plainToken = null;

            if ($existing) {
                $existing->update($validated);
                $existing->profiles()->delete();
            } else {
                $plainToken = \Illuminate\Support\Str::random(64);
                $validated['resume_token_hash'] = hash('sha256', $plainToken);
                $validated['token_expires_at']  = now()->addDays(7);
                $existing = PendingRegistration::create($validated);
            }

            foreach ($profiles as $profile) {
                $existing->profiles()->create(['profile' => $profile]);
            }

            return [$existing, $plainToken];
        });

        // On envoie/renvoie systématiquement un lien de reprise valide.
        // Si la ligne existait déjà, on génère un nouveau token (rotation) plutôt
        // que de tenter de retrouver l'ancien token en clair (impossible, il est hashé).
        if (! $plainToken) {
            $plainToken = \Illuminate\Support\Str::random(64);
            $registration->update([
                'resume_token_hash' => hash('sha256', $plainToken),
                'token_expires_at'  => now()->addDays(7),
            ]);
        }

        //Mail::to($registration->email)->queue(new ResumeRegistrationMail($registration, $plainToken));

            // Log::channel('security')->info('Pré-inscription créée ou mise à jour', [
            //     'registration_id' => $registration->id,
            //     'ip'               => $request->ip(),
            // ]);

        return response()->json([
            'message'         => 'Inscription enregistrée. Vérifiez votre email pour finaliser le paiement.',
            'registration_id' => $registration->id,
        ], 201);
    }

    public function resume(string $token): JsonResponse
    {
        $registration = PendingRegistration::where('resume_token_hash', hash('sha256', $token))
            ->where('token_expires_at', '>', now())
            ->where('status', 'en_attente_paiement')
            ->with('profiles')
            ->first();

        if (! $registration) {
            //Log::channel('security')->warning('Tentative de reprise avec token invalide/expiré', [
            //    'ip' => request()->ip(),
            //]);

            return response()->json(['message' => 'Lien invalide ou expiré.'], 404);
        }

        return response()->json(['registration' => $registration]);
    }
}
