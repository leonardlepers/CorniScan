# Story 5.3: Confirmation visuelle après envoi réussi

Status: done

## Story

As an opérateur,
I want recevoir une confirmation visuelle après l'envoi réussi du scan,
So that je sais que le dossier a bien été transmis à Cornille SA et peux commencer un nouveau scan.

## Acceptance Criteria

1. Écran de confirmation avec message succès + destinataire info@cornille-sa.com (FR28)
2. Récapitulatif dimensions + épaisseur du scan
3. Bouton "Nouveau scan" → /camera + reset scanStore
4. Erreur envoi gérée dans AnalyseView (retry disponible)

## Tasks / Subtasks

- [x] Task 1: `ConfirmationView.vue` — contenu complet (remplace stub)

## File List

- `corniscan/frontend/src/views/ConfirmationView.vue` (modifié — contenu complet)
