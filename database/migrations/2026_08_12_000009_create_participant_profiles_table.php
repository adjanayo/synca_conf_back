<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('participant_profiles', function (Blueprint $table) {
            $table->id();
            $table->foreignId('participant_id')->constrained('participants')->cascadeOnDelete();
            $table->string('profile', 30);
            $table->unique(['participant_id', 'profile']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('participant_profiles');
    }
};
