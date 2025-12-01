# Streaming Documentation Pattern

Pattern pour documenter efficacement de gros fichiers de code.

## Problème

Documenter un gros fichier (2000+ lignes) :
- ❌ Tout lire puis mémoriser → risque d'oublier, crash, contexte perdu
- ❌ Lire par morceaux sans mémoriser → pas de traçabilité
- ❌ Mémoriser trop tard → perte d'info si session crashe

## Solution : Streaming

**Lire + Mémoriser au fur et à mesure**

```
Pour chaque section du fichier (200-400 lignes) :
  1. Lire la section
  2. Mémoriser immédiatement (Mem0)
  3. Passer à la section suivante
```

## Avantages

✅ **Progression visible** : Compteur de mémoires créées
✅ **Récupération facile** : Si crash, reprendre où on s'est arrêté
✅ **Meilleure mémoire** : Traitement par petits chunks
✅ **Queue locale** : Mémoires sauvegardées même si VPS inaccessible

## Exemple réel

**Recording Studio Manager - models.py (2512 lignes)**
- 📖 Lu en sections de ~300 lignes
- 💾 55+ mémoires créées au fur et à mesure
- ✅ 100% complété sans perte
- ⏱️ VPS temporairement down → queue locale a tout géré

## Quand l'utiliser

- Fichiers > 1000 lignes
- Documentation exhaustive requise
- Besoin de traçabilité complète
- Projet critique

## Code snippet

```python
# Pseudo-code
sections = split_file_in_chunks(file, chunk_size=300)
for i, section in enumerate(sections):
    content = read_section(section)
    analyze(content)
    mem0_save(f"Section {i+1}/{len(sections)}: {summary}")
    update_progress_file()
```

## Anti-patterns

❌ Tout lire d'un coup
❌ Mémoriser à la fin
❌ Trop gros chunks (>500 lignes)
❌ Trop petits chunks (<100 lignes, overhead)

## Liens

- [[recording-studio-manager]] - Projet où appliqué
- [[mem0]] - Système de mémoire utilisé
