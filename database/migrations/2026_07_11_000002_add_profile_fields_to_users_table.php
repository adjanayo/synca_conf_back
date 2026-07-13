<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->string('nom')->nullable()->after('name');
            $table->string('prenom')->nullable()->after('nom');
            $table->string('email')->nullable()->change();
            $table->string('telephone')->nullable()->after('prenom');
            $table->string('pays')->nullable()->after('telephone');
            $table->string('ville')->nullable()->after('pays');
            $table->string('profil')->nullable()->after('ville');
            $table->string('secteur')->nullable()->after('profil');
            $table->string('niveau_experience')->nullable()->after('secteur');
            $table->boolean('consentement_rgpd')->default(false)->after('niveau_experience');
        });
    }

    public function down(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn(['nom', 'prenom', 'telephone', 'pays', 'ville', 'profil', 'secteur', 'niveau_experience', 'consentement_rgpd']);
        });
    }
};
