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
            $table->string('first_name', 100);
            $table->string('last_name', 100);
            $table->unsignedInteger('age');
            $table->string('country', 100);
            $table->string('city', 100);
            $table->string('email');
            $table->string('phone_whatsapp', 20);
            $table->string('current_profile', 30)->nullable();
            $table->string('institution_company', 200)->nullable();
            $table->string('linkedin_url')->nullable();
            $table->text('social_handles')->nullable();
            $table->string('followers_range', 20)->nullable();
            $table->text('motivation');
            $table->text('mobilization_plan');
            $table->string('estimated_reach', 20)->nullable();
            $table->boolean('previous_synca')->default(false);
            $table->text('preferred_channels');
            $table->string('availability_pre', 20)->nullable();
            $table->boolean('gdpr_consent')->default(false);
            $table->foreignId('promo_code_id')->nullable()->constrained('promo_codes')->nullOnDelete();
            $table->string('status', 20)->default('pending');
            $table->timestamps();
            $table->foreignId('updated_by')->nullable()->constrained('users')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('ambassadors');
    }
};
