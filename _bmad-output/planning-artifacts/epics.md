---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments: ['_bmad-output/planning-artifacts/prd.md', '_bmad-output/planning-artifacts/architecture.md']
status: 'complete'
completedAt: '2026-02-21'
---

# CorniScan - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for CorniScan, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Un opérateur peut s'authentifier avec un nom d'utilisateur et un mot de passe
FR2: Un opérateur non authentifié est redirigé vers l'écran de connexion
FR3: Un opérateur est contraint de changer son mot de passe à sa première connexion
FR4: Un opérateur peut se déconnecter
FR5: L'administrateur peut consulter la liste de tous les comptes utilisateurs
FR6: L'administrateur peut créer un nouveau compte opérateur avec un mot de passe provisoire
FR7: L'administrateur peut désactiver un compte opérateur (accès révoqué immédiatement)
FR8: L'administrateur dispose d'un rôle distinct des opérateurs avec accès exclusif aux fonctions de gestion des comptes
FR9: L'opérateur peut accéder au flux caméra arrière en temps réel depuis le navigateur mobile
FR10: L'opérateur voit un indicateur temps réel confirmant la détection de la carte bancaire dans le champ caméra
FR11: L'opérateur peut cocher une checklist de qualité (joint propre + carte entièrement visible) avant la capture
FR12: L'opérateur peut déclencher la capture de la photo depuis l'écran caméra
FR13: L'écran caméra s'affiche et reste en mode portrait — le basculement en paysage est bloqué
FR14: Le système détecte la carte bancaire dans la photo et calcule le facteur d'échelle pixel/mm via homographie
FR15: Le système corrige la distorsion de perspective de la photo en utilisant les 4 coins de la carte
FR16: Le système détecte le contour extérieur du joint dans la photo corrigée en perspective
FR17: Le système calcule les dimensions (largeur × hauteur) du joint en millimètres
FR18: Le système signale une calibration insuffisante si moins de 4 coins de la carte sont détectés
FR19: L'opérateur voit le contour détecté du joint superposé sur la photo originale
FR20: L'opérateur voit les dimensions calculées du joint affichées numériquement
FR21: L'opérateur peut saisir manuellement l'épaisseur du joint en millimètres
FR22: L'opérateur voit un avertissement explicite et une action corrective si la calibration est insuffisante
FR23: L'opérateur peut choisir de recommencer la photo ou de forcer l'envoi malgré un avertissement de calibration
FR24: L'opérateur peut valider et envoyer le scan depuis l'écran de validation
FR25: Le système génère un fichier DXF R2018 représentant le contour du joint, coordonnées en millimètres à l'échelle 1:1
FR26: Le système envoie automatiquement un email vers info@cornille-sa.com avec 3 pièces jointes (DXF + PNG contour + JPEG original)
FR27: L'objet de l'email inclut automatiquement la date, l'heure, le nom de l'opérateur, les dimensions et l'épaisseur
FR28: L'opérateur reçoit une confirmation visuelle après l'envoi réussi
FR29: Un scan envoyé avec avertissement de calibration inclut un flag explicite dans le corps de l'email
FR30: L'opérateur voit un message d'erreur explicite avec action corrective en cas d'échec de traitement
FR31: L'opérateur peut recommencer un scan depuis l'écran de validation sans se reconnecter
FR32: L'opérateur voit un message explicite si la connexion réseau est absente lors de l'analyse
FR33: L'application peut être installée sur l'écran d'accueil Android via une invite d'installation native
FR34: L'application affiche un guide d'installation contextuel pour iOS à la première connexion réussie
FR35: L'application s'exécute en mode standalone (sans barre de navigation du navigateur) une fois installée

### NonFunctional Requirements

NFR-P1: Le temps entre la soumission de la photo et l'affichage du contour est inférieur à 5 secondes pour 90% des requêtes en conditions réseau normales (WiFi/4G atelier)
NFR-P2: Le First Contentful Paint est inférieur à 2 secondes sur connexion WiFi ou 4G
NFR-P3: Le bundle JavaScript initial est inférieur à 300KB compressé (gzip)
NFR-P4: L'interface reste interactive pendant le traitement backend — aucun gel de l'UI pendant l'analyse
NFR-S1: Les mots de passe sont stockés exclusivement sous forme de hash bcrypt (salt cost ≥ 12)
NFR-S2: Toutes les communications client–serveur transitent en HTTPS (TLS 1.2+)
NFR-S3: Les sessions expirent après une période d'inactivité définie (8h)
NFR-S4: Les données persistées sont limitées au strict minimum : username + hash bcrypt. Aucune photo, DXF ni métadonnée de scan stockée côté serveur
NFR-R1: L'application est disponible à plus de 99% pendant les heures ouvrées (lundi–vendredi, 7h–18h)
NFR-R2: En cas d'erreur serveur, l'application affiche un message explicite sans perdre l'état de la session ni forcer une reconnexion
NFR-R3: La perte de connexion réseau pendant le traitement n'entraîne aucune corruption ni perte de données — l'état est intégralement côté client avant soumission
NFR-I1: Tout fichier DXF généré s'ouvre sans erreur dans AutoCAD 2018+ et est directement utilisable pour découpe CNC sans manipulation préalable
NFR-I2: La conformité DXF (entités LWPOLYLINE fermées, unités mm, échelle 1:1) est vérifiée automatiquement avant l'envoi email
NFR-I3: En cas d'échec SMTP transitoire, une nouvelle tentative est effectuée avant de retourner une erreur à l'utilisateur (2 retries × 2s via Resend API)
NFR-I4: Le format de l'objet email reste stable et structuré pour permettre un traitement côté Cornille SA

