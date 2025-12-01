# Second Brain - Guide d'utilisation

## Commandes slash

| Commande | Description | Vitesse | Use Case |
|----------|-------------|---------|----------|
| `/start` | Mode rapide (resume.md) par défaut | <100ms | Quick check-in |
| `/start --full` | Contexte complet (Mem0 + Obsidian) | 2-5s | Deep dive session |
| `/end` | Sauvegarde (Mem0 + Obsidian + resume) | 3-10s | Fin de session |
| `/wiki [note]` | Ajoute note au wiki | 1-2s | Documentation |

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

### Mem0 - Sauvegarde automatique
Sauvegarder sans demander :
- Décisions techniques importantes
- Bugs résolus et cause racine
- Changements d'architecture
- Configurations spécifiques
- Après chaque commit/création important

### Mem0 - Consultation automatique
Rechercher avant :
| Action | Rechercher |
|--------|------------|
| Write (nouveau fichier) | Existe déjà ? Pattern ? |
| Edit (fichier critique) | Bugs connus ? |
| git commit | Conventions ? |
| GitHub create | Existe déjà ? |

Rechercher quand :
| Situation | Action |
|-----------|--------|
| Début session | `mem0_recall` |
| Bug rencontré | Solutions connues ? |
| Choix architecture | Décisions passées ? |

Mots-clés déclencheurs :
- "comme avant" → chercher pattern
- "rappelle-toi" → `mem0_search`
- "bug", "erreur" → solutions connues

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

## Workflows Recommandés

### Quick Check-In (rapide)
1. `/start` - Mode rapide automatique (resume.md, <100ms)
2. Travailler sur le projet
3. `/end` - Sauvegarder + update resume

### Context Exhaustion Recovery
1. `/end` - Sauvegarder tout + générer resume + last-project.txt
2. `/clear` - Vider le contexte
3. `/start` - Reprendre automatiquement le dernier projet (mode rapide)

### Deep Dive (complet)
1. `/start --full` - Charger Mem0 + Obsidian (contexte complet)
2. Session longue avec décisions importantes
3. `/end` - Sauvegarder tout + update resume

### Context Switch entre projets
1. `/start` - Charge dernier projet automatiquement (mode rapide)
2. Ou `/start [projet-a]` - Charge projet spécifique
3. Travailler sur le projet
4. `/end` - Sauvegarde (met à jour last-project.txt)
5. `/start [projet-b]` - Switch vers autre projet

## Secrets

**JAMAIS de valeurs dans Obsidian !**

Obsidian = annuaire (nom, où trouver, dashboard)
`.env` par projet = valeurs réelles
