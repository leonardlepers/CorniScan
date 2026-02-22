# Story 5.2: Envoi email avec les 3 pièces jointes

Status: done

## Story

As a système,
I want envoyer automatiquement un email vers info@cornille-sa.com avec les 3 pièces jointes,
So that Cornille SA reçoit le dossier complet du scan.

## Acceptance Criteria

1. Email à info@cornille-sa.com avec DXF + PNG contour + JPEG original (FR26)
2. Sujet : `[CorniScan] YYYY-MM-DD HH:MM — <opérateur> — <w>×<h>mm — ép.<t>mm` (FR27)
3. Corps inclut flag calibration si calibration_warning = true (FR29)
4. 2 retries avec 2s d'intervalle (NFR-I3)
5. Pas de persistance fichier (NFR-S4)

## Tasks / Subtasks

- [x] Task 1: `vision_service.py` — `generate_contour_png(image_bytes, contour_points)` → bytes
- [x] Task 2: `email_service.py` — `send_scan_email(...)` via Resend SDK
- [x] Task 3: `scan.py` — update POST /submit : DXF + PNG + email
- [x] Task 4: `config.py` — `resend_from_email` setting
- [x] Task 5: Tests email service

## File List

- `corniscan/backend/app/services/vision_service.py` (modifié — generate_contour_png)
- `corniscan/backend/app/services/email_service.py` (nouveau)
- `corniscan/backend/app/core/config.py` (modifié — resend_from_email)
- `corniscan/backend/app/routers/scan.py` (modifié — submit pipeline complet)
- `corniscan/backend/tests/test_email_service.py` (nouveau)
