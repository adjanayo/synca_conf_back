# Backblaze B2 — config à faire

Sans ça, tout formulaire avec upload de fichier (photo speaker, photo
ambassadeur, logo partenaire, visuel exposant, photo membre hackathon)
échoue (503 "service de stockage indisponible").

**Dev identique à la prod** : B2 free tier (10 Go de stockage gratuit +
egress gratuit ~3x le stockage moyen) suffit largement pour le dev — pas
besoin d'un stockage local alternatif. Créer **deux buckets séparés sur le
même compte B2 gratuit** : `synca-dev` et `synca-prod` (ou équivalent). Même
stack partout, données isolées.

## 1. Compte + buckets

1. Créer un compte sur https://www.backblaze.com/ (B2 Cloud Storage).
2. Créer **deux buckets** — un par environnement (`synca-dev`, `synca-prod`)
   — publics en lecture, puisque les URLs générées sont servies directement
   au front.
3. Dans "App Keys", générer une Application Key **par bucket** (accès limité
   à son propre bucket — pas de clé partagée dev/prod). Noter tout de suite
   l'`applicationKeyId` et l'`applicationKey` de chacune — cette dernière
   n'est affichée qu'une seule fois.

## 2. Variables à ajouter dans `.env` (dev) et `.env.prod` (Contabo)

```
B2_ENDPOINT_URL=https://s3.<region>.backblazeb2.com
B2_KEY_ID=<applicationKeyId du bucket>
B2_APPLICATION_KEY=<applicationKey du bucket>
B2_BUCKET_NAME=<synca-dev ou synca-prod>
B2_PUBLIC_URL=<url publique du bucket ou du CDN devant>
```

- `B2_ENDPOINT_URL` et la région : visibles sur la page du bucket dans le
  dashboard B2 (ex. `https://s3.eu-central-003.backblazeb2.com`), identique
  pour les deux buckets s'ils sont dans la même région.
- `B2_PUBLIC_URL` : soit l'URL "Friendly URL" du bucket donnée par
  Backblaze, soit un domaine CDN si un CDN est mis devant le bucket. C'est
  ce préfixe + la clé objet qui forme l'URL renvoyée au front après upload.
- Utiliser le bucket `synca-dev` en local, `synca-prod` sur le serveur
  Contabo — même code, mêmes variables, valeurs différentes.

## 3. Redémarrer le backend

```
cd synca_conf_back
docker compose restart app
```

## 4. Vérifier

Soumettre un formulaire avec photo (ex. candidature speaker) et confirmer
qu'il n'y a plus de 503 et que la photo est bien accessible à l'URL
renvoyée.
