# Diagnostic Login Client - Multi-Tenant

**Date:** 2025-12-03  
**Status:** 🔧 En cours (SSL wildcard manquant)  
**Serveur:** 31.220.104.244

## Problème Initial

Erreur lors de la connexion client sur recording-studio-manager.com :
- Erreur 500 Internal Server Error
- Log: `sqlite3.OperationalError: no such table: clients`

## Cause Racine

### Architecture Database-per-Tenant

L'application utilise une architecture **Database-per-Tenant** :

1. **Master DB** (`recording_studio_prod`) : Métadonnées organisations
   - Tables: `organizations`, `plans`, `subscriptions`, `ai_credits_*`
   - Contient: Organization "maraboo" → DB `studio_5_db`

2. **Tenant DBs** (ex: `studio_5_db`) : Données métier par client
   - Tables: `clients`, `sessions`, `invoices`, `equipment`, etc.
   - Une DB PostgreSQL par organisation

### Middleware Tenant Resolution

**Fichier:** `/app/web/app.py` (lignes 77-150)

```python
@app.before_request
def resolve_tenant():
    # Détecte subdomain depuis request.host
    if host.endswith(f'.{platform_domain}'):
        subdomain = host.replace(f'.{platform_domain}', '')
        # Query organization par subdomain
        org = session.query(Organization).filter_by(subdomain=subdomain).first()
        if org:
            g.tenant_db = _tenant_db_connections[org.id]
    else:
        g.tenant = None
        g.tenant_db = None  # ← Fallback SQLite!
```

### Fonction get_active_session()

**Fichier:** `/app/web/app.py` (ligne 130)

```python
def get_active_session():
    tenant_db = getattr(g, 'tenant_db', None)
    if tenant_db:
        # PostgreSQL tenant
        session = tenant_db()
        yield session
    else:
        # Fallback SQLite (DEV mode)
        with db.get_session() as session:
            yield session
```

## Solution

### ✅ Ce qui fonctionne

- DNS wildcard: `*.recording-studio-manager.com` → `31.220.104.244`
- Base tenant `studio_5_db` existe avec table `clients`
- SAAS_MODE=true activé dans Docker
- Nginx configuré avec wildcard `*.recording-studio-manager.com`

### ❌ Problème restant

**Certificat SSL manquant pour wildcard**

- Certificat actuel: `recording-studio-manager.com` + `www` seulement
- Wildcard `*.recording-studio-manager.com` non couvert
- Flask force HTTPS (`SESSION_COOKIE_SECURE=True`)
- Accès HTTP impossible (redirection automatique)

## Infrastructure

### Docker Containers

```bash
studio_app        → Gunicorn :5002 (2 workers)
studio_postgres   → PostgreSQL :5432
studio_redis      → Redis :6379/3
studio_nginx      → Nginx (inactif, Nginx host utilisé)
```

### Nginx

- **Config:** `/etc/nginx/sites-available/recording-studio-manager`
- **Processus:** 2 masters (PID 1547789 + 3505397)
- **Rechargement:** `kill -HUP 1547789`
- **Logs:** `/var/log/nginx/recording-studio-manager-*.log`

### PostgreSQL

**Master DB:** `recording_studio_prod`
- Host: `postgres` (container) / `localhost:5433` (host)
- User: `studio_user`

**Tenant DB:** `studio_5_db`  
- Organization: `maraboo` (TRIAL)
- Tables: 50+ tables incluant `clients`

## Solutions Possibles

### Option 1: Certificat Wildcard (Recommandé)

```bash
# Nécessite validation DNS (pas HTTP)
certbot certonly --manual --preferred-challenges dns \
  -d recording-studio-manager.com \
  -d *.recording-studio-manager.com
```

**Problème:** Validation DNS manuelle requise

### Option 2: Certificats Individuels

```bash
# Par subdomain
certbot certonly --nginx \
  -d maraboo.recording-studio-manager.com
```

**Problème:** Certbot échoue (multiples Nginx instances)

### Option 3: HTTP Temporaire (Quick Fix)

Modifier `.env` Docker:
```bash
SESSION_COOKIE_SECURE=False
# Redémarrer container
docker restart studio_app
```

**Accès:** `http://maraboo.recording-studio-manager.com`

## Accès Correct

### ❌ Incorrect
```
https://recording-studio-manager.com/client/login
→ Pas de tenant détecté → SQLite → Erreur
```

### ✅ Correct
```
https://maraboo.recording-studio-manager.com/client/login
→ Tenant "maraboo" → PostgreSQL studio_5_db → OK
```

## Commandes Utiles

```bash
# Vérifier organization
docker exec studio_postgres psql -U studio_user -d recording_studio_prod \
  -c "SELECT subdomain, database_name, status FROM organizations;"

# Vérifier tables tenant
docker exec studio_postgres psql -U studio_user -d studio_5_db -c '\dt'

# Logs application
docker logs studio_app --tail 50

# Recharger Nginx
ssh root@31.220.104.244 "kill -HUP 1547789"

# Test subdomain
curl -I http://maraboo.recording-studio-manager.com
```

## Prochaines Étapes

1. [ ] Générer certificat SSL wildcard (validation DNS)
2. [ ] Mettre à jour Nginx config avec nouveau certificat
3. [ ] Tester login via `https://maraboo.recording-studio-manager.com`
4. [ ] Documenter procédure ajout nouveau tenant

## Voir Aussi

- [[2025-12-03-site-fix]] - Fix initial Nginx + SSL domaine principal
- [[multi-tenant-provisioning]] - Architecture provisionnement tenant
- [[multi-tenant-routing]] - Middleware routing multi-tenant
