---
description: Charge le contexte Second Brain (mode rapide par défaut, --full pour complet)
---

Charge le contexte du projet avec deux modes intelligents.

**Usage:**
- `/start` - Mode rapide : lit resume.md si disponible, sinon Mem0+Obsidian
- `/start --full` - Mode complet : force Mem0 + Obsidian même si resume existe
- `/start [projet]` - Charge le projet spécifié (mode rapide)
- `/start [projet] --full` - Charge le projet spécifié (mode complet)

---

## Mode de détection

1. **Déterminer le projet :**
   - Si argument fourni (pas --full) : utiliser comme project_id
   - Sinon : lire `~/.claude/last-project.txt` pour le dernier projet
   - Fallback : utiliser `basename` du répertoire courant

2. **Choisir le mode :**
   - Si `--full` présent dans arguments : **Mode complet**
   - Sinon : **Mode rapide** (par défaut)

## Mode Rapide (par défaut)

**Étape 0 - Relire instructions (TOUJOURS en premier) :**
- Lire `~/.claude/CLAUDE.md` avec le Read tool
- Réviser section "Mémoire automatique" (lignes 54-68)

**Priorité 1** : Si `~/.claude/resumes/[project]/resume.md` existe :
- Lire le fichier resume.md
- Calculer l'âge (depuis "Last Updated")
- Si <7 jours : afficher le resume avec warning d'âge si >3 jours
- Si ≥7 jours : afficher warning "Resume obsolète, utilise /start --full"
- Rappel en bas : "💡 Pour le contexte complet : /start --full"

**Priorité 2** : Si resume.md n'existe pas :
- Passer automatiquement en Mode complet
- Informer : "Aucun resume trouvé, chargement du contexte complet..."

## Mode Complet (avec --full)

Force le chargement complet même si resume existe :

**0. CRITIQUE - Relire les instructions de mémorisation (TOUJOURS en premier) :**
   - Lire `~/.claude/CLAUDE.md` avec le Read tool
   - **Section obligatoire à réviser** : "Mémoire automatique (Mem0 + Obsidian)"
   - Lignes 54-68 : Règles de sauvegarde automatique (SANS attendre que l'utilisateur demande)
   - **Se rappeler** : mem0_save après chaque décision technique/config/commit important

1. **Enregistrer la session** : Utilise `~/scripts/obsidian_session_manager.py register [project_id] [cwd]`
2. **Vérifier les sessions actives** : Utilise `source ~/.claude/shell-config/obsidian-session-helpers.sh && obsidian_session_check [project_id]`
3. **Mem0** : Utilise mem0_recall pour charger le contexte de travail
4. **Obsidian** : Lis les _INDEX.md du projet dans SecondBrain/projects/[projet]/

Présente un résumé de :
- Ce qui a été fait précédemment (Mem0)
- L'architecture et les décisions documentées (Obsidian)
- Les prochaines étapes suggérées
- **Warning si autre session active sur même projet**

## Avantages

- **Performance** : Mode rapide <100ms vs mode complet 2-5s
- **Intelligent** : Détecte automatiquement le meilleur mode
- **Flexible** : Force le mode complet quand nécessaire
- **Backward compatible** : Si pas de resume, comportement normal
