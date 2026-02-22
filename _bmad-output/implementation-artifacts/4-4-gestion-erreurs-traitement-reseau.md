# Story 4.4: Gestion des erreurs de traitement et de réseau

Status: done

## Story

As an opérateur,
I want recevoir des messages d'erreur explicites avec des actions correctives en cas d'échec de traitement ou d'absence de réseau,
So that je sais toujours quoi faire pour continuer sans perdre ma session ni mes données.

## Acceptance Criteria

1. **Given** le backend retourne une erreur lors du traitement (HTTP 500 ou résultat inattendu) **When** le frontend reçoit la réponse **Then** un message explicite s'affiche : "Une erreur est survenue lors de l'analyse. Recommencez la photo." (FR30)

2. **Given** le device n'a pas de connexion réseau au moment de la soumission **When** la tentative de soumission est effectuée **Then** un message spécifique s'affiche : "Connexion réseau absente. Vérifiez votre WiFi ou 4G avant de réessayer." (FR32)

3. **Given** une erreur survient pendant le traitement **When** le message d'erreur est affiché **Then** l'opérateur peut réessayer depuis l'écran de validation sans être redirigé vers `/login` (FR31)

4. **Given** une erreur réseau survient **When** la session de l'opérateur est toujours active **Then** aucune perte de données — l'image capturée reste en mémoire (NFR-R3)

5. **Given** une erreur serveur se produit **When** le message est affiché **Then** la session reste active — aucune déconnexion forcée ne survient (NFR-R2)

## Tasks / Subtasks

- [x] Task 1: `AnalyseView.vue` — catch block : `navigator.onLine === false` → message FR32, sinon → message FR30 (AC: #1, #2)
- [x] Task 2: Tests — AnalyseView Story 4.4 (AC: #1–5)

## Dev Notes

### Stratégie de différenciation des erreurs

```typescript
} catch (e) {
  if (!navigator.onLine) {
    error.value = 'Connexion réseau absente. Vérifiez votre WiFi ou 4G avant de réessayer.'
  } else {
    error.value = "Une erreur est survenue lors de l'analyse. Recommencez la photo."
  }
}
```

`navigator.onLine` est `false` quand le navigateur détecte l'absence de réseau. Les erreurs `TypeError: Failed to fetch` (fetch réseau) sont souvent accompagnées de `navigator.onLine === false` dans les navigateurs mobiles.

### NFR-R3 : photo préservée en mémoire

`clearPhoto()` n'est jamais appelé sur erreur. Seul `clearResult()` est appelé via `handleRetake()`. La photo reste dans `scanStore.photo` tant que l'opérateur ne déclenche pas manuellement "Recommencer la photo".

### NFR-R2 : session préservée

`apiClient` ne logout que sur 401. Les erreurs 500 / réseau ne déclenchent pas de logout. Invariant déjà garanti par architecture.

### References

- FR30: message erreur traitement
- FR31: réessai sans redirect /login
- FR32: message erreur réseau
- NFR-R2: session préservée
- NFR-R3: données non perdues

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(à compléter)

### Completion Notes List

- 121/121 tests frontend GREEN
- `navigator.onLine` mocké avec `vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(false)` dans jsdom
- Le catch block n'utilise plus `e.message` : le message est toujours fixe selon le contexte réseau

### Change Log

- 2026-02-22 — Story 4.4 démarrée

### File List

- `corniscan/frontend/src/views/AnalyseView.vue` (modifié — catch block différencié)
- `corniscan/frontend/src/views/__tests__/AnalyseView.spec.ts` (modifié — tests Story 4.4)
