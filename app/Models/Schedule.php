<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Schedule extends Model
{
    protected $fillable = [
        'titre',
        'description',
        'date',
        'heure_debut',
        'heure_fin',
        'type',
        'salle',
    ];

    public function speakers(): BelongsToMany
    {
        return $this->belongsToMany(Speaker::class, 'schedule_speakers');
    }
}
