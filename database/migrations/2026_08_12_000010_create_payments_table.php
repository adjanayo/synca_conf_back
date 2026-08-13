<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('pending_registration_id')->constrained('pending_registrations');
            $table->foreignId('pass_type_id')->constrained('pass_types');
            $table->foreignId('promo_code_id')->nullable()->constrained('promo_codes')->nullOnDelete();
            $table->unsignedInteger('amount_original');
            $table->unsignedInteger('amount_paid');
            $table->string('currency', 10)->default('XOF');
            $table->string('payment_method', 30);
            $table->string('transaction_ref')->unique()->nullable();
            $table->string('status', 20)->default('pending');
            $table->timestamp('paid_at')->nullable();
            $table->timestamp('created_at')->useCurrent();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('payments');
    }
};