### Additional Requirements

**Depuis Architecture — Starter Template (→ Epic 1 Story 1) :**
- Initialisation frontend : `npm create vue@latest corniscan-frontend` avec TypeScript, Vue Router, Pinia, ESLint+Prettier, Vitest
- Initialisation backend : `uv init corniscan-backend` + `uv add fastapi uvicorn[standard] python-multipart opencv-python-headless ezdxf python-jose[cryptography] passlib[bcrypt] sqlalchemy asyncpg alembic resend`
- Structure monorepo : `corniscan/frontend/` + `corniscan/backend/`

**Depuis Architecture — Infrastructure & Setup :**
- Base de données : Neon PostgreSQL free tier — 1 table `users` (id, username, hashed_password, role, force_password_change, created_at)
- Migrations : Alembic, exécuté au démarrage Render via lifespan event
- Variables d'environnement Render : `DATABASE_URL`, `JWT_SECRET`, `RESEND_API_KEY`
- Vite proxy dev : `/api/* → http://localhost:8000` dans `vite.config.ts`

**Depuis Architecture — Patterns techniques à respecter :**
- Endpoints OpenCV (`/scan/process`, `/scan/detect-card`) déclarés `def` synchrone (pas `async def`) — thread pool Uvicorn
- Tous les appels HTTP frontend passent par `apiClient.ts` (centralisé, injecte JWT)
- Pattern isLoading + error dans chaque store Pinia
- snake_case JSON/BD, PascalCase composants Vue

**Depuis Architecture — Intégrations externes :**
- Email : Resend API (SDK Python `resend`), 3 000 emails/mois gratuits
- Hébergement : Render Starter — FastAPI sert `frontend/dist/` via StaticFiles + fallback SPA
- PWA : `vite-plugin-pwa` + Workbox, ajouté post-init frontend

### FR Coverage Map

FR1: Epic 1 — Authentification (login avec username/password)
FR2: Epic 1 — Authentification (redirection si non authentifié)
FR3: Epic 1 — Authentification (changement mot de passe forcé premier login)
FR4: Epic 1 — Authentification (déconnexion)
FR5: Epic 2 — Administration (liste des comptes)
FR6: Epic 2 — Administration (création compte opérateur)
FR7: Epic 2 — Administration (désactivation compte)
FR8: Epic 2 — Administration (rôle admin distinct)
FR9: Epic 3 — Capture (accès flux caméra arrière)
FR10: Epic 3 — Capture (indicateur temps réel détection carte)
FR11: Epic 3 — Capture (checklist qualité)
FR12: Epic 3 — Capture (déclencheur capture)
FR13: Epic 3 — Capture (portrait imposé)
FR14: Epic 4 — Traitement (détection carte + homographie pixel/mm)
FR15: Epic 4 — Traitement (correction perspective 4 coins)
FR16: Epic 4 — Traitement (détection contour joint)
FR17: Epic 4 — Traitement (calcul dimensions mm)
FR18: Epic 4 — Traitement (signal calibration insuffisante < 4 coins)
FR19: Epic 4 — Validation (contour superposé sur photo)
FR20: Epic 4 — Validation (dimensions affichées numériquement)
FR21: Epic 4 — Validation (saisie épaisseur manuelle)
FR22: Epic 4 — Validation (avertissement calibration insuffisante)
FR23: Epic 4 — Validation (choix retry ou envoi forcé)
FR24: Epic 4 — Validation (valider et envoyer)
FR25: Epic 5 — Livraison (génération DXF R2018)
FR26: Epic 5 — Livraison (email triple pièce jointe)
FR27: Epic 5 — Livraison (objet email structuré)
FR28: Epic 5 — Livraison (confirmation visuelle envoi)
FR29: Epic 5 — Livraison (flag calibration dans email)
FR30: Epic 4 — Erreurs (message erreur avec action corrective)
FR31: Epic 4 — Erreurs (retry sans re-login)
FR32: Epic 4 — Erreurs (message réseau absent)
FR33: Epic 6 — PWA (installation Android invite native)
FR34: Epic 6 — PWA (guide installation iOS)
FR35: Epic 6 — PWA (mode standalone)

## Epic List

### Epic 1: Fondation technique et authentification

Les opérateurs peuvent accéder à CorniScan de façon sécurisée depuis un navigateur mobile ou desktop. Le système est déployé sur Render, la base de données est opérationnelle, et la gestion du premier login (changement de mot de passe forcé) est en place.
**FRs couverts :** FR1, FR2, FR3, FR4
**NFRs embarqués :** NFR-S1 (bcrypt ≥ 12), NFR-S2 (HTTPS), NFR-S3 (session 8h), NFR-P2 (FCP < 2s), NFR-P3 (bundle < 300KB), NFR-R1 (uptime > 99%)
**Inclut :** setup projet (create-vue + uv init), Neon PostgreSQL + Alembic, déploiement Render initial

### Epic 2: Gestion des comptes opérateurs

L'administrateur peut contrôler qui a accès à CorniScan : consulter la liste des comptes, créer un nouveau compte opérateur avec mot de passe provisoire, et désactiver un compte révoquant l'accès immédiatement.
**FRs couverts :** FR5, FR6, FR7, FR8

### Epic 3: Capture guidée d'un joint

L'opérateur peut photographier un joint depuis l'écran caméra avec guidage temps réel : indicateur de détection de la carte bancaire, checklist qualité, et orientation portrait imposée — garantissant une photo exploitable avant même de soumettre.
**FRs couverts :** FR9, FR10, FR11, FR12, FR13

### Epic 4: Traitement du scan et validation

