# Story 5.1: Génération du fichier DXF R2018 conforme AutoCAD

Status: done

## Story

As a système,
I want générer un fichier DXF R2018 représentant le contour du joint à l'échelle 1:1 en millimètres,
So that le fichier est directement utilisable pour découpe CNC dans AutoCAD 2018+ sans manipulation préalable.

## Acceptance Criteria

1. LWPOLYLINE fermée en DXF R2018 (FR25)
2. Coordonnées en mm à l'échelle 1:1, $INSUNITS = 4 (NFR-I1)
3. Validation avant envoi : is_closed + units (NFR-I2)
4. Erreur retournée au frontend si validation échoue
5. Bytes en mémoire uniquement — pas de fichier disque (NFR-S4)

## Tasks / Subtasks

- [x] Task 1: `dxf_service.py` — `generate_dxf(contour_points, width_mm, height_mm)` → bytes
- [x] Task 2: `tests/test_dxf_service.py` — tests DXF

## File List

- `corniscan/backend/app/services/dxf_service.py` (nouveau)
- `corniscan/backend/tests/test_dxf_service.py` (nouveau)
