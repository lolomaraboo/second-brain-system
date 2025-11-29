# Claude Code Tools

Liste complète des outils disponibles dans Claude Code.

## Outils natifs

| Outil | Description |
|-------|-------------|
| Task | Lancer des agents spécialisés (Explore, Plan, claude-code-guide) |
| Bash | Exécuter des commandes shell (timeout 2min, max 10min) |
| Glob | Recherche de fichiers par pattern (`**/*.ts`) |
| Grep | Recherche regex dans le contenu (basé sur ripgrep) |
| Read | Lire un fichier (2000 lignes max, supporte images/PDF/notebooks) |
| Edit | Modification de fichier par remplacement de texte |
| Write | Écrire/créer un fichier |
| NotebookEdit | Édition de cellules Jupyter (.ipynb) |
| WebFetch | Récupérer et analyser une URL |
| WebSearch | Recherche web avec résultats |
| TodoWrite | Gestion de liste de tâches |
| AskUserQuestion | Poser des questions avec options |
| EnterPlanMode | Entrer en mode planification |
| ExitPlanMode | Sortir du mode planification |
| BashOutput | Lire la sortie d'un shell en background |
| KillShell | Tuer un shell en background |
| Skill | Exécuter une skill |
| SlashCommand | Exécuter une commande slash |

## MCP Notion

Gestion complète de Notion :
- **Users** : `API-get-user`, `API-get-users`, `API-get-self`
- **Search** : `API-post-search`
- **Databases** : `API-post-database-query`, `API-create-a-database`, `API-update-a-database`, `API-retrieve-a-database`
- **Pages** : `API-retrieve-a-page`, `API-patch-page`, `API-post-page`
- **Blocks** : `API-get-block-children`, `API-patch-block-children`, `API-retrieve-a-block`, `API-update-a-block`, `API-delete-a-block`
- **Properties** : `API-retrieve-a-page-property`
- **Comments** : `API-retrieve-a-comment`, `API-create-a-comment`

## MCP Memory (Mem0)

### Mémoire projet
| Outil | Description |
|-------|-------------|
| `mem0_recall` | Charger le contexte d'un projet |
| `mem0_save` | Sauvegarder une information |
| `mem0_search` | Recherche sémantique dans la mémoire |
| `mem0_list_projects` | Lister tous les projets |
| `mem0_health` | Vérifier l'API |

### Knowledge Graph
| Outil | Description |
|-------|-------------|
| `create_entities` | Créer des entités |
| `create_relations` | Créer des relations entre entités |
| `add_observations` | Ajouter des observations à une entité |
| `delete_entities` | Supprimer des entités |
| `delete_observations` | Supprimer des observations |
| `delete_relations` | Supprimer des relations |
| `read_graph` | Lire tout le graphe |
| `search_nodes` | Rechercher des nœuds |
| `open_nodes` | Ouvrir des nœuds par nom |

## MCP Playwright (Browser)

Automatisation navigateur headless :

| Outil | Description |
|-------|-------------|
| `browser_navigate` | Naviguer vers une URL |
| `browser_click` | Cliquer sur un élément |
| `browser_type` | Taper du texte |
| `browser_snapshot` | Snapshot d'accessibilité (meilleur que screenshot) |
| `browser_take_screenshot` | Capture d'écran |
| `browser_fill_form` | Remplir un formulaire |
| `browser_select_option` | Sélectionner dans un dropdown |
| `browser_hover` | Survoler un élément |
| `browser_drag` | Drag and drop |
| `browser_press_key` | Appuyer sur une touche |
| `browser_evaluate` | Exécuter du JavaScript |
| `browser_wait_for` | Attendre du texte ou un délai |
| `browser_tabs` | Gérer les onglets |
| `browser_navigate_back` | Retour arrière |
| `browser_close` | Fermer la page |
| `browser_resize` | Redimensionner |
| `browser_file_upload` | Upload de fichiers |
| `browser_handle_dialog` | Gérer les dialogues |
| `browser_console_messages` | Messages console |
| `browser_network_requests` | Requêtes réseau |
| `browser_install` | Installer le navigateur |
| `browser_run_code` | Exécuter du code Playwright |

## MCP GitHub

| Outil | Description |
|-------|-------------|
| `create_repository` | Créer un repo |
| `search_repositories` | Rechercher des repos |
| `get_file_contents` | Lire un fichier |
| `create_or_update_file` | Créer/modifier un fichier |
| `push_files` | Push plusieurs fichiers |
| `create_branch` | Créer une branche |
| `list_commits` | Lister les commits |
| `create_issue` | Créer une issue |
| `list_issues` | Lister les issues |
| `get_issue` | Détails d'une issue |
| `update_issue` | Modifier une issue |
| `add_issue_comment` | Commenter une issue |
| `search_issues` | Rechercher issues/PRs |
| `create_pull_request` | Créer une PR |
| `list_pull_requests` | Lister les PRs |
| `get_pull_request` | Détails d'une PR |
| `get_pull_request_files` | Fichiers modifiés |
| `get_pull_request_status` | Statut des checks |
| `get_pull_request_comments` | Commentaires de review |
| `get_pull_request_reviews` | Reviews |
| `create_pull_request_review` | Créer une review |
| `merge_pull_request` | Merger une PR |
| `update_pull_request_branch` | Mettre à jour la branche |
| `fork_repository` | Forker un repo |
| `search_code` | Rechercher du code |
| `search_users` | Rechercher des utilisateurs |

## MCP Postgres

| Outil | Description |
|-------|-------------|
| `query` | Exécuter une requête SQL (read-only) |

## MCP Docker

| Outil | Description |
|-------|-------------|
| `mcp-find` | Trouver des serveurs MCP dans le catalogue |
| `mcp-add` | Ajouter un serveur MCP à la session |
| `mcp-remove` | Retirer un serveur MCP |
| `mcp-config-set` | Configurer un serveur MCP |
| `mcp-exec` | Exécuter un outil MCP |
| `code-mode` | Créer un outil JavaScript combinant plusieurs MCP |
| + tous les `browser_*` | (identiques à Playwright) |

## MCP IDE (VS Code)

| Outil | Description |
|-------|-------------|
| `getDiagnostics` | Obtenir les erreurs/warnings du language server |
| `executeCode` | Exécuter du code Python dans le kernel Jupyter |

## Liens

- [[second-brain]] : Système Mem0 + Obsidian