La photo soumise est analysée par le backend (homographie carte → correction perspective → détection contour → calcul dimensions), et l'opérateur voit le résultat superposé pour validation. Il peut recommencer, forcer l'envoi malgré un avertissement de calibration, ou saisir l'épaisseur. Les erreurs de traitement et de réseau sont gérées avec messages actionnables.
**FRs couverts :** FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR24, FR30, FR31, FR32
**NFRs embarqués :** NFR-P1 (< 5s), NFR-P4 (UI non gelée), NFR-S4 (stateless), NFR-R2 (erreur sans perte état), NFR-R3 (pas de corruption)

### Epic 5: Génération DXF et livraison email

Après validation, le système génère automatiquement le fichier DXF R2018, envoie l'email vers info@cornille-sa.com avec les 3 pièces jointes (DXF + PNG contour + JPEG original), et confirme visuellement à l'opérateur. Les scans avec avertissement de calibration incluent un flag explicite dans l'email.
**FRs couverts :** FR25, FR26, FR27, FR28, FR29
**NFRs embarqués :** NFR-I1 (DXF AutoCAD 2018+), NFR-I2 (DXF valide avant envoi), NFR-I3 (retry email 2×), NFR-I4 (format email stable)

### Epic 6: PWA et installation mobile

L'application peut être installée sur l'écran d'accueil Android via invite native et sur iOS via guide contextuel affiché au premier login. Une fois installée, elle s'exécute en mode standalone sans barre de navigation du navigateur.
**FRs couverts :** FR33, FR34, FR35

---

## Epic 1: Fondation technique et authentification

Les opérateurs peuvent accéder à CorniScan de façon sécurisée depuis un navigateur mobile ou desktop. Le système est déployé sur Render, la base de données est opérationnelle, et la gestion du premier login (changement de mot de passe forcé) est en place.

### Story 1.1: Initialisation du projet et déploiement de base

As a développeur,
I want initialiser le monorepo CorniScan (frontend Vue 3 + backend FastAPI) et le déployer sur Render,
So that une URL publique est disponible et l'équipe peut commencer le développement sur une base stable et reproductible.

**Acceptance Criteria:**

**Given** un poste de développement avec Node.js 20+, Python 3.11+, uv et git installés
**When** les commandes d'initialisation sont exécutées (`npm create vue@latest corniscan-frontend` avec TypeScript, Vue Router, Pinia, ESLint+Prettier, Vitest + `uv init corniscan-backend` + dépendances backend)
**Then** la structure monorepo `corniscan/frontend/` + `corniscan/backend/` est créée et les deux projets démarrent localement sans erreur

**Given** le proxy Vite est configuré (`/api/* → http://localhost:8000` dans `vite.config.ts`)
**When** le développeur exécute `npm run dev` en frontend et `uvicorn main:app --reload` en backend
**Then** les appels API depuis le frontend en dev atteignent le backend sans erreur CORS

**Given** le projet est poussé sur GitHub et un service Render Web Service est configuré (build: `cd frontend && npm run build`, start: `uvicorn main:app`)
**When** Render déclenche un déploiement
**Then** FastAPI sert le `frontend/dist/` via `StaticFiles` avec fallback SPA, et l'URL Render renvoie l'application Vue en HTTP 200

**Given** l'application est déployée sur Render
**When** un navigateur accède à l'URL publique depuis un réseau WiFi ou 4G
**Then** le First Contentful Paint est inférieur à 2 secondes (NFR-P2) et le bundle JS initial est inférieur à 300KB compressé gzip (NFR-P3)

### Story 1.2: Base de données et table utilisateurs

As a développeur,
I want provisionner la base de données PostgreSQL Neon et créer la table `users` via Alembic,
So that le système peut persister les comptes utilisateurs de façon sécurisée dès le premier démarrage.

**Acceptance Criteria:**

**Given** un compte Neon free tier est créé et la `DATABASE_URL` est configurée dans les variables d'environnement Render
**When** l'application FastAPI démarre (via lifespan event)
**Then** Alembic exécute automatiquement les migrations en attente sans erreur, sans intervention manuelle

**Given** la migration initiale est appliquée
**When** on inspecte la base de données
**Then** la table `users` existe avec les colonnes : `id` (UUID), `username` (VARCHAR unique), `hashed_password` (VARCHAR), `role` (ENUM : 'operator'/'admin'), `force_password_change` (BOOLEAN, défaut TRUE), `created_at` (TIMESTAMP)
**And** aucune autre table ni colonne n'est créée (NFR-S4 — données minimales)

**Given** un mot de passe en clair est fourni lors de la création ou mise à jour d'un compte
**When** le système le persiste en base
**Then** seul le hash bcrypt (salt cost ≥ 12) est stocké — jamais le mot de passe en clair (NFR-S1)

**Given** les migrations sont appliquées et la base est vide
**When** un seed de bootstrap est exécuté
**Then** un compte admin par défaut existe (`admin` / mot de passe provisoire documenté) avec `role='admin'` et `force_password_change=true`

### Story 1.3: Authentification — login, session JWT et logout

As an opérateur,
I want me connecter avec mon nom d'utilisateur et mon mot de passe et me déconnecter,
So that j'accède à l'application de façon sécurisée et peux terminer ma session proprement.

**Acceptance Criteria:**

**Given** un opérateur non authentifié tente d'accéder à n'importe quelle route protégée
**When** le router Vue évalue la navigation
**Then** il est redirigé vers `/login` avant d'atteindre la page demandée (FR2)

