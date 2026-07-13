<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Ambassador extends Model
{
    protected $fillable = [
        'nom',
        'email',
        'pays',
        'ville',
        'profil',
        'reseaux',
        'nombre_followers',
        'statut',
    ];
}
