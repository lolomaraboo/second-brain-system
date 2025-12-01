# Models Platform (Master Database)

**Fichier:** `app/models_platform.py` (902 lignes)
**Database:** `studio_platform_master`
**Stack:** SQLAlchemy, PostgreSQL 15

## Vue d'ensemble

12 models SQLAlchemy pour gérer la plateforme SaaS multi-tenant.

## Models Core SaaS (4 models)

### Organization
**Lignes:** 35-122
**Responsabilité:** Représente un client (studio) de la plateforme

**Champs clés:**
- `subdomain`: Routing HTTP (ex: "my-studio")
- `database_name`: Nom DB tenant (ex: "studio_1_db")
- `status`: TRIAL, ACTIVE, SUSPENDED, CANCELLED, DELETED
- `trial_ends_at`: Fin période essai 14 jours

**Relations:**
- `subscription` (1-to-1)
- `domains` (1-to-many)

### Plan
**Lignes:** 534-626
**Responsabilité:** Catalogue offres tarifaires

**Limites JSON:**
```json
{
  "rooms": 1,
  "sessions_per_month": 50,
  "storage_gb": 5,
  "clients": 20,
  "users": 1,
  "stripe_payments": false,
  "custom_domain": false,
  "sms_notifications": false
}
```

**Plans:** Free (0€), Starter (19€/mois), Pro (59€/mois), Enterprise (sur devis)

### Subscription
**Lignes:** 335-446
**Responsabilité:** Souscription active d'une organisation

**Champs clés:**
- `stripe_subscription_id`: ID souscription Stripe
- `stripe_status`: "active", "past_due", "canceled", etc.
- `usage_json`: Tracking usage quotas (`{"sessions_this_month": 25}`)

**Méthodes:**
- `check_limit(limit_name)`: Enforce plan limits

### Domain
**Lignes:** 448-532
**Responsabilité:** Custom domains (ex: studio.mycustom.com)

**Champs clés:**
- `domain_name`: FQDN unique
- `verification_token`: DNS TXT record verification
- `ssl_status`: PENDING, ISSUED, RENEWING, EXPIRED, FAILED
- `k8s_ingress_name`: Ressource Kubernetes Ingress

**Flow:** DNS verification → cert-manager → Let's Encrypt SSL → Nginx Ingress

## Model Admin (1 model)

### PlatformUser
**Lignes:** 264-330
**Responsabilité:** Super-admins plateforme (pas tenants)

**Rôles:**
- `SUPER_ADMIN`: Accès total
- `SUPPORT`: Lecture orgs, suspend
- `BILLING`: Gestion Stripe, refunds
- `VIEWER`: Analytics

**Sécurité:**
- Password bcrypt cost 12
- 2FA TOTP obligatoire pour SUPER_ADMIN
- Audit trail (last_login_at, last_login_ip)

## Models AI Credits (3 models)

### AICreditsAccount
**Lignes:** 752-806
**Responsabilité:** Compte crédits AI par organisation

**Champs:**
- `balance`: Crédits disponibles
- `monthly_quota`: Quota inclus plan (Free: 10, Pro: 200)
- `is_unlimited`: Plans Enterprise custom

**Méthodes:**
- `has_credits()`: Vérifie si crédits disponibles (erreur 402 si non)

### AICreditsTransaction
**Lignes:** 808-860
**Responsabilité:** Historique transactions crédits (ledger append-only)

**Types:** quota_monthly, purchase, usage, refund, adjustment, plan_upgrade

**Champs:**
- `amount`: +/- crédits
- `balance_after`: Audit trail
- `stripe_payment_id`: Lien paiement Stripe

### AICreditsPack
**Lignes:** 862-902
**Responsabilité:** Catalogue packs crédits achetables

**Packs:** 100 crédits (2€), 300 (5€), 500 (7€)

## Models Features Avancées (4 models)

### WebhookEndpoint
**Lignes:** 634-659
**Responsabilité:** Endpoints webhooks configurables par org

**Champs:** url, secret (HMAC), events (array), is_active

### WebhookDeliveryLog
**Lignes:** 661-684
**Responsabilité:** Logs delivery webhooks

**Features:** Retry 3x backoff exponentiel, archive 30j

### SSOConfiguration
**Lignes:** 686-715
**Responsabilité:** SSO SAML/OAuth pour Enterprise

**Providers:** Okta, Google Workspace, Azure AD

### OrganizationBranding
**Lignes:** 717-748
**Responsabilité:** White-label Pro/Enterprise

**Champs:** logo_url, primary_color, custom_css_url

## Conventions

- Tables: snake_case pluriel (`organizations`, `subscriptions`)
- Foreign keys: `{table}_id`
- Timestamps: `created_at`, `updated_at` partout
- Soft delete: `deleted_at` nullable
- Indexes: Unique + recherche fréquente

## Sécurité

- Passwords: bcrypt cost 12
- Secrets: Fernet symmetric encryption
- Validation: Email format, HTTPS only
- Audit: Logs sur models sensibles

## Liens

- [[multi-tenant]] - Architecture Database-per-Tenant
- [[../decisions/2025-11-24-database-per-tenant]]
