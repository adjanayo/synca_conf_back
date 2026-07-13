<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('ambassadors', function (Blueprint $table) {
            $table->id();
            $table->string('nom');
            $table->string('email');
            $table->string('pays');
            $table->string('ville')->nullable();
            $table->string('profil')->nullable();
            $table->string('reseaux')->nullable();
            $table->integer('nombre_followers')->nullable();
            $table->string('statut')->default('pending');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('ambassadors');
    }
};
