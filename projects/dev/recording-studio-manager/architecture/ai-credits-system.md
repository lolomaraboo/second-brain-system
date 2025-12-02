# AI Credits System

**Date:** 2025-11-30
**Fichier source:** `utils/ai_credits_manager.py` (558 lignes)

## Concept

Système de crédits pour limiter l'usage des fonctionnalités IA selon le plan d'abonnement.

**1 requête IA = 1 crédit consommé**

## Business Plan

| Plan | Prix | Crédits/mois | Caractéristique |
|------|------|--------------|-----------------|
| **Starter** | 19€/mois | 50 crédits | Report illimité |
| **Pro** | 59€/mois | 500 crédits | Report illimité |
| **Enterprise** | Custom | Illimité | Pas de limite |

### Report Illimité (Unique !)

Le quota mensuel **s'AJOUTE** au solde existant au lieu de remplacer.

```
Exemple:
Mois 1: 50 crédits → utilisé 30 → reste 20
Mois 2: +50 crédits → solde = 70 crédits
Mois 3: +50 crédits → solde = 120 crédits

Avantages:
✅ Encourage usage modéré
✅ Pas de "use it or lose it"
✅ Accumulation pour gros projets
```

## Architecture

### AICreditsAccount (Master DB)

```python
class AICreditsAccount(Base):
    organization_id = Integer        # FK vers Organisation
    balance = Integer                # Solde actuel crédits
    monthly_quota = Integer          # Quota mensuel selon plan
    is_unlimited = Boolean           # True si Enterprise

    credits_used_this_month = Integer     # Stats utilisation
    credits_purchased = Integer           # Total acheté (packs)

    current_period_start = DateTime
    current_period_end = DateTime
    last_quota_reset = DateTime
```

### AICreditsTransaction (Master DB)

Audit trail de toutes les opérations crédits.

```python
class AICreditsTransaction(Base):
    organization_id = Integer
    type = Enum                      # usage, quota_monthly, purchase, plan_upgrade
    amount = Integer                 # +N ou -N
    balance_after = Integer          # Solde après opération

    description = String
    ai_request_id = String          # Traçabilité requête IA
    stripe_payment_id = String      # Si achat pack
    stripe_session_id = String
    pack_id = Integer               # FK vers AICreditsPack
```

### Types de Transactions

| Type | Amount | Déclencheur |
|------|--------|-------------|
| `usage` | -1 | Requête IA consommée |
| `quota_monthly` | +50/+500 | 1er du mois (cron) |
| `purchase` | +N | Achat pack crédits Stripe |
| `plan_upgrade` | +diff | Changement plan (ex: Free→Pro = +300) |

## AICreditsManager (Singleton)

```python
from utils.ai_credits_manager import get_ai_credits_manager

manager = get_ai_credits_manager()
```

### Consommation Crédit

```python
success, msg = manager.consume_credit(
    organization_id=123,
    ai_request_id="req_20251130_123456",
    description="AI Assistant chat message"
)

if not success:
    # Crédits insuffisants
    return 402  # Payment Required
```

**Avec SELECT FOR UPDATE** pour concurrence :

```python
account = session.query(AICreditsAccount)\
    .filter_by(organization_id=org_id)\
    .with_for_update()\
    .first()

if account.balance < 1:
    return False, "Crédits insuffisants"

account.balance -= 1
account.credits_used_this_month += 1

# Transaction log
transaction = AICreditsTransaction(
    type="usage",
    amount=-1,
    balance_after=account.balance,
    ai_request_id=ai_request_id
)
```

### Plans Illimités

```python
if account.is_unlimited:
    # Pas de débit, mais log quand même pour stats
    account.credits_used_this_month += 1

    transaction = AICreditsTransaction(
        type="usage",
        amount=0,  # 0 car illimité
        balance_after=-1,  # -1 convention illimité
        description="Requête IA (plan illimité)"
    )

    return True, "OK (unlimited)"
```

### Quota Mensuel (Cron)

```python
# Cron: 1er du mois à 00:00
manager.add_monthly_quota(org_id)

# Code
old_balance = account.balance  # Ex: 20 restants
account.balance += account.monthly_quota  # +50 = 70 total
account.credits_used_this_month = 0  # Reset compteur
account.last_quota_reset = datetime.now()

transaction = AICreditsTransaction(
    type="quota_monthly",
    amount=account.monthly_quota,
    balance_after=account.balance,
    description=f"Quota mensuel (+{monthly_quota}, report de {old_balance})"
)
```

### Achat Pack Crédits

