# SESSION 3 - Routes & API Documentation

**Date:** 2025-11-30
**Status:** ✅ Complété
**Lignes documentées:** 12,986

## Vue d'Ensemble

Documentation complète de toutes les routes et API de l'application Flask, couvrant l'interface publique, les APIs internes, l'administration et les intégrations externes.

## Fichiers Documentés

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `web/app.py` | 10,709 | Application principale Flask |
| `web/billing_routes.py` | 816 | Gestion Stripe & AI credits |
| `web/domain_routes.py` | 518 | Custom domains & SSL |
| `web/signup_routes.py` | 443 | Signup & provisioning |
| `web/admin_routes.py` | 500 | Panel administrateur |
| **TOTAL** | **12,986** | **5 fichiers** |

## Architecture Principale

### app.py - Cœur de l'Application (10,709 lignes)

#### Public Booking System

**API Publique sans authentification:**
- `POST /api/public/booking` - Créer réservation
- `GET /api/public/booking/<ref>` - Détails réservation
- `POST /api/public/booking/<ref>/cancel` - Annuler
- `GET /api/public/bookings/search?email` - Recherche par email

**Intégration Stripe:**
- `POST /api/public/booking/<ref>/create-payment` - Checkout session
- `POST /api/stripe/webhook` - Webhooks Stripe
- Auto-confirmation après deposit si policy configurée
- Gestion refunds avec calcul prorata

#### Staff Management (Auth Required)

- `GET /api/bookings` - Liste avec filtres
- `POST /api/bookings/<id>/confirm` - Confirmer
- `POST /api/bookings/<id>/convert` - Convertir en Session
- Decorator: `@staff_login_required`

#### Audit Log System

**API Sécurité:**
- `GET /api/audit-logs` - Liste avec filtres complexes
- `GET /api/audit-logs/stats` - Statistiques
- `GET /api/audit-logs/export` - Export CSV
- `POST /api/audit-logs/cleanup` - Nettoyage

**Helpers automatiques:**
- `log_create()`, `log_update()`, `log_delete()`
- `log_view()`, `log_login()`, `log_logout()`
- Tracking: IP, user agent, request info
- Détection risque automatique

#### RBAC (Roles & Permissions)

**Gestion des rôles:**
- `GET/POST /api/roles` - CRUD rôles
- `GET/PUT/DELETE /api/roles/<id>` - Gestion
- `GET /api/roles/<id>/permissions` - Avec héritage

**Permission Matrix:**
- `GET /api/permissions/matrix` - Matrice complète pour UI
- `GET /api/permissions/resources` - Ressources disponibles
- `GET /api/permissions/actions` - Actions disponibles

**Assignment:**
- `POST /api/users/<id>/roles` - Assigner rôle
- `DELETE /api/users/<id>/roles/<role_id>` - Révoquer
- Support rôles temporaires avec expiration

#### Theme Management

**Customization UI:**
- `GET/POST /api/themes` - CRUD thèmes
- `GET /api/themes/<id>/css` - CSS variables
- `PUT /api/user/theme` - Préférence utilisateur
- `PUT /api/user/custom-colors` - Couleurs custom
- Auto dark mode avec horaires

#### Internationalization (i18n)

- `GET /api/i18n/languages` - Langues supportées
- `POST /api/i18n/set` - Définir langue (avec auth)
- `POST /api/i18n/set-session` - Sans auth
- Sauvegarde dans `User.language_preference`

#### Multi-Currency

**Devises:**
- `GET /api/currencies` - Liste devises actives
- `POST /api/currencies/convert` - Conversion
- `GET /api/currencies/rates` - Taux de change
- `POST /api/currencies/rates/refresh` - MAJ depuis API

**Préférences:**
- `GET/PUT /api/user/currency` - Devise utilisateur
- Conversion automatique dans UI

#### Reports Builder

**Création rapports:**
- `POST /api/reports/build` - Rapport personnalisé
  - Export: JSON, CSV, Excel, PDF
  - Filtres, grouping, sorting, aggregations

**Templates:**
- `GET /api/reports/templates` - Prédéfinis
- `POST /api/reports/templates/saved` - Sauvegarder custom
- `GET /api/reports/templates/<id>/build` - Générer

**Scheduled:**
- `GET/POST /api/reports/scheduled` - Planifiés
- Fréquences: DAILY, WEEKLY, MONTHLY
- Envoi email automatique

#### AI Assistant

**Chatbot contextuel:**
- `POST /api/ai/chat` - Message au chatbot
- `GET /api/ai/conversation/<session_id>` - Historique
- `GET /api/ai/context` - Contexte studio actuel
- Providers: Anthropic Claude, OpenAI GPT

