# Second Brain - Guide d'utilisation

## Commandes slash

| Commande | Description |
|----------|-------------|
| `/start` | Charge le contexte (Mem0 + Obsidian _INDEX.md) |
| `/end` | Sauvegarde le contexte de fin de session |
| `/wiki [note]` | Ajoute une note au wiki Obsidian |

## Structure du vault

```
SecondBrain/
├── projects/           # Un dossier par projet
│   ├── _INDEX.md
│   └── [projet]/
│       ├── _INDEX.md   # Vue d'ensemble
│       └── decisions/  # ADRs
├── wiki/
│   ├── patterns/       # Patterns réutilisables
│   ├── tools/          # Documentation outils
│   ├── secrets/        # Annuaire des secrets (pas les valeurs!)
│   └── troubleshooting/# Solutions aux problèmes
├── ideas/              # Brainstorming
└── daily/              # Notes quotidiennes
```

## Règles

### Mem0 - Automatique
Sauvegarder sans demander :
- Décisions techniques importantes
- Bugs résolus et cause racine
- Changements d'architecture
- Configurations spécifiques

### Obsidian - Avec confirmation
Proposer de documenter après :
- Debug non-trivial résolu
- Nouvelle config/variable d'env
- Décision architecturale
- Workaround découvert
- Script utile créé

### Fichiers atomiques
- 1 sujet = 1 fichier
- Max 50-100 lignes
- Noms en kebab-case
- Toujours maintenir les `_INDEX.md`

## Secrets

**JAMAIS de valeurs dans Obsidian !**

Obsidian = annuaire (nom, où trouver, dashboard)
`.env` par projet = valeurs réelles
