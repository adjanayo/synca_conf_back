<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('ambassador_applications', function (Blueprint $table) {
            $table->id();
            $table->string('nom');
            $table->string('email');
            $table->text('motivation');
            $table->text('strategie')->nullable();
            $table->integer('estimation_participants')->nullable();
            $table->string('statut')->default('pending');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('ambassador_applications');
    }
};