### billing_routes.py (816 lignes)

**Blueprint:** `/api/billing`

#### Stripe Subscriptions

**Checkout:**
- `GET/POST /api/billing/create-checkout`
  - Params: plan_id, billing_period
  - GET → redirect Stripe
  - POST → JSON avec checkout_url

**Management:**
- `POST /api/billing/upgrade` - Upgrade avec proration
- `POST /api/billing/downgrade` - Downgrade (immediate ou fin période)
- `POST /api/billing/cancel` - Annulation

**Info:**
- `GET /api/billing/subscription` - Détails subscription
- `GET /api/billing/plans` - Plans disponibles
- `GET /api/billing/usage` - Usage vs limites

#### AI Credits

**Gestion crédits:**
- `GET /api/billing/credits` - Balance & stats
- `GET /api/billing/credits/packs` - Packs disponibles
- `POST /api/billing/credits/purchase` - Acheter pack
- `GET /api/billing/credits/history` - Historique transactions

#### Webhooks & Portal

- `POST /api/billing/webhooks/stripe` - Events Stripe
- `GET /api/billing/portal` - Customer Portal Stripe

### domain_routes.py (518 lignes)

**Blueprint:** `/api/domains`

#### Gestion Domaines

**CRUD:**
- `GET /api/domains` - Liste domaines org
- `POST /api/domains` - Ajouter custom domain
- `DELETE /api/domains/<id>` - Supprimer

**Verification:**
- `POST /api/domains/<id>/verify` - Vérification DNS + SSL
  - TXT record (ownership)
  - CNAME record (routing)
  - Création certificat SSL si verified

**Status:**
- `GET /api/domains/<id>/status` - Statut temps réel
  - DNS status (TXT + CNAME)
  - SSL status (certificate, expiry, renewal)

**Configuration:**
- `POST /api/domains/<id>/set-primary` - Domain principal
  - Requires: verified + SSL active

### signup_routes.py (443 lignes)

**Flow complet signup:**

#### API

- `GET /api/signup/check-slug?slug` - Disponibilité
- `POST /signup` - Créer organisation
- `GET /signup/success` - Page succès
- `GET /onboarding` - Wizard 5 étapes

#### Provisioning

**TenantProvisioner.create_organization_with_trial():**
1. Crée Organization dans master DB
2. Provisionne tenant database
3. Crée user avec password hash
4. Trial 14 jours (configurable)

#### Onboarding Wizard

**5 étapes:**
1. Welcome + guided tour
2. Créer première salle
3. Configurer tarifs
4. Inviter staff
5. Choisir plan (Stripe)

#### Welcome Email

- Envoi automatique après signup
- Contient credentials (⚠️ password en clair)
- Studio URL, trial info
- Recommande changement password

### admin_routes.py (500 lignes)

**Panel Admin:**

- `POST /admin/login` - Auth admin
- `GET /admin/dashboard` - Stats
  - Total users/staff
  - Active sessions
  - Monthly revenue
  - Rooms count
- CRUD users/staff

Session admin séparée (`admin_id` dans flask session)

## Points Techniques Clés

### Multi-Tenant Architecture

- **Master DB:** Organizations, Plans, Subscriptions, Domains
- **Tenant DB:** Per-org database (provisioned on signup)
- **Middleware:** `@require_tenant` decorator

### Stripe Integration

- Subscriptions: monthly/yearly
- Checkout Sessions redirect flow
- Webhooks: payment events
- AI Credits: one-time payments
- Proration automatique

### Custom Domains & SSL

- DNS: TXT (ownership) + CNAME (routing)
- SSL: cert-manager Kubernetes
- Let's Encrypt: auto-issuance
- Status: PENDING → PROVISIONING → ACTIVE

### Security

- Audit logs complets
- RBAC avec héritage
- Détection risque
- IP tracking

### AI

- Context-aware chatbot
- Studio state (rooms, sessions)
- Multi-provider support

## Métriques

**Total documenté:** 12,986 lignes
**Fichiers:** 5
**Mémoires Mem0:** ~47
**Couverture projet:** 34% (16,400/48,000 lignes)

## Prochaines Étapes

**SESSION 4 - Utils Critiques** (~8,000 lignes)
- stripe_subscriptions.py
- ai_credits_manager.py
- tenant_provisioner.py
- domain_verifier.py / ssl_manager.py
- audit_logger.py / permission_manager.py
- theme_manager.py / currency_manager.py / i18n_manager.py

---

**Tags:** #architecture #api #routes #documentation
**Session:** 3/7
**Date:** 2025-11-30
