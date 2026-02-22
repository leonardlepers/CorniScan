"""
vision_service.py — Story 3.2 + Story 4.1 + Story 5.2

Détection de carte bancaire et pipeline d'analyse complet.
Exécuté de manière synchrone (appelé via thread pool depuis FastAPI).

Story 3.2 — detect_card() :
  1. Décode JPEG → niveaux de gris → flou gaussien → Canny
  2. Cherche les contours → approxPolyDP
  3. Filtre les quadrilatères larges avec ratio ≈ 1.586 (carte bancaire : 85.6 × 53.98mm)
  4. Retourne card_detected + confidence

Story 4.1 — process_image() :
  1. _find_card_corners() → 4 coins de la carte (réutilise même algo) + calibration_warning
  2. getPerspectiveTransform → warpPerspective (856 × 540 px = 10 px/mm)
  3. _detect_joint_contour() sur l'image corrigée
  4. Calcul dimensions mm
  5. Retour contour normalisé [0,1] en coordonnées image originale
"""

import numpy as np
import cv2


# Ratio largeur/hauteur d'une carte bancaire standard (85.6mm / 53.98mm)
_CARD_RATIO = 85.6 / 53.98  # ≈ 1.585
_RATIO_TOLERANCE = 0.35  # ±35 % de tolérance
_MIN_AREA_FRACTION = 0.04  # Le quadrilatère doit couvrir ≥ 4 % de l'image

# Story 4.1 — constantes pipeline
_SCALE = 10.0          # 10 px par mm
_CARD_W_MM = 85.6
_CARD_H_MM = 53.98
_DST_W = int(_CARD_W_MM * _SCALE)   # 856 px
_DST_H = int(_CARD_H_MM * _SCALE)   # 539 px


def detect_card(image_bytes: bytes) -> dict:
    """Détecte une carte bancaire dans l'image JPEG fournie.

    Args:
        image_bytes: contenu brut du fichier JPEG.

    Returns:
        {"card_detected": bool, "confidence": float}
    """
    # Décodage
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return {"card_detected": False, "confidence": 0.0}

    image_area = img.shape[0] * img.shape[1]

    # Pré-traitement
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_confidence = 0.0
    found = False

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)

        # Filtre : exactement 4 sommets (quadrilatère)
        if len(approx) != 4:
            continue

        area = cv2.contourArea(approx)

        # Filtre : surface minimale (évite les petits artéfacts)
        if area < _MIN_AREA_FRACTION * image_area:
            continue

        # Calcul du ratio largeur/hauteur du bounding rect
        x, y, w, h = cv2.boundingRect(approx)
        if h == 0:
            continue
        ratio = w / h
        # Accepte les deux orientations (portrait / paysage)
        ratio_normalized = max(ratio, 1 / ratio)

        if abs(ratio_normalized - _CARD_RATIO) > _RATIO_TOLERANCE:
            continue

        # Confidence proportionnelle à la surface occupée (cap à 1.0)
        confidence = min(area / image_area * 10.0, 1.0)
        if confidence > best_confidence:
            best_confidence = confidence
            found = True

    return {"card_detected": found, "confidence": round(best_confidence, 3)}


# ── Helpers internes Story 4.1 ────────────────────────────────────────────────


