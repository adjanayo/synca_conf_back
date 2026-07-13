<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('speaker_applications', function (Blueprint $table) {
            $table->id();
            $table->string('nom');
            $table->string('email');
            $table->string('entreprise')->nullable();
            $table->string('titre_intervention');
            $table->string('format')->nullable();
            $table->string('thematique');
            $table->text('resume')->nullable();
            $table->string('niveau')->nullable();
            $table->string('langue')->nullable();
            $table->string('statut')->default('en_attente');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('speaker_applications');
    }
};