```python
# Flow Stripe Checkout
manager.purchase_credits(
    organization_id=123,
    pack_id=1,  # Pack 100 crédits = 9.99€
    stripe_payment_id="pi_xxx",
    stripe_session_id="cs_xxx"
)

# Code
pack = session.query(AICreditsPack).get(pack_id)
account.balance += pack.credits  # +100
account.credits_purchased += pack.credits

transaction = AICreditsTransaction(
    type="purchase",
    amount=pack.credits,
    balance_after=account.balance,
    description=f"Achat {pack.name}",
    stripe_payment_id=stripe_payment_id,
    pack_id=pack_id
)
```

### Update Plan (Upgrade/Downgrade)

```python
# Appelé par webhook Stripe subscription.updated
manager.update_plan_quota(
    organization_id=123,
    new_monthly_quota=500,  # Free 50 → Pro 500
    is_unlimited=False
)

# Si upgrade, ajoute différence immédiatement
if new_quota > old_quota:
    diff = new_quota - old_quota  # 500 - 50 = 450
    account.balance += diff

    transaction = AICreditsTransaction(
        type="plan_upgrade",
        amount=diff,
        balance_after=account.balance,
        description=f"Upgrade plan: +{diff} crédits (nouveau quota: {new_quota}/mois)"
    )
```

### Stats Dashboard

```python
stats = manager.get_usage_stats(org_id)

{
    "balance": 150,  # ou None si illimité
    "is_unlimited": False,
    "monthly_quota": 500,
    "credits_used_this_month": 350,
    "credits_purchased": 200,
    "usage_percentage": 70.0,  # (350/500)*100
    "current_period_start": "2025-11-01T00:00:00",
    "current_period_end": "2025-12-01T00:00:00",
    "recent_transactions": [
        {
            "type": "usage",
            "amount": -1,
            "balance_after": 149,
            "description": "Requête IA",
            "created_at": "2025-11-30T14:23:00"
        },
        # ... 9 autres
    ]
}
```

### Historique avec Pagination

```python
transactions = manager.get_transaction_history(
    organization_id=123,
    limit=50,
    offset=0,
    type_filter="usage"  # Optionnel
)

[
    {
        "id": 456,
        "type": "usage",
        "amount": -1,
        "balance_after": 149,
        "description": "AI Assistant chat",
        "ai_request_id": "req_xxx",
        "created_at": "2025-11-30T14:23:00"
    },
    # ...
]
```

## Decorator @require_ai_credits

```python
from utils.ai_credits_manager import require_ai_credits
from utils.tenant_middleware import require_tenant

@app.route('/api/ai/chat')
@require_tenant
@require_ai_credits  # Vérifie + consomme automatiquement
def chat_with_ai():
    # Crédit déjà consommé ici
    # ai_request_id stocké dans g.ai_request_id

    tenant = get_current_tenant()
    ai_request_id = g.ai_request_id

    # ... logique IA ...
```

Retourne automatiquement :

```json
// Si crédits insuffisants
{
    "error": "insufficient_credits",
    "message": "Vous n'avez plus de crédits IA",
    "balance": 0,
    "upgrade_url": "/billing/upgrade",
    "purchase_url": "/billing/credits"
}
```

HTTP 402 Payment Required

## Packs Crédits Disponibles

```python
packs = manager.get_available_packs()

[
    {
        "id": 1,
        "name": "Pack 100 crédits",
        "description": "Crédits supplémentaires",
        "credits": 100,
        "price": 9.99,
        "currency": "EUR",
        "price_per_credit": 0.0999,
        "stripe_price_id": "price_xxx"
    },
    {
        "id": 2,
        "name": "Pack 500 crédits",
        "credits": 500,
        "price": 39.99,
        "price_per_credit": 0.0799  # Dégressif
    }
]
```

## Création Compte Automatique

```python
# Appelé automatiquement si account inexistant
account = manager.get_or_create_account(org_id)

# Détecte quota depuis plan subscription
plan = org.subscription.plan
monthly_quota = plan.limits.get("ai_credits_monthly", 200)
is_unlimited = plan.limits.get("ai_credits_unlimited", False)

# Commence avec le quota
account.balance = monthly_quota
account.monthly_quota = monthly_quota
account.is_unlimited = is_unlimited
```

## Pas d'Expiration

```
❌ Pas de système d'expiration
✅ Crédits achetés valables indéfiniment
✅ Quota mensuel s'accumule sans limite
```

## Références

- Code : `utils/ai_credits_manager.py`
- Stripe billing : [[stripe-billing-system]]
- Pricing : 19€ (Starter 50), 59€ (Pro 500), Custom (Enterprise illimité)
- Session : SESSION 4 (2025-11-30)
