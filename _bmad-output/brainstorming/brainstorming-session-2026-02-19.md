---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: []
session_topic: 'Automatisation de la numérisation de joints d étanchéité vers des fichiers DXF exploitables en CAO'
session_goals: 'Capturer ou charger une photo, détecter/mesurer automatiquement les contours, générer un fichier DXF compatible AutoCAD, envoyer par email'
selected_approach: 'ai-recommended'
techniques_used: ['First Principles Thinking', 'SCAMPER Method', 'Constraint Mapping']
ideas_generated: [25]
session_active: false
workflow_completed: true
context_file: ''
---

# Brainstorming Session Results

**Facilitateur :** Léo
**Date :** 2026-02-19

## Aperçu de la session

**Sujet :** Automatisation de la numérisation de joints d'étanchéité vers des fichiers DXF exploitables en CAO
**Objectifs :** Capturer ou charger une photo, détecter/mesurer automatiquement les contours, générer un fichier DXF compatible AutoCAD, envoyer par email

## Technique 1 : First Principles Thinking — Résultats

### Vérités Fondamentales Découvertes

**[Fondation #1] : L'Épaisseur Découplée**
_Concept :_ L'épaisseur étant toujours uniforme, elle n'a pas besoin d'être détectée visuellement — un simple champ de saisie manuelle au moment de la prise de vue suffit. La photo ne gère que les 2 dimensions planes.
_Nouveauté :_ Élimine un problème techniquement insoluble (3D depuis 2D) en acceptant qu'il soit humain, pas algorithmique.

**[Fondation #2] : La Carte Comme Cerveau de Calibration**
_Concept :_ Un objet de référence standard (carte bancaire, marqueur imprimé) posé à côté du joint résout simultanément l'échelle ET la correction de perspective via homographie. L'app détecte ses 4 coins et "redresse" l'image avant toute mesure.
_Nouveauté :_ Un seul objet physique remplace à la fois le mètre-ruban ET le trépied parfaitement perpendiculaire.

**[Fondation #3] : Le Contour Comme Vérité Unique**
_Concept :_ L'algorithme ne cherche pas "le joint" — il cherche la frontière fermée la plus cohérente dans l'image, après correction de perspective. Le matériau du joint crée naturellement un contraste d'arête avec n'importe quel fond d'atelier.
_Nouveauté :_ Libère complètement l'utilisateur de toute contrainte de fond — pas de tapis vert, pas de surface blanche imposée.

**[Fondation #4] : Le DXF comme Contour Nu**
_Concept :_ Un fichier DXF de joint = une ou plusieurs polylignes fermées à l'échelle 1:1. L'app n'a pas besoin de "comprendre" le joint — elle doit juste extraire des bords fermés et les écrire à la bonne échelle.
_Nouveauté :_ Démystifie le format DXF — ce n'est pas un document technique complexe, c'est une liste de coordonnées. Librairies légères suffisantes, pas d'intégration AutoCAD.

**[Fondation #5] : L'Uniformité Algorithmique**
_Concept :_ Le joint entier — bord externe + tous les trous (0 à 20, n'importe quelle forme) — se réduit à un seul problème : trouver des contours fermés ordonnés du plus grand au plus petit.
_Nouveauté :_ Élimine la logique conditionnelle complexe. Un seul algorithme universel, hiérarchique.

**[Fondation #6] : L'App Multi-Utilisateur Guidée**
_Concept :_ À 2-3 joints/jour sur plusieurs utilisateurs, l'app doit être infaillible sans formation. L'expertise est dans l'algorithme, pas dans l'utilisateur.
_Nouveauté :_ CorniScan devient un processus industriel standardisé — n'importe qui chez Cornille peut scanner un joint correctement du premier coup.

**[Fondation #7] : L'Écran de Validation Comme Filet de Sécurité**
_Concept :_ Après analyse, l'app superpose le contour détecté sur la photo avec les cotes calculées. L'utilisateur valide avant toute génération. La CNC ne découpe jamais sur une mesure non-approuvée.
_Nouveauté :_ Transforme l'erreur algorithmique d'un problème silencieux en un problème visible et rattrapable.

**[Fondation #8] : Destination Unique, Contenu Riche**
_Concept :_ Email toujours vers info@cornille-sa.com. Contenu : DXF en pièce jointe + photo du joint + intitulé identifiant (date, opérateur, référence).
_Nouveauté :_ La boîte mail devient une archive consultable naturelle sans système documentaire supplémentaire.

**[Fondation #9] : Architecture Cloud-Mobile**
_Concept :_ Le smartphone capture et affiche, le cloud calcule. Algorithme lourd côté serveur, interface légère côté app. Historique stockable en cloud.
_Nouveauté :_ Découple l'interface du moteur. Mise à jour algorithmique sans mise à jour de l'app.

**[Fondation #10] : Le Bruit de Surface n'Est Pas un Bruit de Forme**
_Concept :_ Un joint usagé sale reste géométriquement fidèle. Taches d'huile et saleté affectent la texture, pas les arêtes. L'algorithme reste robuste sur des joints d'atelier très utilisés.
_Nouveauté :_ Élimine le besoin de preprocessing complexe.

**[Fondation #11] : Périmètre Net**
_Concept :_ CorniScan commence à l'ouverture de l'app et se termine à l'envoi de l'email. Photo → DXF → email, rien de plus.
_Nouveauté :_ "On ne fait pas X" est une décision de design aussi importante que "on fait Y". Protection contre la dérive fonctionnelle.

---

## Sélection des techniques

**Approche :** Recommandations IA
**Contexte d'analyse :** Défi technique concret avec innovation produit, ton pragmatique

**Techniques recommandées :**
- **First Principles Thinking :** Déconstruire les présupposés jusqu'aux vérités fondamentales pour révéler des approches inattendues
- **SCAMPER Method :** Explorer systématiquement toutes les facettes du produit via 7 lentilles créatives
- **Constraint Mapping :** Identifier toutes les contraintes réelles et trouver des chemins autour d'elles

**Raisonnement IA :** Séquence fondations → génération → affinage, adaptée à un défi technique avec forte composante produit et besoin de pragmatisme.

---

## Technique 2 : SCAMPER — Résultats

**[SCAMPER-S #1] : La Carte Bancaire Comme Standard de Facto**
_Concept :_ La référence de calibration = la carte ISO 7810 ID-1 (85,6 × 54 mm) que tout opérateur a dans sa poche. Pas d'équipement supplémentaire, pas de formation, pas d'oubli possible.
_Nouveauté :_ Le standard industriel de calibration de CorniScan existe déjà dans le portefeuille de chaque utilisateur.

**[SCAMPER-C #2] : Épaisseur sur l'Écran de Validation**
_Concept :_ La saisie de l'épaisseur apparaît sur l'écran de restitution, aux côtés des mesures calculées automatiquement. L'opérateur voit toutes les cotes ensemble et valide l'ensemble d'un coup.
_Nouveauté :_ L'épaisseur devient la 3ème dimension qui complète le tableau de mesures, pas une étape isolée en amont.

**[SCAMPER-C #3] : Objet Email Horodaté**
_Concept :_ Objet automatique : `Scan 2026-02-19 14h32 | Léo | 120×85mm | ép.8mm` — retrouvable par date, heure, opérateur ou dimension sans ouvrir le fichier.
_Nouveauté :_ La boîte info@ devient un registre de production consultable par simple recherche texte.

**[SCAMPER-C #4] : Checklist Qualité à l'Entrée**
_Concept :_ Sur l'écran d'accueil/chargement photo, deux cases à cocher obligatoires avant de continuer : ✓ Joint propre et posé à plat ✓ Carte de référence entièrement visible. Bloque la progression si non cochées.
_Nouveauté :_ Transforme l'erreur en impossibilité — on ne peut pas oublier les prérequis si l'app ne permet pas de les ignorer.

**[SCAMPER-A #5] : Cadrage Guidé Temps Réel**
_Concept :_ Avant la prise de photo, l'app utilise le flux caméra en direct pour détecter la carte de référence en temps réel. Un cadre vert s'affiche quand la carte est bien détectée, la perspective acceptable, et le joint entièrement visible.
_Nouveauté :_ Élimine les photos ratées à la source — feedback visuel immédiat plutôt que découverte d'erreur après analyse.

**[SCAMPER-A #6] : Authentification Login/Mot de Passe**
_Concept :_ Accès à la web app protégé par un système d'authentification. Les utilisateurs de Cornille ont un compte. Le nom de l'opérateur dans l'email horodaté devient automatique.
_Nouveauté :_ Sécurité des données industrielles + identification automatique sans saisie supplémentaire.

**[SCAMPER-M #7] : Validation avec Ajustement Manuel**
_Concept :_ L'écran de validation montre la photo originale avec le contour détecté superposé + les cotes calculées. Si la détection est imparfaite, l'opérateur peut ajuster manuellement le contour avant de valider.
_Nouveauté :_ L'algorithme propose, l'humain dispose. CorniScan reste utilisable même quand la détection n'est pas parfaite.

**[SCAMPER-M #8] : Email Triple Pièce Jointe**
_Concept :_ L'email contient 3 éléments : le DXF (fichier machine), un PNG du contour détecté (ce que l'app a compris), et la photo originale du joint (la réalité physique).
_Nouveauté :_ Traçabilité complète — on voit d'où vient le DXF et comment il a été interprété, sans ouvrir AutoCAD.

**[SCAMPER-E #9] : Interface Épurée par Suppression**
_Concept :_ Quatre éléments éliminés : saisie du nom opérateur (→ login), choix de l'adresse email (→ codée en dur info@cornille-sa.com), écrans de chargement visibles (→ analyse en arrière-plan), gestion de fichiers locaux (→ envoi direct).
_Nouveauté :_ L'interface réduite à l'essentiel — photo, validation, envoi. Trois actions, pas une de plus.

---

## Technique 3 : Constraint Mapping — Résultats

| Contrainte | Type | Verdict |
|-----------|------|---------|
| Précision 1mm | Réelle, surmontable | Atteignable avec cadrage guidé + carte de référence |
| Coupure réseau | Réelle, acceptée | Recommencer — comportement accepté, message d'erreur clair |
| Joint hors cadre | Réelle, acceptée | L'opérateur recule — contrainte physique gérée par l'utilisateur |
| Joint plus petit que la carte | Technique, surmontable | Algorithme hiérarchique détecte tous les contours quelle que soit leur taille relative |
| Éclairage atelier | Imaginée | Pas un obstacle réel — contraste suffisant en conditions d'atelier |
| Contours irréguliers | Imaginée | Pas un problème — contours toujours réguliers (lignes droites + arcs simples) |
| Carte partiellement cachée | Réelle, gérée | Règle absolue : 4 coins visibles obligatoires, sinon blocage avec message |

---

## Organisation et Priorisation

### Idées par thème

**Thème 1 : Capture & Calibration**
- Carte bancaire comme standard universel (toujours en poche, dimensions ISO connues)
- Cadrage guidé temps réel — cadre vert quand les 4 coins de la carte sont détectés
- Checklist qualité à l'entrée — 2 cases obligatoires avant de photographier
- Règle absolue : carte entièrement visible, sinon blocage

**Thème 2 : Algorithme & Traitement**
- Correction de perspective via homographie (4 coins de la carte bancaire)
- Détection de contours hiérarchique — bord externe + 0 à 20 trous, toutes formes régulières
- Robustesse sur joints usagés — bruit de surface ignoré, arêtes fiables
- Génération DXF légère — polylignes fermées simplifiées (Douglas-Peucker), sans AutoCAD
- Architecture cloud-mobile — traitement côté serveur, interface légère sur navigateur

**Thème 3 : Validation & Interface**
- Écran de validation : photo + contour superposé + cotes calculées + saisie épaisseur
- Ajustement manuel du contour si détection imparfaite
- Interface épurée : 3 actions seulement — photo, validation, envoi

**Thème 4 : Livraison & Traçabilité**
- Email triple pièce jointe : DXF + PNG du contour + photo originale
- Objet horodaté : `date | heure | opérateur | dimensions principales`
- Destination unique codée en dur : info@cornille-sa.com

**Thème 5 : Accès & Sécurité**
- Authentification login/mot de passe
- Identification automatique de l'opérateur via session connectée

### Percées transversales
- La carte bancaire résout **deux problèmes avec un seul objet** (échelle + perspective)
- Le login résout **l'identification opérateur sans saisie supplémentaire**
- L'épaisseur manuelle **élimine élégamment le problème 3D insoluble**

### Priorités retenues

**Priorités 1, 2 et 3 : Thèmes Capture, Algorithme et Interface** — le cœur fonctionnel de l'app avant la périphérie.

---

## Plans d'action

**Priorité 1 : Capture & Calibration**
1. Définir le protocole de pose standardisé (position de la carte relative au joint)
2. Prototyper le cadrage guidé temps réel via `getUserMedia` dans le navigateur mobile
3. Tester la détection des 4 coins de carte bancaire sur 10+ photos variées en conditions d'atelier réel
4. Valider que la précision 1mm est atteinte sur joints de tailles différentes (petit < carte, grand > carte)

**Priorité 2 : Algorithme & Traitement**
1. Choisir la stack technique : API Python (OpenCV + ezdxf) côté cloud recommandée
2. Implémenter la correction de perspective (homographie à partir des 4 coins de la carte)
3. Implémenter la détection de contours hiérarchique (bord externe + trous internes)
4. Implémenter la simplification Douglas-Peucker pour polylignes DXF propres
5. Implémenter la génération `.dxf` (librairie `ezdxf` en Python)
6. Tester sur joints réels : ronds, rectangulaires, avec trous circulaires et non-circulaires, joints usagés

**Priorité 3 : Validation & Interface**
1. Concevoir l'écran de validation (photo + contour superposé + tableau de cotes + saisie épaisseur)
2. Implémenter l'ajustement manuel du contour (drag des points de contrôle)
3. Valider l'UX avec un utilisateur non-technique chez Cornille

---

## Résumé et Insights de Session

**Réalisations clés :**
- 25 idées et décisions structurées à travers 3 techniques complémentaires
- Architecture complète de CorniScan définie : web app cloud-mobile, smartphone + navigateur
- Périmètre produit net et défendu : photo → DXF → email, rien de plus
- Stack technique orientée : Python/OpenCV côté cloud, interface web légère

**Percées créatives de la session :**
- La carte bancaire comme outil de calibration industriel universel — élégance par l'ubiquité
- L'épaisseur découplée — résoudre un problème 3D insoluble en l'acceptant comme saisie humaine
- L'écran de validation comme filet de sécurité — l'humain reste dans la boucle de précision

**Narration de la session :**
_Léo a abordé ce défi avec une clarté remarquable sur son problème métier et une capacité à trancher rapidement sur les décisions de périmètre. Le First Principles Thinking a révélé que la complexité apparente du projet (3D, précision industrielle, format propriétaire) se réduit à des vérités simples et gérables. SCAMPER a transformé ces fondations en features concrètes et bien délimitées. La session a produit non pas une liste d'idées mais l'architecture fonctionnelle complète de CorniScan._
