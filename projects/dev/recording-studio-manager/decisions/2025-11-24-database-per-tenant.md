# Décision: Database-per-Tenant

**Date:** 2025-11-24
**Statut:** ✅ Implémenté
**Décideur:** Architecture initiale
**Impact:** Architecture multi-tenant

## Contexte

Application SaaS multi-tenant nécessitant isolation données entre studios clients. Deux patterns possibles:

1. **Shared Database** (1 DB, colonne tenant_id partout)
2. **Database-per-Tenant** (1 DB par client)

## Décision

Choix: **Database-per-Tenant**

Chaque organisation cliente a sa propre PostgreSQL database (`studio_1_db`, `studio_2_db`, etc.).

## Raisons

### Sécurité ✅
- Isolation physique complète
- Impossible d'accéder données autre tenant (pas de WHERE tenant_id oublié)
- Audit trail simple: 1 DB = 1 client

### Performance ✅
- Pas de WHERE tenant_id sur TOUTES les requêtes
- Indexes optimisés par tenant
- Queries plans PostgreSQL plus simples

### Compliance ✅
- RGPD: Export/suppression DB complète facile
- Demande client "supprime toutes mes données" = DROP DATABASE
- Backup par client si requis contractuellement

### Scalabilité ✅
- Migration tenant vers serveur PostgreSQL dédié si croissance
- Horizontal sharding par DB (studio_X_db sur server1, studio_Y_db sur server2)

## Conséquences

### Avantages
- Sécurité renforcée
- Performance améliorée
- Compliance simplifiée
- Scalabilité horizontale

### Inconvénients
- **Coût infrastructure**: N databases vs 1
- **Complexité migrations**: Alembic doit migrer N DBs lors upgrade schema
- **Complexité backup**: N backups vs 1 backup global
- **Monitoring**: N connexions PostgreSQL à surveiller

## Implémentation

### Master Database
`studio_platform_master` contient:
- `organizations` (metadata clients)
- `plans`, `subscriptions` (billing)
- `domains` (custom domains)
- `platform_users` (super-admins)
- `ai_credits_*` (quotas AI)

### Tenant Databases
`studio_X_db` contient:
- `users` (staff studio)
- `clients` (carnet adresses)
- `rooms` (salles)
- `sessions` (réservations)
- `audio_files`, `invoices`, etc.

### Routing
```python
subdomain = request.host.split('.')[0]  # "my-studio"
org = db.query(Organization).filter_by(subdomain=subdomain).first()
tenant_url = f"postgresql://{org.database_name}:{org.database_password}@{org.database_host}/{org.database_name}"
tenant_db = create_engine(tenant_url)
```

## Alternatives Considérées

### 1. Shared Database avec tenant_id
**Rejeté car:**
- Risque sécurité (oubli WHERE tenant_id)
- Performance dégradée (indexes globaux)
- Compliance compliquée (export partiel)

### 2. Schema-per-Tenant (1 DB, N schemas)
**Rejeté car:**
- Moins bon que Database-per-Tenant
- Toujours risque cross-schema leak
- Pas vraiment d'avantages vs Database-per-Tenant

## Monitoring

### Métriques à surveiller
- Nombre total databases tenant
- Taille moyenne DB tenant
- Temps migration schema (upgrade)
- Temps backup par tenant

### Alertes
- DB tenant > 10 GB (possibilité migration serveur dédié)
- Échec migration DB tenant (rollback requis)
- Temps backup > 30 min

## Évolutions Futures

### Court terme
- Script automatisation provisioning tenant DB
- Backup automatique daily par tenant
- Monitoring Prometheus per-DB metrics

### Moyen terme
- Migration tenants "gros" vers PostgreSQL dédié
- Read replicas pour analytics par tenant
- Archive old tenants (CANCELLED > 1 an)

### Long terme
- Sharding géographique (EU vs US databases)
- Multi-region pour latence

## Validation

### Tests
✅ Provisioning nouveau tenant (< 30s)
✅ Isolation données (impossible query cross-tenant)
✅ Migration schema N databases (< 5 min pour 100 tenants)
✅ Performance queries (pas de dégradation vs shared DB)

### Résultats Production
- 0 incidents cross-tenant data leak
- Temps provisioning: ~15s par tenant
- Migration 50 tenants: ~2 min

## Références

- [[../architecture/multi-tenant]]
- [[../architecture/models-platform]]
- Alembic multi-DB: `scripts/migrate_all_tenants.py`
- Provisioning: `app/services/tenant_provisioner.py`

## Révisions

| Date | Changement | Raison |
|------|-----------|--------|
| 2025-11-24 | Décision initiale Database-per-Tenant | Architecture v1 |