**Given** un opérateur est sur l'écran de connexion
**When** il saisit un username et un mot de passe valides et soumet le formulaire
**Then** le backend vérifie les credentials via bcrypt, génère un JWT HS256 (durée 8h), le frontend stocke le token dans `localStorage`, et l'opérateur est redirigé vers la route principale (FR1)

**Given** un opérateur soumet des credentials invalides (username inconnu ou mot de passe erroné)
**When** le backend retourne HTTP 401
**Then** un message d'erreur explicite s'affiche dans l'interface ("Identifiant ou mot de passe incorrect") sans révéler lequel des deux est erroné

**Given** un opérateur est authentifié et effectue des appels API via `apiClient.ts`
**When** le frontend envoie une requête HTTP
**Then** le header `Authorization: Bearer <token>` est automatiquement injecté dans chaque requête

**Given** un opérateur est authentifié depuis plus de 8 heures sans activité
**When** il tente une action nécessitant le backend
**Then** le token JWT est expiré, le backend retourne HTTP 401, et le frontend redirige vers `/login` (NFR-S3)

**Given** un opérateur authentifié clique sur "Se déconnecter"
**When** l'action de logout est déclenchée
**Then** le token JWT est supprimé du `localStorage`, le store Pinia est réinitialisé, et l'opérateur est redirigé vers `/login` (FR4)

### Story 1.4: Changement de mot de passe au premier login

As an opérateur,
I want être contraint de changer mon mot de passe provisoire lors de ma première connexion,
So that mon accès est immédiatement sécurisé avec un mot de passe que je suis le seul à connaître.

**Acceptance Criteria:**

**Given** un opérateur se connecte avec succès et que `force_password_change = true` sur son compte
**When** le JWT est émis et le frontend reçoit la réponse
**Then** il est automatiquement redirigé vers l'écran de changement de mot de passe — aucune autre route n'est accessible (FR3)

**Given** un opérateur est sur l'écran de changement de mot de passe forcé et tente de naviguer vers une autre route
**When** le router Vue évalue la navigation
**Then** il est redirigé de force vers l'écran de changement de mot de passe

**Given** un opérateur saisit un nouveau mot de passe et sa confirmation, et les deux correspondent
**When** il soumet le formulaire
**Then** le nouveau mot de passe est haché (bcrypt ≥ 12) et persisté en base, `force_password_change` est mis à `false`, et il est redirigé vers la route principale

**Given** un opérateur soumet un nouveau mot de passe identique au mot de passe provisoire actuel
**When** le backend reçoit la requête
**Then** une erreur explicite est retournée ("Le nouveau mot de passe doit être différent de l'ancien") et le changement est refusé

**Given** un opérateur saisit un nouveau mot de passe et une confirmation qui ne correspondent pas
**When** le formulaire est soumis
**Then** une erreur de validation s'affiche côté frontend ("Les mots de passe ne correspondent pas") sans appel au backend

---

## Epic 2: Gestion des comptes opérateurs

L'administrateur peut contrôler qui a accès à CorniScan : consulter la liste des comptes, créer un nouveau compte opérateur avec mot de passe provisoire, et désactiver un compte révoquant l'accès immédiatement.

### Story 2.1: Consultation de la liste des comptes utilisateurs

As an administrateur,
I want consulter la liste de tous les comptes utilisateurs,
So that j'ai une vue d'ensemble des accès à l'application et peux identifier rapidement les comptes à gérer.

**Acceptance Criteria:**

**Given** un administrateur est authentifié et navigue vers la section de gestion des comptes
**When** la page se charge
**Then** la liste de tous les comptes utilisateurs s'affiche avec pour chaque compte : username, rôle, statut (actif/inactif), date de création, et indicateur de changement de mot de passe en attente (FR5)

**Given** la liste est affichée
**When** l'administrateur la consulte
**Then** son propre compte admin apparaît dans la liste avec le rôle 'admin' clairement identifié

**Given** un opérateur (rôle 'operator') est authentifié
**When** il tente d'accéder à la page de gestion des comptes
**Then** il est redirigé et reçoit un message lui indiquant qu'il n'a pas les droits nécessaires

### Story 2.2: Création d'un compte opérateur avec mot de passe provisoire

As an administrateur,
I want créer un nouveau compte opérateur avec un mot de passe provisoire,
So that je peux donner accès à l'application à un nouvel opérateur sans intervention technique.

**Acceptance Criteria:**

**Given** un administrateur est sur la page de gestion des comptes
**When** il remplit le formulaire de création (username + mot de passe provisoire) et soumet
**Then** un compte est créé en base avec `role='operator'`, `force_password_change=true`, mot de passe haché bcrypt (≥ 12) (FR6)
**And** le nouveau compte apparaît immédiatement dans la liste des comptes

**Given** un compte opérateur vient d'être créé avec un mot de passe provisoire
**When** le nouvel opérateur se connecte avec ces credentials
**Then** l'authentification réussit et il est redirigé vers l'écran de changement de mot de passe forcé (lien avec Story 1.4)

**Given** un administrateur tente de créer un compte avec un username déjà existant
**When** le formulaire est soumis
**Then** le backend retourne une erreur explicite ("Ce nom d'utilisateur existe déjà") et aucun compte n'est créé

**Given** un administrateur soumet le formulaire de création avec des champs vides ou invalides
**When** la validation s'exécute
**Then** des messages d'erreur explicites s'affichent par champ et la soumission est bloquée côté frontend

### Story 2.3: Désactivation d'un compte opérateur

As an administrateur,
I want désactiver un compte opérateur,
So that je peux révoquer immédiatement l'accès d'un opérateur sans supprimer son historique.

**Acceptance Criteria:**

