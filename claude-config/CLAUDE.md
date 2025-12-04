- j'utilise le navigateur comet de perplexity pour ces fonctions d'agent

---
## ⚠️ CHECKLIST CRITIQUE - À APPLIQUER SYSTÉMATIQUEMENT ⚠️
---

**Avant d'utiliser TOUT outil (Read, Bash, Write, etc.), vérifie:**

1. ✅ **Chercher d'abord dans Second Brain:**
   - `mem0_search` pour trouver informations existantes
   - Lire Obsidian `_INDEX.md` pertinents
   - **SEULEMENT APRÈS:** utiliser filesystem (Bash, Read, etc.)

2. ✅ **Sauvegarder automatiquement:**
   - Après chaque commit important → `mem0_save`
   - Après décision technique → `mem0_save`
   - Après création config/script → `mem0_save`

3. ✅ **Toujours consulter la mémoire avant:**
   - Créer nouveau fichier (Write) → chercher patterns existants
   - Modifier fichier critique (Edit) → chercher bugs/décisions connus
   - Faire git commit → chercher conventions projet
   - Installer package → chercher conflits connus

**RÈGLE D'OR: Mémoire/Obsidian AVANT filesystem/bash**

**Ordre de priorité obligatoire:**
1. `mem0_search` → Chercher dans la mémoire
2. `Read` Obsidian _INDEX.md → Consulter documentation
3. **SEULEMENT APRÈS:** Bash/Read filesystem

---

## Second Brain (Mem0 + Obsidian)

Tu as accès à un "second brain" pour la mémoire persistante entre sessions.

### Architecture
- **Mem0** : Mémoire de travail automatique (contexte, décisions rapides, bugs)
- **Obsidian** : Wiki permanent dans `~/Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/vault/`

### Mem0 - Mémorisation automatique
Utilise `mem0_save` pour mémoriser automatiquement (sans demander) :
- Les décisions techniques importantes
- Les bugs résolus et leur cause racine
- Les changements d'architecture
- Les configurations spécifiques au projet
- Les problèmes récurrents et leurs solutions

### Obsidian - Wiki permanent (avec confirmation)
Structure du vault :
- `projects/[nom]/` : Notes par projet (architecture, decisions, roadmap)
- `wiki/patterns/` : Patterns réutilisables
- `wiki/tools/` : Documentation des outils
- `wiki/secrets/` : Documentation des secrets (JAMAIS les valeurs !)
- `wiki/troubleshooting/` : Solutions aux problèmes
- `ideas/` : Idées et brainstorming
- `daily/` : Notes quotidiennes

Règles Obsidian :
- Fichiers atomiques : 1 sujet = 1 fichier (max 50-100 lignes)
- Chaque dossier a un `_INDEX.md` que tu dois maintenir
- Toujours demander confirmation avant d'écrire
- Au `/start` : lire seulement les `_INDEX.md` pertinents

### Déclencheurs Obsidian
Propose de documenter dans Obsidian (avec confirmation) après :
- Debug non-trivial résolu (cause + solution)
- Nouvelle config/variable d'environnement
- Nouveau service/appareil/intégration
- Décision architecturale
- Workaround ou astuce découverte
- Script/commande utile créé
- Nouveau secret/clé API configuré
- Changement de sécurité (permissions, certificats)

### Gestion des secrets
- JAMAIS de valeur de secret dans Obsidian
- Obsidian = annuaire (nom de variable, où trouver, dashboard)
- .env par projet = valeurs réelles
- Tu peux copier entre projets si demandé

### Mémoire automatique (Mem0 + Obsidian)

#### 1. Sauvegarde automatique (mem0_save)

**Pendant la planification :**
- Décisions importantes discutées avec l'utilisateur

**Pendant l'exécution :**
- Après chaque commit important
- Après création de repo/fichier significatif
- Après configuration établie
- Après décision technique prise

**À la fin d'une tâche complexe :**
- Proposer de documenter dans Obsidian

**Règle : Ne pas attendre que l'utilisateur demande.**

#### 2. Consultation automatique (mem0_search)

⚠️ **RÈGLE CRITIQUE:** TOUJOURS consulter Mem0/Obsidian AVANT d'utiliser Bash/Read/Write pour explorer le système

**Si tu utilises Bash/Read pour chercher sans avoir consulté Mem0/Obsidian d'abord = VIOLATION DE LA RÈGLE**

**Avant ces outils :**
| Outil | Rechercher |
|-------|------------|
| Write (nouveau fichier) | Fichier existant ? Pattern similaire ? |
| Edit (fichier critique) | Bugs connus ? Décisions passées ? |
| Bash: git commit | Conventions du projet ? |
| Bash: npm/pip install | Conflits connus ? |
| mcp__github__create_* | Repo/PR similaire existe ? |

**Dans ces situations :**
| Situation | Rechercher |
|-----------|------------|
| Début de session | mem0_recall automatique |
| Nouveau projet | Ai-je travaillé dessus avant ? |
| Erreur/bug rencontré | Bug connu ? Solution ? |
| Choix d'architecture | Décisions passées ? |
| Création de config | Configs existantes ? |

**Quand l'utilisateur dit :**
| Mot-clé | Action |
|---------|--------|
| "comme avant", "comme d'habitude" | Chercher pattern précédent |
| "on avait fait...", "rappelle-toi" | mem0_search |
| "nouveau projet" | Vérifier si vraiment nouveau |
| "bug", "erreur", "problème" | Chercher bugs similaires |

### Détection de fin de session
Quand l'utilisateur dit "bye", "à plus", "je quitte", "on arrête là", "fin de session", "j'y vais" :
1. Propose de sauvegarder le contexte avant de partir
2. Fais un résumé de ce qui a été accompli
3. Utilise `mem0_save` pour mémoriser les points importants
4. Propose de mettre à jour Obsidian si nécessaire

### Sauvegarde avant épuisement du contexte
Quand le contexte devient long (beaucoup d'échanges, fichiers lus, tâches complexes) :
1. Préviens : "Le contexte devient long, je vais sauvegarder"
2. Utilise `mem0_save` pour mémoriser l'état actuel
3. Suggère de continuer dans une nouvelle session si nécessaire

### Identification du projet
Le project_id = nom du dossier du projet (ex: `recording-studio-manager`).

### Outils et commandes
**MCP Mem0 :**
- `mem0_recall` : Charger le contexte d'un projet
- `mem0_save` : Sauvegarder une information importante
- `mem0_search` : Rechercher dans la mémoire
- `mem0_health` : Vérifier que l'API fonctionne

**Slash commands :**
- `/start` : Charger le contexte complet (Mem0 + Obsidian)
- `/end` : Sauvegarder le contexte (Mem0 + Obsidian)
- `/wiki [note]` : Ajouter une note au wiki Obsidian
