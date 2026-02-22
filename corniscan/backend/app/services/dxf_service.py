"""Service de génération DXF — Story 5.1 (FR25, NFR-I1, NFR-I2, NFR-S4).

Produit un fichier DXF R2018 avec une LWPOLYLINE fermée représentant le contour
du joint à l'échelle 1:1 en millimètres. Le fichier reste en mémoire (bytes) —
aucun fichier n'est écrit sur le disque serveur.
"""

import io

import ezdxf
import numpy as np

# Unité DXF 4 = millimètres (standard DXF InsUnits)
_DXF_UNITS_MM = 4


def generate_dxf(
    contour_points: list[list[float]],
    width_mm: float,
    height_mm: float,
) -> bytes:
    """Génère un fichier DXF R2018 avec le contour du joint (Story 5.1 — FR25).

    Les coordonnées normalisées [0,1] sont converties en mm réels en utilisant
    la boîte englobante du contour mise à l'échelle width_mm × height_mm.

    Args:
        contour_points: Points du contour normalisés [[x, y], ...] avec x,y ∈ [0,1].
        width_mm: Largeur du joint en mm (FR15).
        height_mm: Hauteur du joint en mm (FR15).

    Returns:
        Bytes du fichier DXF (ASCII, encodage UTF-8).

    Raises:
        ValueError: Si le contour a moins de 3 points, ou si la validation
                    DXF échoue (LWPOLYLINE non fermée ou unités incorrectes).
    """
    pts = np.array(contour_points, dtype=float)

    if len(pts) < 3:
        raise ValueError("Le contour doit contenir au moins 3 points.")

    # Convertir les coordonnées normalisées en mm
    # La boîte englobante du contour est mise à l'échelle width_mm × height_mm
    x_min, y_min = pts[:, 0].min(), pts[:, 1].min()
    x_max, y_max = pts[:, 0].max(), pts[:, 1].max()
    x_range = (x_max - x_min) if (x_max - x_min) > 1e-9 else 1.0
    y_range = (y_max - y_min) if (y_max - y_min) > 1e-9 else 1.0

    pts_mm = [
        ((pt[0] - x_min) / x_range * width_mm, (pt[1] - y_min) / y_range * height_mm)
        for pt in pts
    ]

    # Créer le document DXF R2018
    doc = ezdxf.new("R2018")

    # Configurer les unités en mm (NFR-I1)
    doc.header["$INSUNITS"] = _DXF_UNITS_MM

    msp = doc.modelspace()
    polyline = msp.add_lwpolyline(pts_mm)
    polyline.closed = True

    # Validation avant export (NFR-I2)
    if not polyline.is_closed:
        raise ValueError("La LWPOLYLINE générée n'est pas fermée.")
    if doc.header.get("$INSUNITS") != _DXF_UNITS_MM:
        raise ValueError("Les unités DXF ne sont pas configurées en mm.")

    # Export en bytes (NFR-S4 — pas de fichier disque)
    stream = io.StringIO()
    doc.write(stream)
    return stream.getvalue().encode("utf-8")