**Given** un administrateur clique sur "Désactiver" sur un compte opérateur actif
**When** l'action est confirmée et soumise
**Then** le compte est marqué comme inactif en base et son statut est mis à jour dans la liste (FR7)

**Given** un compte opérateur vient d'être désactivé
**When** cet opérateur tente de se connecter avec ses credentials
**Then** le backend retourne HTTP 401 avec un message explicite ("Ce compte a été désactivé. Contactez votre administrateur.")

**Given** un opérateur possède une session JWT active et son compte est désactivé par l'administrateur
**When** il effectue la prochaine requête API
**Then** le backend vérifie le statut du compte, retourne HTTP 401, et le frontend redirige vers `/login`

**Given** un administrateur tente de désactiver son propre compte admin
**When** l'action est soumise
**Then** le backend retourne une erreur explicite ("Impossible de désactiver votre propre compte") et le compte reste actif

### Story 2.4: Protection des routes admin et séparation des rôles

As an administrateur,
I want que les fonctions de gestion des comptes soient exclusivement accessibles aux administrateurs,
So that la séparation des rôles est garantie et les opérateurs ne peuvent pas accéder aux fonctions sensibles.

**Acceptance Criteria:**

**Given** un opérateur authentifié (rôle 'operator') tente d'accéder à une route frontend `/admin/*`
**When** le router Vue évalue la navigation
**Then** il est redirigé vers sa route principale et un message lui indique l'accès refusé (FR8)

**Given** le backend reçoit une requête vers un endpoint d'administration (`/api/v1/admin/*`) avec un JWT de rôle 'operator'
**When** le middleware d'autorisation évalue le token
**Then** HTTP 403 est retourné, quelle que soit la validité du token JWT

**Given** un administrateur est authentifié
**When** il accède à la section administration
**Then** il voit l'interface complète de gestion des comptes (liste, création, désactivation)

**Given** un opérateur est authentifié
**When** il consulte la navigation de l'application
**Then** aucun lien ou élément d'interface menant aux fonctions admin n'est visible dans son menu

---

## Epic 3: Capture guidée d'un joint

L'opérateur peut photographier un joint depuis l'écran caméra avec guidage temps réel : indicateur de détection de la carte bancaire, checklist qualité, et orientation portrait imposée — garantissant une photo exploitable avant même de soumettre.

### Story 3.1: Accès au flux caméra arrière en mode portrait

As an opérateur,
I want accéder au flux caméra arrière de mon mobile en temps réel depuis le navigateur,
So that je peux cadrer le joint à photographier directement depuis l'application.

**Acceptance Criteria:**

**Given** un opérateur authentifié navigue vers l'écran caméra
**When** la page se charge
**Then** le flux de la caméra arrière s'affiche via `getUserMedia` avec `facingMode: 'environment'`, plein écran, en orientation portrait (FR9)

**Given** le flux caméra est actif et l'opérateur bascule le téléphone en mode paysage
**When** le changement d'orientation est détecté
**Then** l'interface reste verrouillée en portrait — le flux caméra ne pivote pas (FR13)

**Given** le navigateur ne supporte pas `getUserMedia` ou l'opérateur refuse la permission caméra
**When** la page tente d'accéder à la caméra
**Then** un message d'erreur explicite s'affiche avec une action corrective ("Autorisez l'accès à la caméra dans les paramètres de votre navigateur")

**Given** le flux caméra est actif
**When** l'opérateur utilise l'application
**Then** aucune barre de navigation du navigateur n'est visible (mode plein écran PWA ou scroll masqué)

### Story 3.2: Détection temps réel de la carte bancaire dans le flux

As an opérateur,
I want voir un indicateur en temps réel me confirmant que ma carte bancaire est bien détectée dans le champ de la caméra,
So that je sais que la calibration sera possible avant de déclencher la capture.

**Acceptance Criteria:**

**Given** le flux caméra est actif
**When** un intervalle de 500ms s'écoule
**Then** une frame est capturée depuis le flux via `canvas.toBlob()` et envoyée en POST à `/scan/detect-card`

**Given** le backend détecte la carte bancaire (4 coins visibles) dans la frame reçue
**When** la réponse est retournée
**Then** un indicateur visuel vert s'affiche sur l'écran caméra confirmant la détection ("Carte détectée ✓") (FR10)

**Given** le backend ne détecte pas la carte ou détecte moins de 4 coins
**When** la réponse est retournée
**Then** l'indicateur affiche un état d'avertissement ("Carte non détectée — repositionnez-la dans le cadre")

**Given** la détection périodique est active
**When** les appels se succèdent à 500ms d'intervalle
**Then** l'interface reste fluide et interactive — aucun gel de l'UI pendant les appels réseau (NFR-P4)

### Story 3.3: Checklist qualité avant capture

As an opérateur,
I want cocher une checklist de qualité avant de déclencher la capture,
So that je m'assure consciemment que les conditions sont optimales avant de soumettre la photo au traitement.

**Acceptance Criteria:**

**Given** l'écran caméra est affiché
**When** l'opérateur le consulte
**Then** une checklist avec 2 cases à cocher est visible : "Joint propre" et "Carte entièrement visible" (FR11)

**Given** au moins une case de la checklist est non cochée
**When** l'opérateur tente de déclencher la capture
**Then** le bouton de capture est désactivé (visuellement grisé) et ne répond pas au tap

**Given** l'opérateur coche les 2 cases de la checklist
**When** toutes les cases sont cochées
**Then** le bouton de capture devient actif et cliquable

**Given** l'opérateur décoche une case précédemment cochée
**When** ce changement d'état se produit
**Then** le bouton de capture redevient immédiatement désactivé

