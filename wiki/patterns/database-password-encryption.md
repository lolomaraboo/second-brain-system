# Database Password Encryption Pattern

**Date:** 2025-11-30
**Context:** Multi-tenant SaaS with database-per-tenant
**Projet:** Recording Studio Manager

## Problème

Dans une architecture database-per-tenant, chaque organisation a ses propres credentials PostgreSQL (user, password) stockés dans la master DB. Ces passwords doivent être :

1. Stockés de manière sécurisée (pas en clair)
2. Récupérables (contrairement à bcrypt) pour connexion automatique
3. Protégés contre compromission de la master DB

## Solution

Chiffrement symétrique avec **Fernet** (cryptography.io)

### Architecture

```
Master DB
├── Organization
│   ├── database_user = "studio_123_user"
│   ├── database_password_hash = "gAAAA..." (CHIFFRÉ)
│   └── database_host/port/name
│
Fernet Key (environnement)
└── DB_ENCRYPTION_KEY = "base64 key 32 bytes"
```

## Implémentation

### 1. Génération de la clé

```bash
# Une seule fois, stocker dans .env
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Résultat : xGH7J9kL2mP5qR8sU1vW4yZ6A3bC5dE7fG9hJ0kL2mN=
```

### 2. Configuration environnement

```bash
# .env (JAMAIS commiter)
DB_ENCRYPTION_KEY=xGH7J9kL2mP5qR8sU1vW4yZ6A3bC5dE7fG9hJ0kL2mN=
```

### 3. Utils

```python
import os
from cryptography.fernet import Fernet

# Singleton Fernet cipher
_fernet = None

def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.getenv("DB_ENCRYPTION_KEY")
        if not key:
            raise ValueError("DB_ENCRYPTION_KEY not set")
        _fernet = Fernet(key.encode())
    return _fernet

def encrypt_db_password(plaintext: str) -> str:
    """Chiffre un password DB pour stockage master DB"""
    cipher = get_fernet()
    encrypted = cipher.encrypt(plaintext.encode())
    return encrypted.decode()  # Stockable en String

def decrypt_db_password(ciphertext: str) -> str:
    """Déchiffre un password DB pour connexion tenant"""
    cipher = get_fernet()
    decrypted = cipher.decrypt(ciphertext.encode())
    return decrypted.decode()
```

### 4. Utilisation Provisioning

```python
# tenant_provisioner.py
import secrets

def provision_tenant(org_id: int):
    # Générer password aléatoire fort
    db_password = secrets.token_urlsafe(32)  # 43 chars

    # Créer user PostgreSQL
    cur.execute(
        sql.SQL("CREATE USER {} WITH ENCRYPTED PASSWORD %s")
        .format(sql.Identifier(db_user)),
        [db_password]  # Parameterized query
    )

    # Chiffrer avant stockage master DB
    encrypted = encrypt_db_password(db_password)
    org.database_password_hash = encrypted
    session.commit()
```

### 5. Utilisation Middleware

```python
# tenant_middleware.py

def get_tenant_connection(tenant: Organization):
    # Déchiffrer password pour connexion
    db_password = decrypt_db_password(tenant.database_password_hash)

    # Construire URL connexion
    db_url = f"postgresql://{tenant.database_user}:{db_password}@{tenant.database_host}:{tenant.database_port}/{tenant.database_name}"

    # Pool SQLAlchemy
    engine = create_engine(db_url, ...)
    return scoped_session(sessionmaker(bind=engine))
```

## Sécurité

### ✅ Protection contre

- **DB Dump master DB** : Passwords chiffrés inutilisables sans clé
- **SQL Injection** : Pas de passwords en clair dans logs
- **Logs application** : Password jamais loggé (déchiffrement in-memory uniquement)

### ⚠️ Limitations

- **Clé compromise** : Tous les passwords déchiffrables
  - Mitigation : Rotation clé + re-chiffrement batch
- **Accès serveur** : Si .env accessible, clé récupérable
  - Mitigation : Secrets manager (AWS Secrets Manager, HashiCorp Vault)

## Rotation de Clé

```python
def rotate_encryption_key(old_key: str, new_key: str):
    """Re-chiffre tous les passwords avec nouvelle clé"""
    old_fernet = Fernet(old_key.encode())
    new_fernet = Fernet(new_key.encode())

    orgs = session.query(Organization).all()

    for org in orgs:
        # Déchiffrer avec ancienne clé
        plaintext = old_fernet.decrypt(org.database_password_hash.encode()).decode()

        # Re-chiffrer avec nouvelle clé
        new_encrypted = new_fernet.encrypt(plaintext.encode()).decode()
        org.database_password_hash = new_encrypted

    session.commit()
```

## Alternatives Considérées

| Solution | Avantages | Inconvénients | Verdict |
|----------|-----------|---------------|---------|
| **Bcrypt** | Standard passwords | Non-réversible | ❌ Impossible connexion auto |
| **AES (raw)** | Rapide | Complexe (IV, padding) | ⚠️ Fernet plus simple |
| **Secrets Manager** | Rotation automatique | Coût, latence réseau | ✅ Recommandé en prod |
| **Fernet** | Simple, sécurisé | Clé unique centralisée | ✅ **CHOISI** |

## Production-Ready

Pour production à grande échelle :

```python
import boto3

def get_db_password_from_secrets_manager(org_id: int) -> str:
    """Alternative production avec AWS Secrets Manager"""
    client = boto3.client('secretsmanager')

    secret_name = f"tenant/{org_id}/db_password"
    response = client.get_secret_value(SecretId=secret_name)

    return response['SecretString']
```

Avantages :
- Rotation automatique
- Audit CloudTrail
- IAM permissions granulaires
- Pas de clé en environnement

## Références

- **Projet** : Recording Studio Manager `tenant_provisioner.py`, `tenant_middleware.py`
- **Lib** : [cryptography.io Fernet](https://cryptography.io/en/latest/fernet/)
- **Pattern** : [[multi-tenant-provisioning]]
- **Session** : SESSION 4 (2025-11-30)
