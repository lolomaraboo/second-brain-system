# Multi-Repo Structure

Pattern pour organiser plusieurs repos git indépendants dans un même workspace.

## Problème

Avoir plusieurs projets liés mais avec leurs propres repos git, sans les imbriquer comme submodules.

## Solution

```
workspace/                    # Repo parent
├── project-a/               # .git propre → GitHub A
├── project-b/               # .git propre → GitHub B
├── project-c/               # .git propre → GitHub C
├── .gitignore               # Ignore project-a/, project-b/, project-c/
└── .git/                    # Repo parent (meta)
```

## Configuration

### .gitignore du parent
```gitignore
# Separate repositories
project-a/
project-b/
project-c/
```

### Initialiser un sous-projet
```bash
cd project-x
git init
git add .
git commit -m "Initial commit"
# Créer repo GitHub via API ou web
git remote add origin https://github.com/user/project-x.git
git push -u origin main
```

## Avantages

- Chaque projet a son propre historique git
- Pas de complexité submodule
- Facile à cloner individuellement
- Le workspace parent peut contenir des configs partagées

## Inconvénients

- Pas de lien automatique entre les repos
- Clone du parent ne clone pas les sous-projets
- Doit gérer plusieurs remotes

## Exemple réel

Voir [[windsurf-project]] pour une implémentation.

## Tags

#pattern #git #architecture
