<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('partner_applications', function (Blueprint $table) {
            $table->id();
            $table->string('organisation');
            $table->string('secteur')->nullable();
            $table->string('nom_contact')->nullable();
            $table->string('email');
            $table->text('offre_souhaitee')->nullable();
            $table->decimal('budget', 10, 2)->nullable();
            $table->text('message')->nullable();
            $table->string('statut')->default('pending');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('partner_applications');
    }
};
