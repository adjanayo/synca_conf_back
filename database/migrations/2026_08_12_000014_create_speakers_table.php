<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('speakers', function (Blueprint $table) {
            $table->id();
            $table->string('first_name', 100);
            $table->string('last_name', 100);
            $table->string('title_role', 200);
            $table->string('company', 200)->nullable();
            $table->string('country', 100);
            $table->string('email');
            $table->string('phone_whatsapp', 20);
            $table->string('linkedin_url')->nullable();
            $table->string('website_url')->nullable();
            $table->string('photo_url')->nullable();
            $table->string('intervention_format', 50);
            $table->string('intervention_title', 100);
            $table->string('theme', 50);
            $table->text('summary');
            $table->string('audience_level', 20)->nullable();
            $table->string('language', 30)->nullable();
            $table->text('past_experience')->nullable();
            $table->string('video_link')->nullable();
            $table->string('availability', 30)->nullable();
            $table->string('departure_city', 100)->nullable();
            $table->boolean('needs_accommodation')->default(false);
            $table->text('motivation');
            $table->string('video_consent', 30)->nullable();
            $table->boolean('gdpr_consent')->default(false);
            $table->string('status', 20)->default('pending');
            $table->boolean('is_public')->default(false);
            $table->timestamps();
            $table->foreignId('updated_by')->nullable()->constrained('admin_users')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('speakers');
    }
};