### Story 3.4: Déclenchement et capture de la photo

As an opérateur,
I want déclencher la capture de la photo depuis l'écran caméra,
So that je peux soumettre l'image du joint au système d'analyse.

**Acceptance Criteria:**

**Given** les 2 cases de la checklist sont cochées et le bouton de capture est actif
**When** l'opérateur appuie sur le bouton de capture
**Then** une image fixe est capturée depuis le flux caméra via `canvas.toBlob()` au format JPEG (FR12)
**And** le flux caméra s'arrête et l'image capturée s'affiche en aperçu

**Given** la photo est capturée
**When** la capture est confirmée
**Then** l'opérateur est automatiquement redirigé vers l'écran d'analyse avec l'image transmise en état de navigation

**Given** la photo est capturée en mode portrait
**When** l'image est exploitée par le backend
**Then** l'orientation est correcte indépendamment des métadonnées EXIF du device

---

## Epic 4: Traitement du scan et validation

La photo soumise est analysée par le backend (homographie carte → correction perspective → détection contour → calcul dimensions), et l'opérateur voit le résultat superposé pour validation. Il peut recommencer, forcer l'envoi malgré un avertissement de calibration, ou saisir l'épaisseur. Les erreurs de traitement et de réseau sont gérées avec messages actionnables.

### Story 4.1: Soumission de la photo et pipeline d'analyse backend

As an opérateur,
I want soumettre la photo capturée pour analyse,
So that le système détecte automatiquement la carte bancaire, corrige la perspective, détecte le contour du joint et calcule ses dimensions en millimètres.

**Acceptance Criteria:**

**Given** une photo JPEG est soumise à `POST /scan/process`
**When** le backend reçoit la requête
**Then** il exécute séquentiellement : détection de la carte + homographie pixel/mm via les 4 coins (FR14), correction de la distorsion de perspective (FR15), détection du contour extérieur du joint sur l'image corrigée (FR16), calcul des dimensions largeur × hauteur en mm (FR17)

**Given** le backend complète l'analyse avec succès
**When** la réponse est retournée au frontend
**Then** elle contient : les coordonnées du contour du joint, les dimensions (largeur × hauteur en mm), et le statut de calibration

**Given** la détection de la carte identifie moins de 4 coins
**When** l'analyse s'exécute
**Then** la réponse inclut `calibration_warning: true` et l'analyse se poursuit dans la mesure du possible (FR18)

**Given** une photo est soumise sur un réseau WiFi ou 4G atelier
**When** le backend traite la requête
**Then** la réponse est retournée en moins de 5 secondes pour 90% des requêtes (NFR-P1)

**Given** l'analyse est en cours
**When** l'endpoint `/scan/process` exécute le traitement OpenCV
**Then** l'endpoint est déclaré `def` (synchrone) et s'exécute dans le thread pool Uvicorn — aucune photo ni métadonnée n'est persistée côté serveur (NFR-S4)

**Given** la soumission est en cours côté frontend
**When** l'utilisateur attend la réponse
**Then** un indicateur de chargement est visible et l'interface reste interactive — aucun gel de l'UI (NFR-P4)

### Story 4.2: Affichage du résultat — contour superposé et dimensions

As an opérateur,
I want voir le contour détecté du joint superposé sur la photo originale ainsi que les dimensions calculées numériquement,
So that je peux valider visuellement que l'analyse correspond bien au joint photographié.

**Acceptance Criteria:**

**Given** le backend retourne un résultat d'analyse réussi
**When** l'écran de validation s'affiche
**Then** le contour détecté du joint est dessiné en surimpression sur la photo originale (FR19)

**Given** le contour est affiché en superposition
**When** l'opérateur le compare visuellement à la photo
**Then** il trace fidèlement le contour extérieur du joint visible dans l'image

**Given** les dimensions sont calculées
**When** l'écran de validation s'affiche
**Then** la largeur et la hauteur du joint sont affichées numériquement en millimètres avec 1 décimale de précision (FR20)

**Given** `calibration_warning` est `false`
**When** le résultat est affiché
**Then** aucun avertissement n'est visible et l'interface est en état de validation normal

### Story 4.3: Saisie de l'épaisseur et gestion de l'avertissement de calibration

As an opérateur,
I want saisir manuellement l'épaisseur du joint et être informé clairement en cas de calibration insuffisante,
So that je fournis une information complète et peux décider de la suite si la détection est incomplète.

**Acceptance Criteria:**

**Given** l'écran de validation est affiché
**When** l'opérateur le consulte
**Then** un champ de saisie numérique pour l'épaisseur du joint (en mm) est visible et éditable (FR21)

**Given** `calibration_warning` est `true` (moins de 4 coins de la carte détectés)
**When** l'écran de validation s'affiche
**Then** un avertissement explicite s'affiche avec la cause et une action corrective : "Calibration insuffisante — moins de 4 coins de la carte détectés. Recommencez avec la carte entièrement visible." (FR22)

**Given** l'avertissement de calibration est affiché
**When** l'opérateur choisit une action
**Then** deux options explicites lui sont proposées : "Recommencer la photo" et "Forcer l'envoi malgré l'avertissement" (FR23)

**Given** l'opérateur sélectionne "Recommencer la photo"
**When** l'action est déclenchée
**Then** il est redirigé vers l'écran caméra avec l'état de capture réinitialisé

**Given** `calibration_warning` est `false`
**When** le résultat est affiché
**Then** aucun avertissement et aucune option "Forcer l'envoi" ne sont visibles

### Story 4.4: Gestion des erreurs de traitement et de réseau

