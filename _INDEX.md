# Second Brain

Système de mémoire persistante combinant Mem0 (mémoire de travail) et Obsidian (wiki permanent).

## Structure

- [[projects/_INDEX|projects]] : Projets documentés (dev, perso, studio)
- [[wiki/_INDEX|wiki]] : Documentation transversale et réutilisable
- [[daily/_INDEX|daily]] : Notes quotidiennes
- [[ideas/_INDEX|ideas]] : Idées et brainstorming

## Architecture

- **Mem0** : Mémoire de travail automatique (contexte, décisions rapides, bugs)
- **Obsidian** : Wiki permanent pour documentation structurée

## Utilisation

- `/start` : Charger le contexte (mode rapide avec resume, ou --full pour complet)
- `/end` : Sauvegarder le contexte (Mem0 + Obsidian + resume)
- `/wiki [note]` : Ajouter une note au wiki
