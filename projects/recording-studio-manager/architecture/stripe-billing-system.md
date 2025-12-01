# Stripe Billing System

**Date:** 2025-11-30
**Fichiers sources:**
- `utils/stripe_subscriptions.py` (854 lignes)
- `utils/stripe_integration.py` (395 lignes)

## Architecture

### 2 Modules Distincts

| Module | Usage | Mode Stripe |
|--------|-------|-------------|
| `stripe_subscriptions.py` | Abonnements récurrents (plans SaaS) | `mode=subscription` |
| `stripe_integration.py` | Paiements ponctuels (factures) | `mode=payment` |

## Abonnements Récurrents

### StripeSubscriptionManager (Singleton)

```python
from utils.stripe_subscriptions import get_stripe_manager

manager = get_stripe_manager()
```

### Flow Complet Signup

```
1. User clique "Upgrade to Pro"
    ↓
2. create_checkout_session(org, plan, billing_period)
    → Stripe Checkout URL
    ↓
3. Redirect user vers Stripe
    ↓
4. User entre carte bancaire
    ↓
5. Webhook: customer.subscription.created
    → Active subscription dans master DB
    ↓
6. Redirect /billing/success
```

### Checkout Session

```python
session = stripe.checkout.Session.create(
    customer=customer_id,
    mode="subscription",
    line_items=[{"price": price_id, "quantity": 1}],
    success_url="/billing/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url="/billing/cancel",
    metadata={
        "organization_id": org.id,
        "plan_id": plan.id,
        "billing_period": "monthly"
    },
    allow_promotion_codes=True,  # Codes promo
)
```

### 7 Webhooks Stripe Gérés

| Événement | Action |
|-----------|--------|
| `customer.subscription.created` | Active subscription, Organisation TRIAL→ACTIVE |
| `customer.subscription.updated` | Update période, si plan change → update AI credits quota |
| `invoice.payment_succeeded` | Renouvellement mensuel, reset payment_failed_count=0 |
| `invoice.payment_failed` | Incrémente échecs, PAST_DUE après 1, SUSPENDED après 3 |
| `customer.subscription.deleted` | Suspend Organisation, status=CANCELLED |
| `charge.refunded` | Log remboursement, TODO: audit trail |
| `checkout.session.completed` | Détecte achat crédits IA via metadata.type |

### Upgrade/Downgrade avec Prorata

#### Upgrade (Plan Supérieur)

```python
manager.upgrade_subscription(org, new_plan, billing_period)

# Stripe gère automatiquement :
# - Calcul temps non utilisé plan actuel
# - Crédit prorata
# - Facturation immédiate nouveau plan
```

Config Stripe :
```python
stripe.Subscription.modify(
    subscription_id,
    items=[{"price": new_price_id}],
    proration_behavior="always_invoice",  # Facture prorata immédiatement
)
```

#### Downgrade (Plan Inférieur)

**Option 1 : Fin de période (défaut)**

```python
manager.downgrade_subscription(org, new_plan, immediate=False)

# Changement appliqué à current_period_end
# Pas de remboursement
```

Config Stripe :
```python
proration_behavior="none",
billing_cycle_anchor="unchanged",
```

**Option 2 : Immédiat**

```python
manager.downgrade_subscription(org, new_plan, immediate=True)

# Changement immédiat avec crédit prorata
```

Config Stripe :
```python
proration_behavior="create_prorations",  # Crédit prorata
```

### Annulation Subscription

```python
# À la fin de la période (défaut)
manager.cancel_subscription(org, cancel_at_period_end=True)

# Immédiat
manager.cancel_subscription(org, cancel_at_period_end=False)
```

### Gestion Suspension Automatique

```python
# Webhook: invoice.payment_failed
payment_failed_count += 1

if payment_failed_count == 1:
    subscription.status = SubscriptionStatus.PAST_DUE

if payment_failed_count >= 3:
    org.status = OrganizationStatus.SUSPENDED
    org.suspended_reason = "Payment failed after 3 attempts"
    org.suspended_at = datetime.now()
```

### Intégration AI Credits

