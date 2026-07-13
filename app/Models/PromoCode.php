<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PromoCode extends Model
{
    protected $fillable = [
        'code',
        'type',
        'reduction',
        'date_expiration',
        'usage_max',
    ];

    protected $casts = [
        'reduction' => 'decimal:2',
        'date_expiration' => 'datetime',
    ];
}
