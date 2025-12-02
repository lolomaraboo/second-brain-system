# Architecture Multi-Tenant

**Pattern:** Database-per-Tenant
**Fichier:** `models_platform.py`
**Date:** 2025-11-24

## Principe

Isolation complète des données clients via databases PostgreSQL séparées.

- **Master DB:** `studio_platform_master` (métadonnées SaaS)
- **Tenant DBs:** `studio_1_db`, `studio_2_db`, etc. (données opérationnelles)

## Avantages

1. **Sécurité**: Aucun tenant_id dans requêtes, impossible d'accéder aux données d'un autre tenant
2. **Performance**: Pas de WHERE tenant_id sur chaque requête, indexes optimisés par tenant
3. **Compliance**: Isolation physique pour RGPD, clients peuvent demander export/suppression DB complète
4. **Scalabilité**: Possibilité de migrer certains tenants vers serveurs PostgreSQL dédiés

## Inconvénients

1. **Coût**: Une DB par tenant vs une seule DB multi-tenant
2. **Migrations**: Alembic doit migrer N databases tenant lors upgrade schema
3. **Backup**: N backups séparés au lieu d'un seul

## Connexion Dynamique

```python
# Master DB (metadata SaaS)
master_engine = create_engine(MASTER_DATABASE_URL)

# Tenant DB (données client)
org = db.query(Organization).filter_by(subdomain="my-studio").first()
tenant_url = f"postgresql://{org.database_name}:{org.database_password}@{org.database_host}:5432/{org.database_name}"
tenant_engine = create_engine(tenant_url)
```

## Provisioning Nouveau Tenant

1. Création Organization dans Master DB (subdomain, database_name)
2. Génération password aléatoire (hashé bcrypt)
3. Exécution SQL `CREATE DATABASE studio_X_db`
4. Application migrations Alembic sur tenant DB
5. Création Subscription, AICreditsAccount
6. Déploiement config Nginx/Ingress pour routing

## Routing Requêtes

```
Client: GET https://my-studio.platform.com/sessions
  ↓
Nginx Ingress: Lit subdomain "my-studio"
  ↓
Flask Middleware: Query Master DB → trouve Organization
  ↓
Switch DB Context: Connexion vers studio_X_db
  ↓
Query Tenant DB: SELECT * FROM sessions
```

## Liens

- [[models-platform]] - Models Master Database
- [[../decisions/2025-11-24-database-per-tenant]] - Décision architecturale
