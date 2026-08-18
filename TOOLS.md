# Outils installés sur la machine de dev

## 🐳 Docker / Conteneurs
- **docker** — prérequis (via Docker Desktop)
  ```bash
  # Désinstaller : supprimer Docker Desktop depuis Applications
  ```

## 🖥️ Frontend / Node.js (installés pendant le projet)
| Date       | Outil      | Commande install              | Commande désinstaller     |
|------------|------------|-------------------------------|---------------------------|
| 2026-08-02 | node       | `brew install node`           | `brew uninstall node`     |

Version : `v26.5.1` (npm `11.17.0`)

## 🧹 Nettoyage complet en fin de projet
```bash
brew uninstall node
# Supprimer Docker Desktop depuis Applications
# brew uninstall si on veut aussi retirer Homebrew
```


opencode a installe playwright base sur node si je ne me trompe pas.


Rtk Ai
  Usage:
    rtk init : initialisation
    rtk gain : une fois par semaine pour voir les gains

Caveman
  Usage:
    /caveman ultra : compression maximale
    /caveman off : pour récuperer les explications détaillées

Context7
  Config:
    /caveman ultra : compression maximale
  Usage:
    /caveman ultra : compression maximale

Graphify
  Usage:
    Exécutez /graphify . (ou faites un clic droit sur votre dossier de projet pour générer le graphe) avant de commencer une grosse session de refactorisation.



Prompt:
  "use context7 [votre requête complexe ici]. Analyse l'architecture globale avec Graphify pour ne rien casser. Réponds en mode /caveman pour aller droit au but."


  Graphify examples:
    "Si je supprime la fonction validateUser dans auth.ts, utilise /graphify pour lister tous les contrôleurs ou services qui vont casser."

    "Utilise /graphify pour me montrer le chemin complet du traitement d'une requête de l'API /orders depuis le routeur jusqu'à la base de données."


  Pour ajouter les commandes RTK spécifiques à FastAPI :
    "Met à jour la section RTK de mon fichier CLAUDE.md pour y ajouter les commandes optimisées pour FastAPI (comme rtk uvicorn main:app --reload ou rtk pytest)."

  Pour lier Context7 à la documentation officielle de FastAPI :
    "Ajoute une règle dans CLAUDE.md pour forcer l'utilisation de Context7 afin de vérifier la documentation officielle de FastAPI et Pydantic v2 avant de générer des routes d'API."
    
  Pour suivre l'architecture Python avec Graphify :
    "Met à jour mes règles pour que Graphify ignore le dossier .venv et __pycache__ lors de l'analyse d'architecture de mon projet FastAPI."


# Docker
```
docker system prune -a --volumes -f
```
Que fait exactement cette commande ?
- `docker system prune` : Nettoie l'ensemble du système Docker.
- `-a (ou --all)` : Supprime toutes les images inutilisées, pas seulement celles sans nom (dangling). Comme tous les conteneurs sont arrêtés, cela supprime toutes vos images.
- `--volumes` : Supprime tous les volumes anonymes pour ne laisser aucun résidu de données.
- `-f (ou --force)` : Force la suppression sans vous demander de confirmation de type (y/N).

```
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null; sudo docker system prune -a --volumes -f
```
Que fait exactement cette commande ?
- `sudo docker ps -aq` : Liste les identifiants de tous les conteneurs (actifs et arrêtés).
- `sudo docker rm -f` : Force l'arrêt et supprime immédiatement tous ces conteneurs.
- `&&` : Lance la suite uniquement si la première étape a réussi.
- `sudo docker system prune -a --volumes -f` : Nettoie tout le reste (images désormais isolées, volumes déconnectés, réseaux obsolètes).