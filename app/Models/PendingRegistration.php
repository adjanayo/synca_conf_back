<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PendingRegistration extends Model
{
    //
    protected $fillable = [
        'first_name', 'last_name', 'gender', 'email', 'phone_whatsapp',
        'country', 'city', 'sector', 'profile', 'profile_other',
        'experience_level', 'linkedin_url', 'portfolio_url', 'heard_from',
        'special_needs', 'gdpr_consent', 'newsletter_consent',
        'pass_type_id', 'promo_code_id',
    ];

    // Jamais exposé dans une réponse JSON, même par erreur
    protected $hidden = ['resume_token_hash'];

    protected function casts(): array
    {
        return [
            'gdpr_consent'       => 'boolean',
            'newsletter_consent' => 'boolean',
            'token_expires_at'   => 'datetime',
        ];
    }

    public function passType()
    {
        return $this->belongsTo(PassType::class);
    }

    public function promoCode()
    {
        return $this->belongsTo(PromoCode::class);
    }
}
