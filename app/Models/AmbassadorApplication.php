<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AmbassadorApplication extends Model
{
    protected $fillable = [
        'nom',
        'email',
        'motivation',
        'strategie',
        'estimation_participants',
        'statut',
    ];
}
