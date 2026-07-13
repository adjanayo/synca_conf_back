<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PartnerApplication extends Model
{
    protected $fillable = [
        'organisation',
        'secteur',
        'nom_contact',
        'email',
        'offre_souhaitee',
        'budget',
        'message',
        'statut',
    ];

    protected $casts = [
        'budget' => 'decimal:2',
    ];
}
