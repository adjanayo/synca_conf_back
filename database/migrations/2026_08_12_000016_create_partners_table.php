<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('partners', function (Blueprint $table) {
            $table->id();
            $table->string('organization_name', 200);
            $table->string('sector', 50);
            $table->string('country', 100);
            $table->string('city', 100);
            $table->string('website_url')->nullable();
            $table->string('contact_name', 200);
            $table->string('contact_position', 200);
            $table->string('contact_email');
            $table->string('contact_phone', 20);
            $table->foreignId('level_id')->constrained('partner_levels');
            $table->string('has_budget', 30)->nullable();
            $table->text('objectives');
            $table->boolean('previous_sponsor')->default(false);
            $table->text('message')->nullable();
            $table->string('heard_from', 100)->nullable();
            $table->boolean('gdpr_consent')->default(false);
            $table->string('status', 20)->default('pending');
            $table->string('logo_url')->nullable();
            $table->boolean('is_public')->default(false);
            $table->timestamps();
            $table->foreignId('updated_by')->nullable()->constrained('admin_users')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('partners');
    }
};
