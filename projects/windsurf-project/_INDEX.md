# Windsurf Project

Workspace parent contenant plusieurs projets indépendants.

## Structure

```
windsurf-project/
├── recording-studio-manager/   # SaaS studio
├── ClaudeCodeChampion/         # Framework Claude Code v4
├── SecondBrain/                # Wiki Obsidian
├── .gitignore                  # Ignore les sous-projets
└── .git/                       # Repo parent
```

## Repos GitHub

| Projet | Repo |
|--------|------|
| windsurf-project | [lolomaraboo/windsurf-project](https://github.com/lolomaraboo/windsurf-project) |
| recording-studio-manager | [lolomaraboo/recording-studio-manager](https://github.com/lolomaraboo/recording-studio-manager) |
| ClaudeCodeChampion | [lolomaraboo/claude-code-champion-v4](https://github.com/lolomaraboo/claude-code-champion-v4) |
| SecondBrain | [lolomaraboo/SecondBrain](https://github.com/lolomaraboo/SecondBrain) |

## Architecture

Chaque sous-projet a son propre `.git` et repo GitHub.
Le repo parent les ignore via `.gitignore`.

Voir [[multi-repo-structure]] pour le pattern.

## Décisions

- [[decisions/2025-12-01-multi-session-protection]] - Protection multi-sessions Claude Code (2025-12-01)
- [[decisions/2025-11-29-file-locking]] - File locking pour queue Mem0 multi-instances (2025-11-29)

## Liens

- Chemin: `~/Documents/APP_HOME/CascadeProjects/windsurf-project`
