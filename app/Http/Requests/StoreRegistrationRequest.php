<?php

namespace App\Http\Requests;

use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Validator;

class StoreRegistrationRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
      public function authorize(): bool
    {
        return true; // formulaire public
    }

    public function rules(): array
    {
        return [
            'first_name'         => 'required|string|max:100',
            'last_name'          => 'required|string|max:100',
            'gender'             => 'nullable|in:Homme,Femme,Autre',
            'email'              => 'required|email:rfc,dns|max:255',
            'phone_whatsapp'     => 'required|string|max:20|regex:/^\+?[0-9]{7,15}$/',
            'country'            => 'required|string|max:100',
            'city'               => 'required|string|max:100',
            'sector'             => 'nullable|in:Dev,Data,Design,Cybersec,Product,IA,Autre',
            'profile'            => 'required|in:Étudiant,Professionnel,Entrepreneur,Recruteur,Autre',
            'profile_other'      => 'nullable|string|max:100', // requis seulement si profile = 'Autre', cf. withValidator()
            'experience_level'   => 'nullable|in:Débutant,Junior,Senior,Expert',
            'linkedin_url'       => 'nullable|url:https|max:255',
            'portfolio_url'      => 'nullable|url:https|max:255',
            'heard_from'         => 'nullable|in:Amis,WhatsApp,Autre',
            'special_needs'      => 'nullable|string|max:500',
            // exists avec condition : le pass doit être actif, pas juste exister
            'pass_type_id'       => 'required|integer|exists:pass_types,id,is_active,1',
            'promo_code'         => 'nullable|string|max:50',
            'gdpr_consent'       => 'required|accepted',
            'newsletter_consent' => 'boolean',
            'website_confirm'    => 'prohibited', // honeypot : doit rester vide
            //'recaptcha_token'    => ['required', 'string', new Recaptcha], // classe définie dans securite.md §9
        ];
    }

    public function messages(): array
    {
        return [
            'gdpr_consent.accepted' => 'Vous devez accepter le traitement de vos données.',
            'profile.required'      => 'Sélectionnez un profil.',
            'pass_type_id.exists'   => 'Ce type de pass est invalide ou n\'est plus disponible.',
        ];
    }

    // Règles métier qui ne peuvent pas s'exprimer avec les règles Laravel classiques
    public function withValidator(Validator $validator): void
    {
        $validator->after(function (Validator $v) {
            if (ParticipantRequest::where('email', $this->input('email'))->exists()) {
                $v->errors()->add('email', 'Cet email est déjà inscrit et le paiement a été confirmé.');
            }

            if ($this->input('profile') === 'Autre' && ! $this->filled('profile_other')) {
                $v->errors()->add('profile_other', 'Précisez votre profil.');
            }
        });
    }
}
