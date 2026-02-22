---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish']
inputDocuments: ['_bmad-output/brainstorming/brainstorming-session-2026-02-19.md', '_bmad-output/planning-artifacts/research/technical-CorniScan-stack-research-2026-02-21.md']
workflowType: 'prd'
classification:
  projectType: web_app
  domain: general_industrial
  complexity: medium
  projectContext: greenfield
---

# Product Requirements Document - CorniScan

**Author:** Léo
**Date:** 2026-02-21

## Executive Summary

CorniScan est une web application industrielle destinée aux employés de Cornille SA. Elle convertit la photo d'un joint d'étanchéité — prise avec un smartphone standard — en fichier DXF exploitable en CAO, envoyé automatiquement par email. Le workflow complet se déroule en 3 gestes (poser, photographier, recevoir) et compresse un processus de quelques minutes à plusieurs heures en une opération de 2 minutes, sans matériel supplémentaire, sans formation technique, sans expertise CAO côté opérateur.

**Utilisateurs cibles :** Employés de Cornille SA (opérateurs d'atelier, ~5–10 utilisateurs), non-techniciens, usage quotidien (2–3 scans/jour).

**Problème résolu :** Le relevé manuel des cotes d'un joint suivi de la saisie CAO est lent, sujet aux erreurs de transcription, et dépendant d'une expertise disponible en nombre limité. CorniScan élimine ce processus intégralement.

### Ce qui rend ce produit unique

La proposition de valeur repose sur deux innovations combinées :

1. **La carte bancaire comme outil de calibration industriel universel.** Un objet ISO 7810 (85,6 × 54 mm) posé à côté du joint résout simultanément l'échelle et la correction de perspective via homographie — remplaçant le mètre-ruban, le trépied et l'opérateur CAO avec un objet déjà dans la poche de chaque utilisateur.

2. **La radicalité du périmètre.** CorniScan ne fait qu'une chose : photo → DXF → email. L'écran de validation maintient l'humain dans la boucle avant tout envoi (contour superposé + cotes calculées + saisie épaisseur). Aucune fonctionnalité périphérique ne compromet cette simplicité.

**Pourquoi maintenant :** OpenCV, ezdxf et smartphones 12MP existaient depuis plusieurs années, mais le coût de développement était prohibitif pour une PME. Les outils IA actuels ouvrent une fenêtre d'opportunité inédite pour construire cet outil à coût maîtrisé.

## Project Classification

- **Type de projet :** Web App — PWA mobile-first, SPA 3 écrans (Login, Camera, Validation), backend FastAPI
- **Domaine :** Outil industriel de fabrication — vision par ordinateur appliquée, génération de fichiers CAO
- **Complexité :** Moyenne — précision ±1mm comme risque technique principal (à valider en Phase 0) ; aucune contrainte réglementaire
- **Contexte :** Greenfield — nouveau produit construit de zéro

## Success Criteria

### User Success

- **Autonomie dès la première utilisation :** Un opérateur réalise son premier scan complet (photo → DXF → email reçu) sans assistance ni documentation, en moins de 5 minutes.
- **Zéro retour au processus manuel :** Après adoption, aucun opérateur ne revient au relevé manuel pour les joints dans le périmètre de l'app (posables à plat, carte bancaire visible).
- **Interface sans friction :** Chaque écran comporte une action principale évidente. La checklist qualité et le cadrage guidé éliminent les erreurs avant qu'elles n'arrivent.
- **Confiance dans les résultats :** L'opérateur valide le contour sur l'écran de validation sans doute — le contour affiché correspond visuellement au joint physique.

### Business Success

- **Adoption complète :** 100% des opérateurs concernés utilisent CorniScan pour tous les joints éligibles dans les 4 semaines suivant le déploiement.
- **Élimination du processus manuel :** Le temps cumulé consacré au relevé + saisie CAO tombe à zéro pour les cas couverts.
- **Coût d'exploitation maîtrisé :** ≤ 10€/mois (infrastructure uniquement — Render Starter + services email).

### Technical Success

- **Précision dimensionnelle :** Erreur ≤ ±1mm sur 90% des joints testés (validé sur 20+ joints réels, mesures de référence au pied à coulisse).
- **Temps de traitement :** < 5 secondes entre soumission photo et affichage du contour superposé.
- **Taux de détection carte :** > 95% sur photos en conditions normales d'atelier.
- **Taux de succès contour :** > 90% sur joints propres et usagés.
- **Disponibilité :** > 99% pendant les heures ouvrées (Render Starter sans spin-down).

### Measurable Outcomes

| Métrique | Cible | Méthode de mesure |
|---|---|---|
| Autonomie premier scan | 1re utilisation sans aide | Test utilisateur observé |
| Précision | ≤ ±1mm sur ≥ 90% des cas | Suite 20+ joints, pied à coulisse |
| Temps traitement | < 5 secondes | Chronométrage submission → contour |
| Détection carte | > 95% | Tests photos variées |
| Détection contour | > 90% | Tests joints réels |
| Adoption équipe | 100% en 4 semaines | Suivi d'utilisation |
| Coût infra | ≤ 10€/mois | Factures services cloud |

## Product Scope & Development Phases

### Development Strategy

Problem-solving MVP — éliminer le processus manuel de relevé et saisie CAO pour les joints éligibles chez Cornille SA. Développement solo (Léo), sans contrainte de planning externe. Architecture modulaire (algo vision → API → frontend) pour permettre l'avancement et le test couche par couche.

### Phase 0 — Prototype de validation (Python standalone)

**Objectif :** Gate go/no-go sur l'hypothèse technique centrale avant tout investissement full-stack.

**Périmètre :** Script Python standalone — homographie carte + détection contours OpenCV + conversion pixel/mm. Sans interface, sans déploiement.

**Critère de passage :** Précision ≤ ±1mm sur ≥ 90% d'une suite de 20+ joints réels Cornille SA, mesurés au pied à coulisse.

**Décision :** Validé → Phase 1. Non validé → re-travail algo ou abandon du projet.

### Phase 1 — MVP (Web App complète)

**Critères de mise en production :**
1. Le produit fonctionne comme spécifié (précision, temps traitement, taux de détection)
2. Les opérateurs utilisent l'app de façon autonome (premier scan sans assistance)

**Périmètre :**
- Authentification login/mot de passe + gestion comptes admin (liste, ajout, désactivation, changement mdp forcé au 1er login)
- Écran Camera : flux plein écran portrait, caméra arrière, checklist qualité, indicateur de détection carte en temps réel
- Backend : homographie + détection contours hiérarchiques (OpenCV) + conversion pixel/mm via carte ISO 7810
- Écran Validation : contour superposé, cotes calculées, saisie épaisseur, avertissement carte partielle, options retry/force-envoi
- Génération DXF R2018 (ezdxf) + envoi email vers info@cornille-sa.com : triple pièce jointe (DXF + PNG contour + JPEG original), objet horodaté `Scan date | heure | opérateur | dimensions | épaisseur`
- PWA installable iOS & Android

### Phase 2 — Growth (Post-MVP)

- Historique des scans par opérateur (consultation des DXF passés)
- Ajustement manuel du contour sur l'écran de validation (drag des points de contrôle)
- Export formats supplémentaires (PDF avec cotes, SVG)
- Statistiques d'utilisation (tableau de bord admin)

### Phase 3 — Vision (Expansion)

- Extension SaaS multi-tenant (autres entreprises)
- Détection automatique de l'épaisseur (capteur de profondeur ou stéréovision)
- Intégration directe logiciel CAO (import DXF automatique dans AutoCAD/SolidWorks)

### Risques & Mitigations

| Risque | Mitigation |
|---|---|
| Précision insuffisante (>±1mm) | Phase 0 obligatoire — zéro investissement full-stack sans validation algo |
| Risque marché | Base utilisateurs captive (5–10 opérateurs Cornille SA) — validation directe en conditions réelles |
| Solo dev — parallélisme impossible | Architecture modulaire — chaque couche développable et testable indépendamment |

## User Journeys

### Parcours 1 — Thomas, Opérateur (Parcours Nominal)

**Persona :** Thomas, technicien atelier chez Cornille SA depuis 8 ans. À l'aise avec son smartphone, mais pas du tout avec AutoCAD. Pour chaque joint à reproduire, il appelait le bureau technique et attendait — parfois des heures.

**Scène d'ouverture :** Un client envoie un joint usagé à reproduire en urgence. Thomas est seul en atelier. Il ouvre CorniScan dans le navigateur, entre ses identifiants, voit le bouton "Nouveau scan". Il appuie.

**Action montante :** L'écran affiche la caméra en direct avec deux cases à cocher. Il pose le joint sur la table, sort sa carte bancaire, la pose à côté. Il coche "Joint propre et posé à plat" et "Carte entièrement visible". Un cadre vert apparaît autour de la carte — détection confirmée. Il appuie sur "Capturer".

**Climax :** Un spinner "Analyse en cours…" pendant 3 secondes. L'écran de validation s'ouvre : sa photo avec le contour tracé en vert, les dimensions calculées (147 × 93 mm), un champ "Épaisseur". Il saisit 6 mm. Le contour correspond exactement. Il appuie sur "Valider et envoyer".

**Résolution :** 40 secondes plus tard : confirmation d'envoi. Dans la boîte info@cornille-sa.com : `Scan 2026-02-21 09h14 | Thomas | 147×93mm | ép.6mm` — avec le DXF, le PNG du contour, et la photo originale. Thomas retourne à son poste. Zéro appel, zéro attente.

*Capacités révélées : authentification, capture guidée avec checklist, feedback visuel temps réel (cadre vert), analyse backend, validation contour+cotes+saisie épaisseur, email automatique triple pièce jointe.*

---

### Parcours 2 — Thomas, Opérateur (Cas Limite : Carte Mal Détectée)

**Scène d'ouverture :** Thomas scanne un deuxième joint. Pressé, il a posé la carte à moitié sous le joint sans s'en rendre compte. Il coche les cases et capture.

**Action montante :** L'app détecte 3 coins de la carte sur 4. L'écran de validation s'affiche avec un bandeau : "Calibration insuffisante — coin de la carte non détecté. Résultat potentiellement imprécis."

**Climax :** Thomas choisit de recommencer. Il repositionne la carte, reprend la photo. Le cadre vert s'affiche clairement. L'analyse réussit.

**Résolution :** Le scan correct est envoyé. Thomas a compris l'importance du positionnement — l'app lui a enseigné la bonne pratique sans documentation.

*Capacités révélées : détection partielle carte (< 4 coins = avertissement), message d'erreur actionnable, retry sans re-login, option envoi forcé avec flag dans l'email.*

---

### Parcours 3 — Léo, Administrateur (Gestion des Comptes)

**Persona :** Léo, développeur et responsable de l'outil chez Cornille. Il gère qui a accès à CorniScan.

**Scène d'ouverture :** Un nouveau technicien (Karim) rejoint l'équipe. Léo doit lui créer un compte pour son premier jour.

**Action montante :** Léo se connecte avec son compte admin, voit la liste des utilisateurs existants, clique "Ajouter un utilisateur", saisit le nom et le mot de passe provisoire de Karim.

**Climax :** Le compte est créé. Karim se connecte le lendemain — l'app lui demande de changer son mot de passe au premier login.

**Résolution :** Karim est opérationnel. Six mois plus tard, un technicien part — Léo désactive son compte en un clic. L'ex-employé ne peut plus se connecter.

*Capacités révélées : liste users, ajout, désactivation, changement mot de passe forcé au 1er login, rôles admin/user.*

---

### Journey Requirements Summary

| Parcours | Capacités révélées |
|---|---|
| Opérateur nominal | Auth, capture guidée, checklist, cadrage temps réel, analyse backend, validation contour+cotes, saisie épaisseur, email automatique |
| Opérateur cas limite | Détection partielle carte (< 4 coins), message d'erreur actionnable, retry sans re-login, option envoi forcé avec avertissement |
| Admin gestion comptes | Liste users, ajout, désactivation, changement mot de passe forcé au 1er login, rôles admin/user |

## Domain-Specific Requirements

### Conformité & Réglementation

- **RGPD — impact minimal :** L'architecture stateless (zéro stockage fichiers côté serveur) élimine la majorité des obligations RGPD. Photos et DXF transitent uniquement en mémoire RAM. Seules données persistantes : username + hash bcrypt. Aucun consentement explicite requis pour un outil interne professionnel.
- **Aucune certification industrielle requise :** CorniScan est un outil d'aide à la numérisation, non un système de mesure certifié. La responsabilité de la précision incombe à l'opérateur via l'écran de validation.

### Contraintes Techniques

- **Conditions d'atelier :** L'algorithme doit être robuste à l'éclairage variable (néons, lumière naturelle, ombres portées), aux joints sales/huileux, et aux surfaces de pose non maîtrisées (établis métalliques, carton, tissu).
- **Connectivité réseau :** WiFi d'atelier (qualité variable) ou 4G/5G. Le workflow tolère 1–3 secondes de latence réseau. Pas de mode hors-ligne requis.
- **Appareils non imposés :** Smartphone personnel ou entreprise. Compatibilité cible : Chrome/Safari mobile sur iOS 15+ et Android 10+. Résolution caméra minimale : 8 MP.

### Format DXF — Compatibilité CAO

- **Standard requis :** DXF R2018 (AutoCAD 2018+), entités `LWPOLYLINE` fermées, coordonnées en millimètres à l'échelle 1:1, sans calques nommés complexes.
- **Exigence de validité :** Tout fichier DXF généré s'ouvre sans erreur dans AutoCAD et est directement utilisable pour découpe CNC sans manipulation préalable.

### Risques Domaine & Mitigations

| Risque | Mitigation |
|---|---|
| Précision insuffisante sur joint complexe | Écran de validation obligatoire — opérateur approuve avant envoi |
| Joint hors champ (trop grand) | Message guidant l'opérateur à reculer — contrainte physique documentée |
| Connexion réseau coupée pendant l'analyse | Message d'erreur explicite, invitation à réessayer — état non persisté |
| Format DXF invalide pour certains logiciels CAO | Tests de compatibilité AutoCAD + validation ezdxf en CI |

## Innovation & Novel Patterns

### Innovations Identifiées

**Innovation #1 — La carte bancaire comme instrument de mesure industriel universel**

La carte bancaire ISO 7810 (85,6 × 54 mm), objet déjà dans la poche de chaque opérateur, devient la référence métrologique du système. Posée à côté du joint, elle résout simultanément deux problèmes en une seule opération d'homographie :

- **L'échelle** : dimensions normalisées → conversion pixel/mm précise
- **La perspective** : les 4 coins détectés corrigent la distorsion de perspective (homographie plane → vue orthogonale)

Un objet du quotidien, standardisé mondialement, remplace un équipement de mesure industriel. Aucune infrastructure, aucun calibrage préalable, aucun consommable.

**Innovation #2 — Passerelle smartphone → fichier machine (DXF) sans expertise intermédiaire**

Le flux complet s'étend du monde physique (joint en caoutchouc) au monde numérique (fichier DXF exploitable en CAO/CNC) via un navigateur mobile — sans scanner 3D, sans logiciel CAO, sans technicien. La vision par ordinateur assume le rôle de l'expert intermédiaire.

**Innovation #3 — Fenêtre technologique PME ouverte par les outils IA de développement**

CorniScan n'aurait pas été économiquement faisable avant 2024. La combinaison (OpenCV mature + outils IA de développement + infrastructure cloud à coût marginal) démocratise la vision par ordinateur industrielle pour les PME.

### Market Context & Competitive Landscape

| Alternative | Coût | Friction | Précision |
|---|---|---|---|
| Relevé manuel + saisie CAO | 0€ matériel | Haute (expert requis, attente) | Variable (erreur humaine) |
| Photogrammétrie professionnelle | >1 000€/an | Haute (logiciel complexe) | Excellente |
| Scanner 3D industriel | >5 000€ | Très haute (matériel dédié) | Excellente |
| CorniScan | ~10€/mois infra | Minimale (3 gestes) | ±1mm cible |

Aucun concurrent direct dans le segment PME pour ce cas d'usage. Positionnement unique : précision industrielle suffisante + friction opérateur minimale + coût infra marginal.

### Validation de l'Hypothèse Centrale

Le prototype Phase 0 (Python standalone) constitue le gate go/no-go — voir section Product Scope. Critères : précision ±1mm sur 20+ joints réels, robustesse en conditions atelier, autonomie opérateur premier scan.

### Risques Innovation

| Risque | Probabilité | Mitigation |
|---|---|---|
| Précision insuffisante (>±1mm) sur joints complexes | Moyen | Gate Phase 0 — prototype Python avant dev full-stack |
| Détection carte impossible (< 4 coins visibles) | Faible | Contrainte explicite : 4 coins requis, avertissement UI, option retry |
| Variabilité smartphone (distorsion optique) | Moyen | Tests sur 3+ modèles différents en Phase 0 |
| Joints trop grands pour le champ de la caméra | Faible | Message guidé, contrainte physique documentée dans l'onboarding |
| Innovation sans marché au-delà de Cornille | Faible (MVP scope) | Périmètre délibérément limité à Cornille SA — expansion post-validation |

## Web App Specific Requirements

### Project-Type Overview

SPA mobile-first déployée comme PWA installable sur iOS et Android. 3 routes : `/login`, `/camera`, `/validation`. Service worker pour installation et cache des assets statiques — pas de fonctionnalité offline.

### Browser Matrix

| Browser | Version min | Plateforme | Rôle |
|---|---|---|---|
| Chrome Mobile | 90+ | Android 10+ | Primaire — opérateurs |
| Safari Mobile | 15+ | iOS 15+ | Primaire — opérateurs |
| Chrome Desktop | 90+ | Windows/Mac | Secondaire — admin |
| Firefox Desktop | 90+ | Windows/Mac | Secondaire — admin |

### Camera Requirements

- `facingMode: "environment"` — caméra arrière imposée, frontale désactivée
- Résolution cible : 1920×1080 (fallback 1280×720)
- Flux plein écran : preview caméra couvre 100% du viewport en portrait
- Orientation portrait imposée sur l'écran Camera — basculement en paysage bloqué
- HTTPS obligatoire pour l'accès à la caméra (fourni automatiquement par Render)

### PWA & Installability

- Manifest.json : nom, icônes 192×192 + 512×512, `display: standalone`, `orientation: portrait`, `theme_color`
- Android : `beforeinstallprompt` event → bannière native d'installation
- iOS : guide UX contextuel "Partager → Sur l'écran d'accueil" affiché à la première connexion réussie
- Offline : non supporté — message explicite si réseau absent

### Responsive Design

- Mobile-first : écrans Camera et Validation conçus pour portrait smartphone (320px → 430px)
- Admin desktop : interface de gestion des comptes responsive jusqu'à 1440px
- Touch targets : zones interactives ≥ 48×48px sur toutes les actions principales

### Accessibility Level

Bonnes pratiques UX — pas de certification WCAG formelle :
- Contraste texte/fond ≥ 4.5:1
- Messages d'erreur avec action corrective explicite
- Interface sans jargon technique (validé par test opérateur en Phase 1)

## Functional Requirements

### Authentification & Sessions

- **FR1 :** Un opérateur peut s'authentifier avec un nom d'utilisateur et un mot de passe
- **FR2 :** Un opérateur non authentifié est redirigé vers l'écran de connexion
- **FR3 :** Un opérateur est contraint de changer son mot de passe à sa première connexion
- **FR4 :** Un opérateur peut se déconnecter

### Administration & Gestion des Comptes

- **FR5 :** L'administrateur peut consulter la liste de tous les comptes utilisateurs
- **FR6 :** L'administrateur peut créer un nouveau compte opérateur avec un mot de passe provisoire
- **FR7 :** L'administrateur peut désactiver un compte opérateur (accès révoqué immédiatement)
- **FR8 :** L'administrateur dispose d'un rôle distinct des opérateurs avec accès exclusif aux fonctions de gestion des comptes

### Capture de Scan

- **FR9 :** L'opérateur peut accéder au flux caméra arrière en temps réel depuis le navigateur mobile
- **FR10 :** L'opérateur voit un indicateur temps réel confirmant la détection de la carte bancaire dans le champ caméra
- **FR11 :** L'opérateur peut cocher une checklist de qualité (joint propre + carte entièrement visible) avant la capture
- **FR12 :** L'opérateur peut déclencher la capture de la photo depuis l'écran caméra
- **FR13 :** L'écran caméra s'affiche et reste en mode portrait — le basculement en paysage est bloqué

### Traitement d'Image & Calibration

- **FR14 :** Le système détecte la carte bancaire dans la photo et calcule le facteur d'échelle pixel/mm via homographie
- **FR15 :** Le système corrige la distorsion de perspective de la photo en utilisant les 4 coins de la carte
- **FR16 :** Le système détecte le contour extérieur du joint dans la photo corrigée en perspective
- **FR17 :** Le système calcule les dimensions (largeur × hauteur) du joint en millimètres
- **FR18 :** Le système signale une calibration insuffisante si moins de 4 coins de la carte sont détectés

### Validation du Scan

- **FR19 :** L'opérateur voit le contour détecté du joint superposé sur la photo originale
- **FR20 :** L'opérateur voit les dimensions calculées du joint affichées numériquement
- **FR21 :** L'opérateur peut saisir manuellement l'épaisseur du joint en millimètres
- **FR22 :** L'opérateur voit un avertissement explicite et une action corrective si la calibration est insuffisante
- **FR23 :** L'opérateur peut choisir de recommencer la photo ou de forcer l'envoi malgré un avertissement de calibration
- **FR24 :** L'opérateur peut valider et envoyer le scan depuis l'écran de validation

### Génération & Livraison

- **FR25 :** Le système génère un fichier DXF R2018 représentant le contour du joint, coordonnées en millimètres à l'échelle 1:1
- **FR26 :** Le système envoie automatiquement un email vers info@cornille-sa.com avec 3 pièces jointes (DXF + PNG contour + JPEG original)
- **FR27 :** L'objet de l'email inclut automatiquement la date, l'heure, le nom de l'opérateur, les dimensions et l'épaisseur
- **FR28 :** L'opérateur reçoit une confirmation visuelle après l'envoi réussi
- **FR29 :** Un scan envoyé avec avertissement de calibration inclut un flag explicite dans le corps de l'email

### Gestion des Erreurs & Reprise

- **FR30 :** L'opérateur voit un message d'erreur explicite avec action corrective en cas d'échec de traitement
- **FR31 :** L'opérateur peut recommencer un scan depuis l'écran de validation sans se reconnecter
- **FR32 :** L'opérateur voit un message explicite si la connexion réseau est absente lors de l'analyse

### PWA & Installation

- **FR33 :** L'application peut être installée sur l'écran d'accueil Android via une invite d'installation native
- **FR34 :** L'application affiche un guide d'installation contextuel pour iOS à la première connexion réussie
- **FR35 :** L'application s'exécute en mode standalone (sans barre de navigation du navigateur) une fois installée

## Non-Functional Requirements

### Performance

- **NFR-P1 :** Le temps entre la soumission de la photo et l'affichage du contour est inférieur à 5 secondes pour 90% des requêtes en conditions réseau normales (WiFi/4G atelier)
- **NFR-P2 :** Le First Contentful Paint est inférieur à 2 secondes sur connexion WiFi ou 4G
- **NFR-P3 :** Le bundle JavaScript initial est inférieur à 300KB compressé (gzip)
- **NFR-P4 :** L'interface reste interactive pendant le traitement backend — aucun gel de l'UI pendant l'analyse

### Sécurité

- **NFR-S1 :** Les mots de passe sont stockés exclusivement sous forme de hash bcrypt (salt cost ≥ 12)
- **NFR-S2 :** Toutes les communications client–serveur transitent en HTTPS (TLS 1.2+)
- **NFR-S3 :** Les sessions expirent après une période d'inactivité définie (calibrée pour le contexte atelier — ex. 8h)
- **NFR-S4 :** Les données persistées sont limitées au strict minimum : username + hash bcrypt. Aucune photo, DXF ni métadonnée de scan stockée côté serveur

### Fiabilité

- **NFR-R1 :** L'application est disponible à plus de 99% pendant les heures ouvrées (lundi–vendredi, 7h–18h)
- **NFR-R2 :** En cas d'erreur serveur, l'application affiche un message explicite sans perdre l'état de la session ni forcer une reconnexion
- **NFR-R3 :** La perte de connexion réseau pendant le traitement n'entraîne aucune corruption ni perte de données — l'état est intégralement côté client avant soumission

### Intégration & Compatibilité

- **NFR-I1 :** Tout fichier DXF généré s'ouvre sans erreur dans AutoCAD 2018+ et est directement utilisable pour découpe CNC sans manipulation préalable
- **NFR-I2 :** La conformité DXF (entités LWPOLYLINE fermées, unités mm, échelle 1:1) est vérifiée automatiquement avant l'envoi email
- **NFR-I3 :** En cas d'échec SMTP transitoire, une nouvelle tentative est effectuée avant de retourner une erreur à l'utilisateur
- **NFR-I4 :** Le format de l'objet email (`Scan date | heure | opérateur | dimensions | épaisseur`) reste stable et structuré pour permettre un traitement côté Cornille SA
