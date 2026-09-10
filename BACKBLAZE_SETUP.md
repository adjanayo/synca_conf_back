# Backblaze B2 — config à faire

Sans ça, tout formulaire avec upload de fichier (photo speaker, photo
ambassadeur, logo partenaire, visuel exposant, photo membre hackathon)
échoue (503 "service de stockage indisponible").

## 1. Compte + bucket

1. Créer un compte sur https://www.backblaze.com/ (B2 Cloud Storage).
2. Créer un bucket (privé ou public selon besoin — ici public en lecture
   puisque les URLs générées sont servies directement au front).
3. Dans "App Keys", générer une clé d'application (Application Key) avec
   accès au bucket créé. Noter tout de suite l'`applicationKeyId` et
   l'`applicationKey` — cette dernière n'est affichée qu'une seule fois.

## 2. Variables à ajouter dans synca_conf_back/.env

```
B2_ENDPOINT_URL=https://s3.<region>.backblazeb2.com
B2_KEY_ID=<applicationKeyId>
B2_APPLICATION_KEY=<applicationKey>
B2_BUCKET_NAME=<nom du bucket>
B2_PUBLIC_URL=<url publique du bucket ou du CDN devant>
```

- `B2_ENDPOINT_URL` et la région : visibles sur la page du bucket dans le
  dashboard B2 (ex. `https://s3.eu-central-003.backblazeb2.com`).
- `B2_PUBLIC_URL` : soit l'URL "Friendly URL" du bucket donnée par
  Backblaze, soit un domaine CDN si un CDN est mis devant le bucket. C'est
  ce préfixe + la clé objet qui forme l'URL renvoyée au front après upload.

## 3. Redémarrer le backend

```
cd synca_conf_back
docker compose restart app
```

## 4. Vérifier

Soumettre un formulaire avec photo (ex. candidature speaker) et confirmer
qu'il n'y a plus de 503 et que la photo est bien accessible à l'URL
renvoyée.