```python
# Webhook: customer.subscription.updated
if plan_id_changed:
    new_plan = session.query(Plan).get(new_plan_id)
    new_quota = new_plan.limits.get("ai_credits_monthly", 200)
    is_unlimited = new_plan.limits.get("ai_credits_unlimited", False)

    from utils.ai_credits_manager import get_ai_credits_manager
    manager = get_ai_credits_manager()
    manager.update_plan_quota(org_id, new_quota, is_unlimited)
```

## Paiements Ponctuels

### StripePaymentManager

```python
from utils.stripe_integration import StripePaymentManager

manager = StripePaymentManager()
```

### Checkout Session (Facture)

```python
result = manager.create_checkout_session(
    invoice_id=123,
    invoice_number="INV-2024-001",
    amount=150.00,  # EUR
    currency="eur",
    success_url="/payments/success",
    customer_email="client@studio.com"
)

# Retourne
{
    "session_id": "cs_xxx",
    "url": "https://checkout.stripe.com/...",
    "payment_status": "unpaid"
}
```

### PaymentIntent (UI Custom)

```python
result = manager.create_payment_intent(
    amount=150.00,
    invoice_id=123
)

# Retourne client_secret pour frontend
{
    "payment_intent_id": "pi_xxx",
    "client_secret": "pi_xxx_secret_yyy",
    "status": "requires_payment_method"
}
```

### Remboursements

```python
# Remboursement complet
result = manager.create_refund(
    payment_intent_id="pi_xxx",
    reason="requested_by_customer"
)

# Remboursement partiel
result = manager.create_refund(
    payment_intent_id="pi_xxx",
    amount=50.00,  # 50€ sur 150€
    reason="duplicate"
)
```

Raisons possibles : `duplicate`, `fraudulent`, `requested_by_customer`

### Récupération Détails Paiement

```python
result = manager.retrieve_payment_intent("pi_xxx")

{
    "payment_intent_id": "pi_xxx",
    "status": "succeeded",
    "amount": 150.00,
    "charge_id": "ch_xxx",
    "receipt_url": "https://pay.stripe.com/receipts/..."
}
```

## Conversion EUR ↔ Cents

```python
# TOUJOURS convertir en cents pour Stripe API
amount_cents = int(amount_euros * 100)

stripe.checkout.Session.create(
    line_items=[{
        "price_data": {
            "unit_amount": amount_cents,  # 15000 pour 150.00€
            "currency": "eur"
        }
    }]
)

# Reconvertir lors récupération
amount_euros = invoice["amount_paid"] / 100
```

## Gestion Customers

```python
# Créer customer
customer = manager.create_customer(
    email="owner@studio.com",
    name="Studio Paris",
    metadata={"organization_id": 123}
)

# Lister méthodes paiement
methods = manager.list_payment_methods(customer_id)

[
    {
        "id": "pm_xxx",
        "type": "card",
        "card": {
            "brand": "visa",
            "last4": "4242",
            "exp_month": 12,
            "exp_year": 2025
        }
    }
]
```

## Webhook Verification

```python
def handle_webhook(payload: bytes, signature: str):
    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )

        event_type = event["type"]
        data = event["data"]["object"]

        # Router vers handler spécifique
        handlers = {
            "customer.subscription.created": _handle_subscription_created,
            "invoice.payment_succeeded": _handle_payment_succeeded,
            # ...
        }

        handler = handlers.get(event_type)
        if handler:
            return handler(event)

    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}, 400
```

## Balance Compte Stripe

```python
balance = manager.get_balance()

{
    "available": [
        {"amount": 1250.00, "currency": "eur"}
    ],
    "pending": [
        {"amount": 350.00, "currency": "eur"}
    ]
}
```

## Variables d'Environnement

```bash
# API Keys
STRIPE_SECRET_KEY=sk_live_xxx  # ou sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Test mode detection
is_test = os.getenv("STRIPE_SECRET_KEY").startswith("sk_test_")
```

## Mode Test vs Production

```python
from utils.stripe_integration import is_test_mode

if is_test_mode():
    # Cartes de test Stripe
    # 4242 4242 4242 4242 → Succès
    # 4000 0000 0000 0002 → Carte déclinée
else:
    # Mode production, vraies cartes
```

## Références

- Code subscriptions : `utils/stripe_subscriptions.py`
- Code paiements : `utils/stripe_integration.py`
- AI Credits : [[ai-credits-system]]
- Session : SESSION 4 (2025-11-30)
