# File Locking avec fcntl

Pattern pour empêcher les race conditions lors d'accès concurrents à un fichier.

## Problème

Deux processus qui lisent, modifient et écrivent le même fichier peuvent créer une race condition :

```
Process A          Fichier          Process B
────────           ──────           ────────
Read: {count: 5}                    Read: {count: 5}
count += 1                          count += 1
Write: {count: 6}                   Write: {count: 6}  ❌ Perte de l'update A
```

## Solution : fcntl avec timeout

```python
import fcntl
import time
from pathlib import Path

LOCK_FILE = Path("/path/to/file.lock")
LOCK_TIMEOUT = 5  # secondes

def acquire_lock_with_timeout(lock_file, timeout=LOCK_TIMEOUT):
    """Acquire file lock with timeout to prevent blocking indefinitely"""
    start = time.time()

    while time.time() - start < timeout:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True  # Lock acquired
        except BlockingIOError:
            time.sleep(0.1)  # Wait 100ms and retry

    return False  # Timeout

def safe_operation():
    """Perform file operation with lock protection"""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOCK_FILE, 'w') as lock:
        if not acquire_lock_with_timeout(lock):
            raise Exception("Could not acquire lock (timeout)")

        # Critical section - protected by lock
        data = read_file()
        data = modify_data(data)
        write_file(data)

        # Lock automatically released when exiting 'with' block
```

## Avec le pattern

```
Process A          Lock File        Process B
────────           ─────────        ────────
Acquire lock       🔒 A             Try acquire lock
Read: {count: 5}                    ⏳ Wait...
count += 1                          ⏳ Wait...
Write: {count: 6}                   ⏳ Wait...
Release lock       🔓               🔒 B
                                    Read: {count: 6}
                                    count += 1
                                    Write: {count: 7}  ✅ Correct
```

## Flags fcntl

- `LOCK_EX` : Lock exclusif (write lock)
- `LOCK_SH` : Lock partagé (read lock)
- `LOCK_NB` : Non-blocking (retourne erreur au lieu d'attendre)
- `LOCK_UN` : Unlock (automatique avec `with`)

## Timeout

**Pourquoi ?** Sans timeout, un processus peut bloquer indéfiniment si :
- L'autre processus crashe avec le lock
- Deadlock circulaire
- Opération anormalement longue

**Stratégie :**
- Timeout court (5s) pour opérations normales
- Retry avec backoff exponentiel si nécessaire
- Log les timeouts pour debugging

## Cas d'usage

✅ **Bon pour :**
- Fichiers de configuration partagés
- Queues locales (JSON, etc.)
- Cache partagé entre processus
- Compteurs/statistiques

❌ **Pas pour :**
- Haute concurrence (utiliser DB)
- Synchronisation réseau (utiliser lock distribué)
- Fichiers très gros (lock tout le fichier)

## Voir aussi

- [[sync-with-backup]] - Combine file locking avec backup
- [[multi-instance-claude]] - Usage avec Claude Code
- Projet : [[windsurf-project/decisions/2025-11-29-file-locking]]
