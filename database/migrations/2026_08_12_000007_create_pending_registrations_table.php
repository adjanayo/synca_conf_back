<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('pending_registrations', function (Blueprint $table) {
            $table->id();
            $table->string('resume_token', 64)->unique();
            $table->timestamp('token_expires_at');
            $table->string('first_name', 100);
            $table->string('last_name', 100);
            $table->string('gender', 20)->nullable();
            $table->string('email')->unique();
            $table->string('phone_whatsapp', 20);
            $table->string('country', 100);
            $table->string('city', 100);
            $table->string('sector', 50)->nullable();
            $table->string('profile', 30)->nullable();
            $table->string('experience_level', 30)->nullable();
            $table->string('linkedin_url')->nullable();
            $table->string('portfolio_url')->nullable();
            $table->string('heard_from', 100)->nullable();
            $table->text('special_needs')->nullable();
            $table->boolean('gdpr_consent')->default(false);
            $table->boolean('newsletter_consent')->default(false);
            $table->foreignId('pass_type_id')->constrained('pass_types');
            $table->foreignId('promo_code_id')->nullable()->constrained('promo_codes')->nullOnDelete();
            $table->string('status', 20)->default('en_attente_paiement');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pending_registrations');
    }
};