As an opérateur,
I want recevoir des messages d'erreur explicites avec des actions correctives en cas d'échec de traitement ou d'absence de réseau,
So that je sais toujours quoi faire pour continuer sans perdre ma session ni mes données.

**Acceptance Criteria:**

**Given** le backend retourne une erreur lors du traitement (HTTP 500 ou résultat inattendu)
**When** le frontend reçoit la réponse
**Then** un message explicite s'affiche avec une action corrective : "Une erreur est survenue lors de l'analyse. Recommencez la photo." (FR30)

**Given** le device n'a pas de connexion réseau au moment de la soumission de la photo
**When** la tentative de soumission est effectuée
**Then** un message spécifique s'affiche : "Connexion réseau absente. Vérifiez votre WiFi ou 4G avant de réessayer." (FR32)

**Given** une erreur survient pendant le traitement
**When** le message d'erreur est affiché
**Then** l'opérateur peut réessayer depuis l'écran de validation sans être redirigé vers `/login` (FR31)

**Given** une erreur réseau survient pendant la soumission
**When** la session de l'opérateur est toujours active
**Then** aucune perte de données ne survient — l'image capturée reste en mémoire et l'état de la session est intégralement préservé côté client (NFR-R3)

**Given** une erreur serveur se produit
**When** le message est affiché à l'opérateur
**Then** la session reste active — aucune déconnexion forcée ne survient (NFR-R2)

### Story 4.5: Validation finale et déclenchement de l'envoi

As an opérateur,
I want valider et envoyer le scan depuis l'écran de validation,
So that le dossier complet est transmis au pipeline de génération DXF et d'envoi email.

**Acceptance Criteria:**

**Given** l'opérateur a vérifié le contour, saisi l'épaisseur, et est satisfait du résultat
**When** il clique sur "Valider et envoyer"
**Then** le payload complet (image JPEG + coordonnées du contour + dimensions + épaisseur + `calibration_warning`) est soumis au backend pour livraison (FR24)

**Given** `calibration_warning` est `true` et l'opérateur a choisi "Forcer l'envoi"
**When** il clique sur "Valider et envoyer"
**Then** le flag `calibration_warning: true` est inclus dans le payload transmis au backend

**Given** la soumission est en cours
**When** la requête est envoyée
**Then** l'interface affiche un état de chargement et reste interactive — aucun double-envoi n'est possible (bouton désactivé pendant le traitement)

**Given** la soumission aboutit avec succès
**When** le backend confirme la réception
**Then** l'opérateur est redirigé vers un écran de confirmation (couvert par Epic 5 — FR28)

---

## Epic 5: Génération DXF et livraison email

Après validation, le système génère automatiquement le fichier DXF R2018, envoie l'email vers info@cornille-sa.com avec les 3 pièces jointes (DXF + PNG contour + JPEG original), et confirme visuellement à l'opérateur. Les scans avec avertissement de calibration incluent un flag explicite dans l'email.

### Story 5.1: Génération du fichier DXF R2018 conforme AutoCAD

As a système,
I want générer un fichier DXF R2018 représentant le contour du joint à l'échelle 1:1 en millimètres,
So that le fichier est directement utilisable pour découpe CNC dans AutoCAD 2018+ sans manipulation préalable.

**Acceptance Criteria:**

**Given** les coordonnées du contour et les dimensions en mm sont reçues par le backend après validation
**When** la génération DXF s'exécute via `ezdxf`
**Then** un fichier DXF R2018 est produit contenant une entité `LWPOLYLINE` fermée représentant le contour extérieur du joint (FR25)

**Given** le fichier DXF est généré
**When** on inspecte son contenu
**Then** les coordonnées sont exprimées en millimètres à l'échelle 1:1, les unités DXF sont configurées en mm (NFR-I1)

**Given** le fichier DXF est généré
**When** la validation automatique s'exécute avant l'envoi
**Then** il est vérifié que : la `LWPOLYLINE` est fermée (`is_closed=True`), les unités sont en mm, l'échelle est 1:1 (NFR-I2)

**Given** la validation DXF échoue (entité non fermée ou unités incorrectes)
**When** le problème est détecté
**Then** une erreur est retournée au frontend avant toute tentative d'envoi email

**Given** le fichier DXF passe la validation
**When** il est prêt pour l'envoi
**Then** il est conservé en mémoire (bytes) — aucun fichier n'est écrit sur le disque serveur (NFR-S4)

### Story 5.2: Envoi email avec les 3 pièces jointes

As a système,
I want envoyer automatiquement un email vers info@cornille-sa.com avec les 3 pièces jointes et un objet structuré,
So that Cornille SA reçoit le dossier complet du scan avec toutes les informations nécessaires pour la découpe.

**Acceptance Criteria:**

**Given** la validation DXF est passée et toutes les données sont prêtes
**When** l'envoi email est déclenché via le SDK Resend
**Then** un email est envoyé à `info@cornille-sa.com` avec 3 pièces jointes : fichier DXF + PNG contour superposé + JPEG original (FR26)

**Given** l'email est composé
**When** l'objet est défini
**Then** il suit le format structuré : `[CorniScan] YYYY-MM-DD HH:MM — <nom_opérateur> — <largeur>×<hauteur>mm — ép.<épaisseur>mm`, stable pour traitement côté Cornille SA (FR27, NFR-I4)

**Given** `calibration_warning` est `true`
**When** le corps de l'email est composé
**Then** un flag explicite est inclus dans le corps : "⚠️ AVERTISSEMENT : scan envoyé malgré une calibration insuffisante (moins de 4 coins de la carte détectés)" (FR29)

