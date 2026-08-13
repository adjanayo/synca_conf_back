<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('pass_types', function (Blueprint $table) {
            $table->id();
            $table->string('name', 50)->unique();
            $table->unsignedInteger('price');
            $table->text('description')->nullable();
            $table->text('inclusions')->nullable();
            $table->unsignedInteger('max_days')->default(3);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            $table->foreignId('updated_by')->nullable()->constrained('admin_users')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pass_types');
    }
};
