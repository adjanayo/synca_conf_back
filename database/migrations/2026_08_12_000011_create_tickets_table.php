<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('tickets', function (Blueprint $table) {
            $table->id();
            $table->foreignId('participant_id')->constrained('participants');
            $table->foreignId('payment_id')->unique()->constrained('payments');
            $table->foreignId('pass_type_id')->constrained('pass_types');
            $table->string('ticket_number', 20)->unique();
            $table->string('qr_code_hash')->unique();
            $table->string('pdf_url')->nullable();
            $table->boolean('is_scanned')->default(false);
            $table->timestamp('scanned_at')->nullable();
            $table->timestamp('created_at')->useCurrent();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('tickets');
    }
};
