<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('site_metrics', function (Blueprint $table) {
            $table->id();
            $table->string('metric_key', 100);
            $table->date('metric_date');
            $table->unsignedInteger('value')->default(0);
            $table->text('note')->nullable();
            $table->timestamp('updated_at')->useCurrent();
            $table->foreignId('updated_by')->nullable()->constrained('admin_users')->nullOnDelete();
            $table->unique(['metric_key', 'metric_date']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('site_metrics');
    }
};
