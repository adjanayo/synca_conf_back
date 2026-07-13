<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class SpeakerApplication extends Model
{
    protected $fillable = [
        'nom',
        'email',
        'entreprise',
        'titre_intervention',
        'format',
        'thematique',
        'resume',
        'niveau',
        'langue',
        'statut',
    ];
}
