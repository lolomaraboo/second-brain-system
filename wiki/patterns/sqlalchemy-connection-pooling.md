# SQLAlchemy Connection Pooling (Multi-Tenant)

**Date:** 2025-11-30
**Context:** Multi-tenant SaaS avec database-per-tenant
**Projet:** Recording Studio Manager

## Problème

Dans une architecture multi-tenant avec N organisations, chaque requête HTTP doit se connecter à une base de données différente selon le tenant résolu.

**Défis :**
1. Créer une connexion par requête est trop lent (~50ms)
2. Connexions permanentes consomment ressources PostgreSQL
3. Besoin de cache intelligent par tenant
4. Gérer fermeture propre après requête

## Solution

**Connection pooling par tenant** avec cache en mémoire et `scoped_session` SQLAlchemy.

### Architecture

```
HTTP Request → Middleware
    ↓
Tenant résolu (org_id=123)
    ↓
Cache lookup: self.db_connections[123] ?
    ├── HIT → Retourne pool existant (~1ms)
    └── MISS → Créer pool + cache (~50ms)
```

## Implémentation

### 1. Cache en Mémoire

```python
class TenantMiddleware:
    def __init__(self):
        # Dict[org_id, scoped_session]
        self.db_connections: Dict[int, scoped_session] = {}
```

### 2. Création Pool SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def get_tenant_connection(self, tenant: Organization) -> scoped_session:
    # Cache hit
    if tenant.id in self.db_connections:
        return self.db_connections[tenant.id]

    # Cache miss: créer nouveau pool
    db_password = decrypt_db_password(tenant.database_password_hash)

    db_url = (
        f"postgresql://{tenant.database_user}:{db_password}"
        f"@{tenant.database_host}:{tenant.database_port}"
        f"/{tenant.database_name}"
    )

    engine = create_engine(
        db_url,
        pool_size=5,              # 5 connexions permanentes
        max_overflow=10,          # +10 temporaires max (= 15 total)
        pool_pre_ping=True,       # Vérifie connexion avant usage
        pool_recycle=3600,        # Recycle après 1h (évite stale connections)
        pool_timeout=30,          # 30s timeout acquisition connexion
        echo=False,               # Pas de log SQL (sauf debug)
    )

    Session = scoped_session(sessionmaker(bind=engine))

    # Cache pour prochaines requêtes
    self.db_connections[tenant.id] = Session

    return Session
```

### 3. Configuration Pool

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| `pool_size` | 5 | Connexions permanentes ouvertes |
| `max_overflow` | 10 | Connexions temporaires max (pic de trafic) |
| `pool_pre_ping` | True | Teste connexion avant usage (détecte déconnexions) |
| `pool_recycle` | 3600 | Recycle connexion après 1h (évite timeouts PostgreSQL) |
| `pool_timeout` | 30 | Erreur si pas de connexion dispo après 30s |

**Total max connexions par tenant** : 5 + 10 = **15 connexions**

### 4. Utilisation Flask g Context

```python
# Middleware WSGI
def __call__(self, environ, start_response):
    tenant = self.resolve_tenant(host)

    # Injection dans Flask g
    g.tenant = tenant
    g.tenant_db = self.get_tenant_connection(tenant)

    # Requête traitée
    return self.app(environ, start_response)
```

```python
# Route Flask
from utils.tenant_middleware import get_tenant_db

@app.route('/api/rooms')
@require_tenant
def list_rooms():
    session = get_tenant_db()  # scoped_session du tenant

    rooms = session.query(Room).filter_by(deleted_at=None).all()
    return jsonify([r.to_dict() for r in rooms])
```

### 5. Cleanup Après Requête

```python
@app.teardown_appcontext
def shutdown_tenant_connections(error=None):
    """Appelé automatiquement après chaque requête"""
    if hasattr(g, 'tenant_db') and g.tenant_db:
        g.tenant_db.remove()  # Retourne connexion au pool

    if hasattr(g, 'master_db') and g.master_db:
        g.master_db.close()   # Ferme session master
```

**Important** : `remove()` ne ferme PAS la connexion, elle la **retourne au pool** pour réutilisation.

### 6. Shutdown Application

```python
def close_all_connections(self):
    """Appelé au shutdown serveur (SIGTERM)"""
    for tenant_id, session in self.db_connections.items():
        session.remove()  # Retourne connexions au pool
        session.get_bind().dispose()  # Ferme engine et pool

    self.db_connections.clear()
