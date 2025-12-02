# Recording Studio Manager

Application SaaS de gestion de studio d'enregistrement.

## Stack

- Backend: Flask + SQLAlchemy
- Base de données: PostgreSQL (multi-tenant)
- Architecture: Database-per-Tenant
- Pricing: 19€/mois (Starter), 59€/mois (Pro)
- Crédits AI: 50 (Starter), 500 (Pro)

## Documentation

### Sessions complétées

- ✅ **SESSION 1/7** - models_platform.py (902 lignes, 12 modèles Master DB)
  - Fichier: `~/recording-studio-manager/.session1-progress.md`
  - 80 mémoires Mem0 créées

- ✅ **SESSION 2/7** - models.py (2512 lignes, 50 modèles Tenant DB)
  - Fichier: `~/recording-studio-manager/.session2-progress.md`
  - 55+ mémoires Mem0 créées
  - Méthode: [[streaming-documentation]]

- ✅ **SESSION 3/7** - Routes & API (12,986 lignes, 5 fichiers web/)
  - Fichier: `~/recording-studio-manager/.session3-progress.md`
  - Note: [[session3-routes-api]]
  - ~47 mémoires Mem0 créées
  - Contenu: Public Booking, Stripe, Domains/SSL, Signup, Admin, RBAC, Themes, i18n, Currency, Reports, AI Assistant

- ✅ **SESSION 4/7** - Utils critiques (3,052 lignes, 5 fichiers utils/)
  - Fichier: `~/recording-studio-manager/.session4-progress.md`
  - 74 mémoires Mem0 créées
  - Méthode: [[streaming-documentation]]
  - Contenu: Stripe Subscriptions, Stripe Payments, AI Credits Manager, Tenant Provisioner, Tenant Middleware
  - Architecture: [[multi-tenant-provisioning]], [[multi-tenant-routing]], [[stripe-billing-system]], [[ai-credits-system]]
  - Patterns: [[database-password-encryption]], [[sqlalchemy-connection-pooling]]

### À faire

- ⏳ SESSION 5/7 - Intégrations externes (~5,000 lignes)
- ⏳ SESSION 6/7 - Tests & Migrations (~10,000 lignes)
- ⏳ SESSION 7/7 - Scripts & Examples (~8,570 lignes)

**Total documenté:** 19,452 lignes (40% du code)
**Total restant:** ~28,518 lignes

## Fichiers

- decisions/ : Décisions architecturales
- architecture/ : Architecture multi-tenant

## Liens

- Repo: ~/Documents/APP_HOME/CascadeProjects/windsurf-project/recording-studio-manager
- Prod: https://recording-studio-manager.com
- GitHub: https://github.com/lolomaraboo/recording-studio-manager
