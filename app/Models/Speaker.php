<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Speaker extends Model
{
    protected $fillable = [
        'nom',
        'prenom',
        'entreprise',
        'poste',
        'bio',
        'photo_url',
        'linkedin',
        'statut',
    ];

    public function schedules(): BelongsToMany
    {
        return $this->belongsToMany(Schedule::class, 'schedule_speakers');
    }
}