```

## Performance

### Benchmarks (1 tenant actif)

| Opération | 1ère requête | Requêtes suivantes |
|-----------|--------------|---------------------|
| Création pool | ~50ms | - |
| Lookup cache | - | ~0.5ms |
| Acquisition connexion | ~2ms | ~1ms (depuis pool) |
| **Total overhead** | **~52ms** | **~1.5ms** |

### Scalabilité Multi-Tenants

| Tenants actifs | Connexions PostgreSQL totales | RAM estimée |
|----------------|-------------------------------|-------------|
| 10 | 50 (10×5 pool_size) | ~100 MB |
| 50 | 250 | ~500 MB |
| 100 | 500 | ~1 GB |
| 1000 | 5000 | ~10 GB |

**Mitigation pour 1000+ tenants** :
- Pool LRU eviction (fermer pools inactifs)
- Pool size réduit (2-3 au lieu de 5)
- Serveurs dédiés pour tenants premium

## Gestion Concurrence

### scoped_session Thread-Safety

```python
Session = scoped_session(sessionmaker(bind=engine))

# Thread 1
session1 = Session()  # Connexion A
session1.query(Room).all()

# Thread 2 (même temps)
session2 = Session()  # Connexion B (différente !)
session2.query(User).all()

# Auto cleanup par thread
Session.remove()
```

`scoped_session` garantit :
- 1 session SQLAlchemy par thread
- Isolation des transactions
- Cleanup automatique via `remove()`

### Pool Exhaustion

```python
# Scenario: 20 requêtes simultanées, pool_size=5, max_overflow=10

# Requêtes 1-5 → Pool connexions permanentes
# Requêtes 6-15 → Overflow connexions temporaires
# Requêtes 16-20 → ATTENTE (pool_timeout=30s)

# Si timeout dépassé
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
```

**Solution** : Augmenter `max_overflow` ou optimiser durée requêtes.

## Monitoring

```python
def get_pool_status(tenant_id: int) -> dict:
    """Debug info pour un tenant pool"""
    session = self.db_connections.get(tenant_id)
    if not session:
        return {"error": "Pool not initialized"}

    engine = session.get_bind()
    pool = engine.pool

    return {
        "size": pool.size(),          # Connexions permanentes
        "checked_in": pool.checkedin(), # Connexions disponibles
        "checked_out": pool.checkedout(), # Connexions en usage
        "overflow": pool.overflow(),   # Connexions overflow actuelles
        "max_overflow": pool._max_overflow,
    }
```

Exemple output :
```json
{
  "size": 5,
  "checked_in": 3,
  "checked_out": 2,
  "overflow": 0,
  "max_overflow": 10
}
```

## pool_pre_ping Explication

```python
pool_pre_ping=True
```

**Avant chaque query** :
```sql
-- SQLAlchemy exécute automatiquement
SELECT 1;

-- Si succès → Utilise connexion
-- Si échec → Invalidate connexion, en crée nouvelle
```

**Utile pour** :
- Connexions expirées (PostgreSQL `idle_in_transaction_session_timeout`)
- Network glitches
- Database restarts

**Coût** : +1ms par query, mais évite erreurs `connection lost`.

## pool_recycle Explication

```python
pool_recycle=3600  # 1 heure
```

**Comportement** :
- Connexion > 1h d'existence → Fermée et recréée
- Évite timeouts PostgreSQL (`tcp_keepalives_idle`)

**PostgreSQL default** :
```sql
-- postgresql.conf
idle_in_transaction_session_timeout = 0  # Pas de limite (dangereux)
statement_timeout = 0
```

Recommandation :
- `pool_recycle` < `idle_in_transaction_session_timeout`
- Ex : `pool_recycle=3600`, PostgreSQL timeout=7200

## Anti-Patterns

### ❌ Créer engine par requête

```python
# LENT : 50ms par requête
def get_rooms():
    engine = create_engine(db_url)
    session = Session(bind=engine)
    rooms = session.query(Room).all()
    engine.dispose()
    return rooms
```

### ❌ Pool global shared

```python
# DANGEREUX : Connexion tenant A utilisée pour tenant B
global_engine = create_engine(master_db_url)

def get_rooms(tenant_id):
    # Tous les tenants partagent same pool → FUITE DONNÉES
    session = Session(bind=global_engine)
    ...
```

### ✅ Pool par tenant (pattern actuel)

```python
# BON : Cache dict[tenant_id, scoped_session]
self.db_connections[tenant.id] = scoped_session(...)
```

## Références

- **Projet** : Recording Studio Manager `tenant_middleware.py:89-119`
- **SQLAlchemy Docs** : [Engine Configuration](https://docs.sqlalchemy.org/en/14/core/engines.html)
- **Pattern** : [[multi-tenant-routing]]
- **Encryption** : [[database-password-encryption]]
- **Session** : SESSION 4 (2025-11-30)
