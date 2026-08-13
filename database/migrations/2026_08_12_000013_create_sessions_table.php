<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('sessions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('day_id')->constrained('days');
            $table->string('title', 200);
            $table->text('description')->nullable();
            $table->string('category', 50);
            $table->time('start_time');
            $table->time('end_time');
            $table->string('room', 100)->nullable();
            $table->unsignedBigInteger('speaker_id')->nullable();
            $table->boolean('is_public')->default(true);
            $table->timestamps();
            $table->foreignId('updated_by')->nullable()->constrained('admin_users')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('sessions');
    }
};
