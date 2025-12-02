# Multi-Tenant Routing (WSGI Middleware)

**Date:** 2025-11-30
**Fichier source:** `utils/tenant_middleware.py` (543 lignes)

## Concept

Middleware WSGI Flask qui intercepte **toutes les requêtes HTTP** pour résoudre le tenant et configurer dynamiquement la connexion à sa base de données.

## Architecture

```
HTTP Request
    ↓
TenantMiddleware (WSGI)
    ↓
1. Extrait host (HTTP_HOST)
2. Résout tenant (subdomain ou custom domain)
3. Vérifie statuts (SUSPENDED, DELETED, expired)
4. Configure Flask g.tenant, g.tenant_db, g.master_db
    ↓
Flask App (routes avec accès tenant)
```

## Résolution Tenant

### 2 Stratégies

#### 1. Subdomain (Automatique)

```
Request: studio-paris.studioplatform.com
         ↓
Extraction: subdomain = "studio-paris"
         ↓
Query: Organization.filter_by(subdomain="studio-paris")
```

#### 2. Custom Domain

```
Request: studio-pro.com
         ↓
Query: Domain.filter_by(domain="studio-pro.com", is_active=True)
         ↓
Result: domain.organization
```

### Code

```python
def resolve_tenant(self, host: str) -> Optional[Organization]:
    # Cas 1: Subdomain
    if host.endswith(f".{self.platform_domain}"):
        subdomain = host.replace(f".{self.platform_domain}", "")
        return Organization.filter_by(subdomain=subdomain).first()

    # Cas 2: Custom domain
    domain = Domain.filter_by(domain=host, is_active=True).first()
    if domain:
        return domain.organization

    return None
```

## Vérifications Statuts

### Organisation

| Statut | Code HTTP | Action |
|--------|-----------|--------|
| `SUSPENDED` | 403 Forbidden | Affiche raison suspension (payment overdue) |
| `DELETED` | 410 Gone | Compte supprimé définitivement |
| `ACTIVE` | 200 OK | Continue |

### Subscription

```python
if not tenant.subscription.is_active:
    return 402 Payment Required  # Abonnement expiré
```

## Connection Pooling par Tenant

### Cache en Mémoire

```python
class TenantMiddleware:
    def __init__(self):
        self.db_connections: Dict[int, scoped_session] = {}
```

### Pool SQLAlchemy

```python
def get_tenant_connection(self, tenant: Organization) -> scoped_session:
    # Cache hit
    if tenant.id in self.db_connections:
        return self.db_connections[tenant.id]

    # Cache miss: créer pool
    encrypted_password = tenant.database_password_hash
    db_password = self.fernet.decrypt(encrypted_password.encode()).decode()

    db_url = f"postgresql://{tenant.database_user}:{db_password}@{tenant.database_host}:{tenant.database_port}/{tenant.database_name}"

    engine = create_engine(
        db_url,
        pool_size=5,              # 5 connexions permanentes
        max_overflow=10,          # +10 temporaires max (= 15 total)
        pool_pre_ping=True,       # Vérifie connexion avant usage
        pool_recycle=3600,        # Recycle après 1h
    )

    Session = scoped_session(sessionmaker(bind=engine))
    self.db_connections[tenant.id] = Session

    return Session
```

### Performance

- **1ère requête** : Création pool (~50ms)
- **Requêtes suivantes** : Réutilisation pool (~1ms)
- **Max 15 connexions** par tenant (5 permanentes + 10 overflow)

## Flask g Context

### Variables Injectées

```python
# Dans middleware
g.tenant = tenant                          # Organization object
g.tenant_db = self.get_tenant_connection() # scoped_session tenant DB
g.master_db = self.master_db_session()     # session master DB

# Dans routes Flask
from utils.tenant_middleware import get_current_tenant, get_tenant_db

@app.route('/api/rooms')
@require_tenant
def list_rooms():
    tenant = get_current_tenant()
    session = get_tenant_db()

    rooms = session.query(Room).filter_by(deleted_at=None).all()
    return jsonify([r.to_dict() for r in rooms])
```

## Routes Publiques (Sans Tenant)

```python
def _is_public_route(self, path: str) -> bool:
    public_prefixes = [
        "/signup",       # Inscription nouveau studio
        "/static/",      # Assets CSS/JS/images
        "/health",       # Healthcheck K8s
        "/favicon.ico",  # Icon navigateur
        "/platform",     # Admin super-user
    ]
    return any(path.startswith(prefix) for prefix in public_prefixes)
```

## Decorators

### @require_tenant

```python
@app.route('/api/rooms')
@require_tenant
def list_rooms():
    # Tenant garanti non-None ici
    tenant = get_current_tenant()
    ...
```

### @require_active_subscription

```python
@app.route('/api/rooms')
@require_active_subscription
def create_room():
    # Subscription active garantie
    tenant = get_current_tenant()
    ...
```

Retourne 402 Payment Required si abonnement expiré.

## Réponses Erreur HTML

### 404 Not Found (Tenant Inexistant)

```html
<h1>Studio Not Found</h1>
<p>No studio found for domain: <strong>studio-xyz.com</strong></p>
<a href="/signup">Create a new studio</a>
```

### 403 Forbidden (Suspendu)

```html
<h1>Account Suspended</h1>
<p>Reason: Payment overdue</p>
<p>Contact support: support@studioplatform.com</p>
```

### 410 Gone (Supprimé)

```html
<h1>Account Deleted</h1>
<p>This studio has been permanently deleted.</p>
```

### 402 Payment Required (Abonnement Expiré)

```html
<h1>Subscription Expired</h1>
<p><a href="/billing/renew">Renew your subscription</a></p>
```

## Teardown & Cleanup

### Après Chaque Requête

```python
@app.teardown_appcontext
def shutdown_tenant_connections(error=None):
    if hasattr(g, 'tenant_db') and g.tenant_db:
        g.tenant_db.remove()  # Retourne connexion au pool

    if hasattr(g, 'master_db') and g.master_db:
        g.master_db.close()   # Ferme session master
```

### Shutdown Application

```python
def close_all_connections(self):
    for tenant_id, session in self.db_connections.items():
        session.remove()  # Ferme pool SQLAlchemy

    self.db_connections.clear()
```

## Tracking Activité

```python
def _log_tenant_activity(self, tenant: Organization):
    tenant.last_activity_at = datetime.now()
    session.commit()
```

Utilisé pour analytics et détection comptes inactifs.

## Setup

```python
from utils.tenant_middleware import init_tenant_middleware

# Dans web/app.py
def create_app():
    app = Flask(__name__)

    # ... config ...

    # Activer middleware tenant
    init_tenant_middleware(app, master_db_session)

    return app
```

## Références

- Code : `utils/tenant_middleware.py`
- Provisioning : [[multi-tenant-provisioning]]
- Pattern : [[sqlalchemy-connection-pooling]]
- Session : SESSION 4 (2025-11-30)
