# XO Cortex

Application Second Brain multi-plateforme.

## Infos
- **Domaine** : xo-cortex.com (acheté)
- **Date idée** : 2025-11-28
- **Statut** : Brainstorming

## Vision

Un "second cerveau" personnel accessible partout : mobile, web, desktop, navigateur.
Inspiré de l'expérience Second Brain (Mem0 + Obsidian) utilisée avec Claude Code.

## Plateformes cibles

| Plateforme | Priorité | Notes |
|------------|----------|-------|
| Web | P1 | Application principale |
| Mobile | P1 | iOS + Android |
| Desktop | P2 | Mac, Windows, Linux |
| Extension navigateur | P2 | Capture rapide depuis le web |

## Fonctionnalités potentielles

### Core (MVP)
- [ ] Capture rapide (notes, liens, idées)
- [ ] Organisation (dossiers, tags)
- [ ] Recherche full-text
- [ ] Sync temps réel cross-platform
- [ ] Markdown support

### Avancé (V2)
- [ ] Liens bidirectionnels (wikilinks)
- [ ] Graph view (visualisation des connexions)
- [ ] Recherche sémantique (IA)
- [ ] Templates de notes
- [ ] Import/Export (Obsidian, Notion, Roam)

### IA (V3)
- [ ] Résumé automatique
- [ ] Suggestions de liens
- [ ] Q&A sur ses propres notes
- [ ] Génération de contenu assistée

## Stack technique - Options

### Option A : React Everywhere
```
Mobile     : React Native / Expo
Web        : Next.js
Desktop    : Electron
Extension  : React + WebExtension API
Backend    : Node.js + PostgreSQL
```
**Avantage** : Une seule compétence (React/TS)

### Option B : Flutter Everywhere
```
Mobile     : Flutter
Web        : Flutter Web
Desktop    : Flutter Desktop
Extension  : Dart2JS ou séparé
Backend    : Dart (Serverpod) ou Node.js
```
**Avantage** : Vraiment cross-platform, UI native

### Option C : Hybride pragmatique
```
Mobile     : Expo (React Native)
Web        : Next.js
Desktop    : Tauri (Rust + WebView)
Extension  : Vanilla JS/TS
Backend    : Supabase (PostgreSQL + Auth + Realtime)
```
**Avantage** : Best of breed, Tauri léger

## Backend & Data

### Options BaaS
- **Supabase** : PostgreSQL, Auth, Realtime, Storage (open source)
- **Firebase** : NoSQL, facile mais vendor lock-in
- **Appwrite** : Alternative open source

### Self-hosted
- PostgreSQL + API custom (Node/Python/Go)
- SQLite local + sync (comme Obsidian)

## Questions ouvertes

1. **Modèle** : Personnel only ou SaaS multi-users ?
2. **Sync** : Cloud-first ou local-first avec sync ?
3. **Pricing** : Freemium ? Quel tier gratuit ?
4. **Open source** : Core open source + cloud payant ?
5. **Différenciation** : Qu'est-ce qui distingue XO Cortex de Notion/Obsidian/Roam ?
6. **Priorité plateforme** : Commencer par web ou mobile ?

## Concurrence

| App | Forces | Faiblesses |
|-----|--------|------------|
| Obsidian | Local-first, plugins, gratuit | Sync payant, pas vraiment mobile |
| Notion | Complet, collab | Lent, cloud-only, complexe |
| Roam | Graph, bidirectionnel | Cher, niche |
| Logseq | Open source, outliner | UX brute |
| Apple Notes | Simple, intégré | Apple only, basique |

## Prochaines étapes

1. Répondre aux questions ouvertes
2. Définir le MVP (fonctionnalités minimum)
3. Choisir la stack technique
4. Maquettes UI/UX
5. Setup projet + repo

## Ressources

- Domaine : xo-cortex.com