**Given** l'appel à l'API Resend échoue lors de la première tentative
**When** l'erreur est reçue
**Then** 2 nouvelles tentatives sont effectuées avec 2 secondes d'intervalle avant de retourner une erreur à l'utilisateur (NFR-I3)

**Given** l'email est envoyé avec succès
**When** l'envoi est confirmé par l'API Resend
**Then** aucun fichier (DXF, PNG, JPEG) n'est conservé sur le serveur après l'envoi (NFR-S4)

### Story 5.3: Confirmation visuelle après envoi réussi

As an opérateur,
I want recevoir une confirmation visuelle après l'envoi réussi du scan,
So that je sais que le dossier a bien été transmis à Cornille SA et peux commencer un nouveau scan.

**Acceptance Criteria:**

**Given** l'email a été envoyé avec succès
**When** le backend confirme au frontend
**Then** un écran de confirmation s'affiche avec un message de succès explicite (FR28)

**Given** l'écran de confirmation est affiché
**When** l'opérateur le consulte
**Then** il indique : l'envoi réussi, le destinataire (`info@cornille-sa.com`), et un récapitulatif des dimensions et de l'épaisseur du scan envoyé

**Given** l'opérateur souhaite scanner un autre joint
**When** il est sur l'écran de confirmation
**Then** un bouton "Nouveau scan" est visible et le redirige vers l'écran caméra sans nécessiter de reconnexion

**Given** l'envoi email échoue après toutes les tentatives (2 retries épuisés)
**When** l'erreur remonte au frontend
**Then** un message d'erreur explicite s'affiche avec action corrective ("L'envoi a échoué. Vérifiez votre connexion et réessayez.") et le bouton de renvoi reste disponible

---

## Epic 6: PWA et installation mobile

L'application peut être installée sur l'écran d'accueil Android via invite native et sur iOS via guide contextuel affiché au premier login. Une fois installée, elle s'exécute en mode standalone sans barre de navigation du navigateur.

### Story 6.1: Configuration PWA et mode standalone

As a développeur,
I want configurer l'application comme une PWA avec `vite-plugin-pwa` et Workbox,
So that l'application peut être installée sur l'écran d'accueil et s'exécute en mode standalone sans barre de navigation du navigateur.

**Acceptance Criteria:**

**Given** `vite-plugin-pwa` est ajouté et configuré dans `vite.config.ts`
**When** l'application est buildée
**Then** un Web App Manifest valide est généré avec : `name`, `short_name`, `display: 'standalone'`, `orientation: 'portrait'`, icônes (192px + 512px), `theme_color`, `background_color`

**Given** le manifest PWA est en place et l'application est servie en HTTPS
**When** un opérateur installe l'application et l'ouvre depuis l'écran d'accueil
**Then** elle s'exécute en mode standalone sans barre de navigation du navigateur (FR35)

**Given** le service worker est enregistré via Workbox
**When** l'application se charge
**Then** les assets statiques (JS, CSS, icônes) sont précachés pour permettre l'accès au shell applicatif même en cas de réseau dégradé

**Given** l'application s'exécute en mode standalone
**When** l'orientation du device est vérifiée
**Then** le mode portrait est maintenu de façon cohérente avec FR13

### Story 6.2: Invite d'installation native Android

As an opérateur Android,
I want recevoir une invite native pour installer l'application sur mon écran d'accueil,
So that j'accède à CorniScan directement depuis mon écran d'accueil sans passer par le navigateur.

**Acceptance Criteria:**

**Given** l'opérateur utilise Chrome sur Android et les critères PWA sont remplis (HTTPS + service worker actif + manifest valide)
**When** le navigateur détermine que l'application est installable
**Then** l'invite native "Ajouter à l'écran d'accueil" apparaît automatiquement (FR33)

**Given** l'événement `beforeinstallprompt` est capturé par le frontend
**When** l'opérateur est sur l'écran principal après login
**Then** l'application peut contrôler le moment d'affichage de l'invite pour une expérience optimale

**Given** l'opérateur a ignoré l'invite initiale
**When** il souhaite installer l'application plus tard
**Then** l'application reste installable via le menu du navigateur Chrome

**Given** l'application est installée depuis l'écran d'accueil Android
**When** l'opérateur la lance
**Then** elle démarre en mode standalone sans barre de navigation Chrome (FR35 confirmé)

### Story 6.3: Guide d'installation contextuel iOS au premier login

As an opérateur iOS,
I want voir un guide d'installation contextuel lors de ma première connexion réussie sur Safari iOS,
So that je sais comment installer CorniScan sur mon écran d'accueil malgré l'absence d'invite native sur iOS.

**Acceptance Criteria:**

**Given** un opérateur se connecte avec succès pour la première fois depuis Safari sur iOS (détecté via `navigator.userAgent`)
**When** la connexion est validée et que l'application n'est pas déjà en mode standalone (`window.matchMedia('(display-mode: standalone)')`)
**Then** un guide d'installation contextuel s'affiche expliquant : appuyer sur l'icône Partager → "Sur l'écran d'accueil" (FR34)

**Given** le guide est affiché
**When** l'opérateur le consulte
**Then** il présente les instructions spécifiques iOS avec les icônes visuels du bouton Partager et de l'option "Sur l'écran d'accueil"

**Given** l'opérateur a déjà vu et fermé le guide iOS
**When** il se connecte lors des sessions suivantes
**Then** le guide ne s'affiche plus (état persisté dans `localStorage`)

**Given** l'opérateur accède à l'application depuis un device non-iOS, depuis un navigateur autre que Safari, ou depuis l'application déjà installée en mode standalone
**When** la connexion est validée
**Then** le guide d'installation iOS n'est pas affiché