def _order_points(pts: np.ndarray) -> np.ndarray:
    """Ordonne 4 points en TL, TR, BR, BL."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # TL : somme minimale
    rect[2] = pts[np.argmax(s)]   # BR : somme maximale
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # TR : diff minimale
    rect[3] = pts[np.argmax(diff)]  # BL : diff maximale
    return rect


def _find_card_corners(img: np.ndarray) -> tuple:
    """Cherche les 4 coins de la carte bancaire dans l'image.

    Returns:
        (corners_float32_4x2 | None, calibration_warning: bool)
        calibration_warning = True si moins de 4 coins trouvés.
    """
    image_area = img.shape[0] * img.shape[1]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_corners = None
    best_area = 0.0

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)

        if len(approx) != 4:
            continue

        area = cv2.contourArea(approx)
        if area < _MIN_AREA_FRACTION * image_area:
            continue

        x, y, w, h = cv2.boundingRect(approx)
        if h == 0:
            continue
        ratio = w / h
        ratio_normalized = max(ratio, 1 / ratio)

        if abs(ratio_normalized - _CARD_RATIO) > _RATIO_TOLERANCE:
            continue

        if area > best_area:
            best_area = area
            best_corners = approx.reshape(4, 2).astype(np.float32)

    if best_corners is None:
        return None, True  # calibration_warning

    return best_corners, False


def _detect_joint_contour(img: np.ndarray) -> tuple:
    """Détecte le contour principal (joint) sur l'image corrigée.

    Returns:
        (points: list[list[int]], (width_px: float, height_px: float))
        Fallback sur les dimensions de l'image entière si aucun contour trouvé.
    """
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        # Fallback : contour = bounding box de l'image entière
        return [[0, 0], [w, 0], [w, h], [0, h]], (float(w), float(h))

    # Contour le plus grand → joint principal
    largest = max(contours, key=cv2.contourArea)
    perimeter = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.01 * perimeter, True)
    pts = approx.reshape(-1, 2).tolist()

    bx, by, bw, bh = cv2.boundingRect(largest)
    return pts, (float(bw), float(bh))


# ── API publique Story 4.1 ────────────────────────────────────────────────────


def process_image(image_bytes: bytes) -> dict:
    """Pipeline complet d'analyse : carte → homographie → perspective → contour joint → dimensions.

    Args:
        image_bytes: contenu brut du fichier JPEG.

    Returns:
        {
            "contour_points": list[list[float]],  # normalisé [0,1] dans l'image originale
            "dimensions": {"width_mm": float, "height_mm": float},
            "calibration_warning": bool,
        }

    Raises:
        ValueError: si l'image JPEG ne peut pas être décodée.
    """
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Impossible de décoder l'image JPEG.")

    orig_h, orig_w = img.shape[:2]

    # Étape 1 : coins de la carte
    corners, calibration_warning = _find_card_corners(img)

    # Étape 2 : correction perspective
    if corners is not None:
        ordered = _order_points(corners)
        dst_pts = np.array(
            [
                [0, 0],
                [_DST_W - 1, 0],
                [_DST_W - 1, _DST_H - 1],
                [0, _DST_H - 1],
            ],
            dtype=np.float32,
        )
        H = cv2.getPerspectiveTransform(ordered, dst_pts)
        H_inv = np.linalg.inv(H)
        warped = cv2.warpPerspective(img, H, (_DST_W, _DST_H))
    else:
        # Pas de homographie disponible : redimensionnement simple
        H_inv = None
        warped = cv2.resize(img, (_DST_W, _DST_H))

    # Étape 3 : détection contour joint sur image corrigée
    contour_warped, (w_px, h_px) = _detect_joint_contour(warped)

    # Étape 4 : dimensions en mm
    width_mm = w_px / _SCALE
    height_mm = h_px / _SCALE

    # Étape 5 : remappage contour → coordonnées image originale (normalisées)
    if H_inv is not None and contour_warped:
        pts_warped = np.array(contour_warped, dtype=np.float32).reshape(-1, 1, 2)
        pts_orig = cv2.perspectiveTransform(pts_warped, H_inv)
        pts_norm = pts_orig.reshape(-1, 2) / np.array([orig_w, orig_h], dtype=np.float32)
        contour_normalized = pts_norm.tolist()
    elif contour_warped:
        # Scaling proportionnel vers l'image originale
        pts = np.array(contour_warped, dtype=np.float32)
        pts[:, 0] = pts[:, 0] / _DST_W
        pts[:, 1] = pts[:, 1] / _DST_H
        contour_normalized = pts.tolist()
    else:
        contour_normalized = []

    return {
        "contour_points": contour_normalized,
        "dimensions": {
            "width_mm": round(width_mm, 1),
            "height_mm": round(height_mm, 1),
        },
        "calibration_warning": calibration_warning,
    }


def generate_contour_png(image_bytes: bytes, contour_points: list[list[float]]) -> bytes:
    """Génère un PNG avec le contour du joint superposé sur l'image originale (Story 5.2 — FR26).

    Args:
        image_bytes: Bytes JPEG de l'image originale.
        contour_points: Points du contour normalisés [[x, y], ...] avec x,y ∈ [0,1].

    Returns:
        Bytes PNG de l'image avec le contour tracé en vert.

    Raises:
        ValueError: Si l'image ne peut pas être décodée.
    """
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Image invalide — impossible de décoder le JPEG.")

    h, w = img.shape[:2]
    pts = np.array(
        [[int(pt[0] * w), int(pt[1] * h)] for pt in contour_points],
        dtype=np.int32,
    )

    overlay = img.copy()
    cv2.polylines(overlay, [pts], isClosed=True, color=(0, 255, 0), thickness=3)

    _, encoded = cv2.imencode(".png", overlay)
    return encoded.tobytes()
