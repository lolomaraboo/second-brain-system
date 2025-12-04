# Recording Studio Manager - Session Resume

**Date:** 2025-12-04
**Status:** ✅ Chatbot opérationnel

## État Actuel du Projet

Application SaaS multi-tenant en production sur 31.220.104.244
- Architecture: Database-per-Tenant (PostgreSQL)
- Backend: Flask/Gunicorn (Docker)
- Frontend: HTTPS avec certificat wildcard
- Organisation active: maraboo (TRIAL) → DB studio_5_db
- **NOUVEAU**: Chatbot IA fonctionnel avec Claude Haiku

## Dernière Session (2025-12-04)

**Objectif:** Tests chatbot complets

**Résultat:** ✅ Chatbot opérationnel après correction configuration Docker
- Test envoi message: "Combien de clients j'ai actuellement?"
- Réponse intelligente reçue avec function calling
- Performance: 15136 tokens, 2664ms latency

## Décisions Techniques Clés

1. **Architecture tenant DB confirmée:**
   - Superuser unique (studio_user) pour toutes les connexions tenant
   - Pas de users PostgreSQL individuels par tenant
   - Middleware résout: subdomain → organization → tenant DB connection

2. **Initialisation tenant DB:**
   - Master DB: `database_manager_saas.py` (tables platform)
   - Tenant DB: `models.Base.metadata.create_all()` (tables application)

3. **Chatbot AI Assistant:**
   - Provider: Anthropic Claude (claude-3-haiku-20240307)
   - API endpoint: POST /api/ai/chat
   - Features: Function calling, contexte de session, historique
   - Interface: Panneau latéral avec input, statistiques temps réel
   - Authentification: Nécessite staff_id en session + CSRF token

## Fichiers Modifiés (Session actuelle)

1. `/root/recording-studio-manager/docker-compose.yml`
   - Ajout ligne 91: ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
   - Ajout ligne 92: OPENAI_API_KEY: ${OPENAI_API_KEY:-}
   - Commit: bed8b0d "fix: add Anthropic and OpenAI API keys to Docker environment"

2. PostgreSQL (via docker exec)
   - Utilisateur test créé: staff@test.com / test (id=1) dans studio_5_db

## Tests Validés

**Chatbot:**
- ✅ Localisation code (base.html, /api/ai/chat)
- ✅ Authentification et CSRF protection
- ✅ Envoi de messages via UI
- ✅ Réponse avec function calling (get_all_clients)
- ✅ Affichage statistiques (tokens, latence)

**Pages de login:**
- ✅ /client/login (subdomain) - Validation erreurs
- ✅ /login (subdomain) - Login staff avec compteur tentatives

**Redirections:**
- ✅ Subdomain / → /login
- ✅ Domaine principal / → /signup
- ✅ Navigation entre portails

**Formulaire signup:**
- ✅ Multi-étapes (Studio → Compte → Sécurité)
- ✅ Validation AJAX subdomain
- ✅ Conservation données entre étapes

## Problème Résolu (Session actuelle)

**Symptôme:** Chatbot retournait "No LLM providers available"

**Cause racine:** Variables ANTHROPIC_API_KEY et OPENAI_API_KEY présentes dans .env mais non passées au container Docker

**Solution:** Ajout des variables dans section environment de docker-compose.yml

**Validation:** Chatbot répond maintenant avec succès, utilise Claude Haiku, function calling opérationnel

## Prochaines Étapes

- [ ] Tester autres fonctions chatbot (get_sessions, create_session, etc.)
- [ ] Valider contexte multi-pages (conservation session_id)
- [ ] Tester chatbot avec plusieurs questions successives
- [ ] Documenter API chatbot dans Obsidian
- [ ] Créer utilisateurs réels (staff + client) pour tests authentification
- [ ] Tester flow signup complet (création org + tenant DB auto)
- [ ] Vérifier création automatique tenant DB lors signup

## Références

- **Mem0:** recording-studio-manager (sauvegarde: 2025-12-04 + chatbot-test-2025-12-04)
- **Serveur:** root@31.220.104.244
- **URL Test Client:** https://maraboo.recording-studio-manager.com/client/login
- **URL Test Staff:** https://maraboo.recording-studio-manager.com/login
- **URL Signup:** https://recording-studio-manager.com/signup
- **Chatbot Test User:** staff@test.com / test

## Commandes Utiles

```bash
# Vérifier logs app
ssh root@31.220.104.244 "docker logs --tail 50 studio_app"

# Recréer container après modif .env
ssh root@31.220.104.244 "cd /root/recording-studio-manager && docker compose up -d --force-recreate app"

# Tester chatbot API
curl -X POST https://maraboo.recording-studio-manager.com/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: TOKEN" \
  -d '{"message": "Question", "session_id": "test-123"}' -k

# Vérifier variables env dans container
ssh root@31.220.104.244 "docker exec studio_app env | grep ANTHROPIC"
```
