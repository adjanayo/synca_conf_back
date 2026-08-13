<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('participants', function (Blueprint $table) {
            $table->id();
            $table->foreignId('pending_registration_id')->unique()->nullable()->constrained('pending_registrations')->nullOnDelete();
            $table->string('first_name', 100);
            $table->string('last_name', 100);
            $table->string('gender', 20)->nullable();
            $table->string('email')->unique();
            $table->boolean('email_verified')->default(false);
            $table->string('phone_whatsapp', 20);
            $table->string('country', 100);
            $table->string('city', 100);
            $table->string('sector', 50)->nullable();
            $table->string('experience_level', 30)->nullable();
            $table->string('linkedin_url')->nullable();
            $table->string('portfolio_url')->nullable();
            $table->string('heard_from', 100)->nullable();
            $table->boolean('gdpr_consent')->default(false);
            $table->boolean('newsletter_consent')->default(false);
            $table->timestamp('created_at')->useCurrent();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('participants');
    }
};
