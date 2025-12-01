# Multi-Tenant Provisioning (Database-per-Tenant)

**Date:** 2025-11-30
**Fichier source:** `utils/tenant_provisioner.py` (702 lignes)

## Concept

Architecture **database-per-tenant** : Chaque organisation a sa propre base de données PostgreSQL dédiée pour isolation maximale des données.

## Architecture

```
Master DB (platform)
├── organizations (metadata)
├── subscriptions
├── plans
└── domains

Tenant DBs (isolated)
├── studio_1_db → Organisation #1
├── studio_2_db → Organisation #2
└── studio_N_db → Organisation #N
```

## Flow Provisioning Complet

### 7 Étapes Automatiques

```python
TenantProvisioner.provision_tenant(org_id, slug, owner_email, owner_password)
```

1. **Génération credentials sécurisés**
   - `db_name = f"studio_{org_id}_db"`
   - `db_user = f"studio_{org_id}_user"`
   - `db_password = secrets.choice(32 chars)`

2. **CREATE DATABASE PostgreSQL**
   - Connexion superuser (`POSTGRES_SUPERUSER`)
   - `CREATE DATABASE studio_X_db`
   - Vérification existence avant création

3. **CREATE USER PostgreSQL**
   - `CREATE USER studio_X_user WITH ENCRYPTED PASSWORD`
   - `GRANT ALL PRIVILEGES ON DATABASE`
   - Protection SQL injection via `sql.Identifier()`

4. **Permissions PostgreSQL 15+**
   - `GRANT ALL ON SCHEMA public TO user`
   - `ALTER DEFAULT PRIVILEGES ... GRANT ALL ON TABLES`
   - Requis pour permissions complètes

5. **Migrations (35 tables)**
   - Engine SQLAlchemy vers tenant DB
   - `Base.metadata.create_all(engine)`
   - Crée toutes tables depuis `models.py`

6. **Seed data initial**
   - `StudioConfig` avec defaults :
     - timezone = "Europe/Paris"
     - currency = "EUR"
     - default_tax_rate = 20.0 (TVA FR)
     - invoice_prefix = "INV"

7. **Utilisateur admin initial**
   - `User` avec role = "Administrateur"
   - `admin.set_password()` hash bcrypt
   - Premier compte pour studio owner

8. **Update Organization credentials**
   - `database_password_hash = encrypt_db_password()`
   - Stockage chiffré dans master DB
   - Organisation prête à l'emploi

## Sécurité

### Protection SQL Injection

```python
# ❌ DANGEREUX
cur.execute(f"CREATE DATABASE {db_name}")

# ✅ SÉCURISÉ
cur.execute(
    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
)
```

### Chiffrement Passwords

```python
from cryptography.fernet import Fernet

# Avant stockage master DB
encrypted = encrypt_db_password(db_password)
org.database_password_hash = encrypted

# Lors connexion tenant
db_password = fernet.decrypt(encrypted).decode()
```

## Deprovisioning

### Soft Delete (Défaut)

- `deleted_at = datetime.now()`
- `status = OrganizationStatus.DELETED`
- Base de données gardée **30 jours** (RGPD droit à l'oubli)
- Restauration possible

### Hard Delete

```python
# Tuer connexions actives
pg_terminate_backend(pid) WHERE datname = 'studio_X_db'

# Supprimer base
DROP DATABASE IF EXISTS studio_X_db
DROP USER IF EXISTS studio_X_user

# Supprimer Organisation
session.delete(org)
```

## Flow Signup Complet

```python
TenantProvisioner.create_organization_with_trial(
    name="Studio Paris",
    slug="studio-paris",
    owner_email="owner@studio.com",
    owner_password="***",
    trial_days=14
)
```

1. Vérification unicité `slug` et `owner_email`
2. Création `Organization` (status=TRIAL, trial_ends_at)
3. Création `Subscription` (plan=Free, status=TRIAL)
4. Provisioning complet via `provision_tenant()`
5. Retour Organisation prête

## Variables d'Environnement

```bash
# Superuser PostgreSQL (CREATE DATABASE/USER)
POSTGRES_SUPERUSER=postgres
POSTGRES_SUPERUSER_PASSWORD=***
POSTGRES_MASTER_HOST=localhost
POSTGRES_MASTER_PORT=5432
POSTGRES_MASTER_DB=postgres

# Serveur tenant DBs
POSTGRES_TENANT_HOST=postgres-tenant-service
POSTGRES_TENANT_PORT=5432

# Encryption passwords DB
DB_ENCRYPTION_KEY=***
```

## Avantages Database-per-Tenant

- ✅ **Isolation maximale** : Données complètement séparées
- ✅ **Sécurité RGPD** : Suppression facile (DROP DATABASE)
- ✅ **Performance** : Pas de WHERE tenant_id sur chaque query
- ✅ **Scaling horizontal** : DBs sur serveurs différents
- ✅ **Backup granulaire** : pg_dump par organisation
- ✅ **Migrations indépendantes** : Tester sur un tenant

## Inconvénients

- ⚠️ Gestion complexe (N databases vs 1)
- ⚠️ Coût mémoire (pool connexions par tenant)
- ⚠️ Migrations à multiplier (une fois par tenant)

## Références

- Code : `utils/tenant_provisioner.py`
- Middleware : [[multi-tenant-routing]]
- Pattern : [[database-password-encryption]]
- Session : SESSION 4 (2025-11-30)
