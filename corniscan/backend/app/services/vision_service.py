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

Améliorations fiabilité :
  - Seuils Canny auto-adaptatifs (médiane de l'histogramme, σ=0.33)
  - Normalisation résolution entrée (max 2048 px) — stabilise le comportement
    quelque soit la résolution du capteur (iPhone 17 = jusqu'à 48 MP)
  - CLAHE avant détection joint — meilleur contraste en éclairage non uniforme
  - Raffinement sub-pixel des coins carte (cv2.cornerSubPix)
  - minAreaRect pour les dimensions — insensible à l'orientation du joint
  - Dilation morphologique avant findContours — ferme les lacunes Canny
  - Filtre de taille pour exclure les micro-contours parasites
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

# Normalisation résolution — stabilise le comportement quel que soit le capteur
# (iPhone 15 Pro = 48 MP, iPhone 17 = ~48-200 MP selon modèle)
_MAX_PROCESSING_WIDTH = 2048


def _resize_for_processing(img: np.ndarray) -> tuple[np.ndarray, float]:
    """Redimensionne l'image à _MAX_PROCESSING_WIDTH si nécessaire.

    Returns:
        (image_redimensionnée, facteur_scale_down)
        scale_down < 1.0 si redimensionnée, sinon 1.0
    """
    h, w = img.shape[:2]
    if w > _MAX_PROCESSING_WIDTH:
        scale = _MAX_PROCESSING_WIDTH / w
        resized = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        return resized, scale
    return img, 1.0


def _canny_auto(blurred: np.ndarray, sigma: float = 0.33) -> np.ndarray:
    """Canny avec seuils calculés automatiquement via la médiane de l'histogramme.

    Méthode de Bouchet : lower = median * (1 - sigma), upper = median * (1 + sigma).
    Adapte les seuils à la luminosité réelle de l'image (éclairage de chantier variable).
    """
    median = float(np.median(blurred))
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))
    # Canny requiert upper > lower — fallback sur valeurs fixes si médiane trop basse
    if upper <= lower or upper < 20:
        return cv2.Canny(blurred, 30, 100)
    return cv2.Canny(blurred, lower, upper)


def detect_card(image_bytes: bytes) -> dict:
    """Détecte une carte bancaire dans l'image JPEG fournie.

    Args:
        image_bytes: contenu brut du fichier JPEG.

    Returns:
        {"card_detected": bool, "confidence": float}
    """
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return {"card_detected": False, "confidence": 0.0}

    # Normalisation résolution
    img, _ = _resize_for_processing(img)
    image_area = img.shape[0] * img.shape[1]

    # Pré-traitement — kernel adapté à la résolution normalisée
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = _canny_auto(blurred, sigma=0.33)

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

    Améliorations :
      - Seuils Canny auto-adaptatifs
      - Raffinement sub-pixel des coins (cornerSubPix) pour homographie précise

    Returns:
        (corners_float32_4x2 | None, calibration_warning: bool)
        calibration_warning = True si moins de 4 coins trouvés.
    """
    image_area = img.shape[0] * img.shape[1]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = _canny_auto(blurred, sigma=0.33)
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

    # ── Raffinement sub-pixel des coins (améliore la précision de l'homographie)
    # cornerSubPix affine chaque coin à ±0.01 px au lieu de ±1 px
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners_subpix = cv2.cornerSubPix(
        gray,
        best_corners.reshape(-1, 1, 2),
        winSize=(11, 11),
        zeroZone=(-1, -1),
        criteria=criteria,
    )

    return corners_subpix.reshape(4, 2), False


def _detect_joint_contour(img: np.ndarray) -> tuple:
    """Détecte le contour principal (joint) sur l'image corrigée.

    Améliorations :
      - CLAHE pour égaliser le contraste (éclairage non uniforme sur chantier)
      - Seuils Canny auto-adaptatifs
      - Dilation morphologique pour fermer les lacunes du contour
      - minAreaRect pour mesurer les vraies dimensions (insensible à l'inclinaison)
      - Filtre de taille : exclut les contours < 1 % de l'image (bruit)

    Returns:
        (points: list[list[int]], (width_px: float, height_px: float))
        Fallback sur les dimensions de l'image entière si aucun contour trouvé.
    """
    h, w = img.shape[:2]
    min_contour_area = 0.01 * h * w  # Ignore les contours < 1 % de l'image

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE — égalisation adaptative du contraste local
    # Corrige les zones d'ombre/surexposition sans altérer la géométrie
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    edges = _canny_auto(blurred, sigma=0.4)  # sigma légèrement plus large pour le joint

    # Dilation morphologique — ferme les lacunes dans le contour du joint
    # (arêtes manquantes dues aux variations de texture du joint)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        # Fallback : contour = bounding box de l'image entière
        return [[0, 0], [w, 0], [w, h], [0, h]], (float(w), float(h))

    # Filtre les micro-contours parasites puis sélectionne le plus grand
    valid = [c for c in contours if cv2.contourArea(c) >= min_contour_area]
    if not valid:
        return [[0, 0], [w, 0], [w, h], [0, h]], (float(w), float(h))

    largest = max(valid, key=cv2.contourArea)
    perimeter = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.01 * perimeter, True)
    pts = approx.reshape(-1, 2).tolist()

    # ── minAreaRect : dimensions réelles indépendantes de l'orientation ──
    # boundingRect (axe-aligné) surestime les dimensions si le joint est incliné :
    # ex. joint 50×20 mm à 10° → boundingRect donne ~52×24 mm (+4%/+20%)
    # minAreaRect suit les axes principaux du contour → dimensions exactes
    rect = cv2.minAreaRect(largest)
    (_cx, _cy), (rw, rh), _angle = rect
    # minAreaRect peut retourner (width, height) ou (height, width) selon l'angle ;
    # on retourne (plus grande dimension, plus petite) pour un affichage cohérent
    width_px = float(max(rw, rh))
    height_px = float(min(rw, rh))

    return pts, (width_px, height_px)


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

    # ── Normalisation résolution ──
    # Stabilise le comportement quel que soit le capteur (iPhone 17 jusqu'à ~48 MP).
    # On normalise AVANT toute détection, et on retrace les coordonnées en fin de pipeline.
    proc_img, scale_down = _resize_for_processing(img)
    proc_h, proc_w = proc_img.shape[:2]

    # Étape 1 : coins de la carte (sur image normalisée)
    corners, calibration_warning = _find_card_corners(proc_img)

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
        warped = cv2.warpPerspective(proc_img, H, (_DST_W, _DST_H))
    else:
        # Pas de homographie disponible : redimensionnement simple
        H_inv = None
        warped = cv2.resize(proc_img, (_DST_W, _DST_H))

    # Étape 3 : détection contour joint sur image corrigée
    contour_warped, (w_px, h_px) = _detect_joint_contour(warped)

    # Étape 4 : dimensions en mm
    width_mm = w_px / _SCALE
    height_mm = h_px / _SCALE

    # Étape 5 : remappage contour → coordonnées image originale (normalisées)
    # Les coins ont été détectés sur proc_img (scale_down appliqué).
    # H_inv ramène en coordonnées proc_img → on divise par proc_img.shape pour normaliser.
    if H_inv is not None and contour_warped:
        pts_warped = np.array(contour_warped, dtype=np.float32).reshape(-1, 1, 2)
        pts_proc = cv2.perspectiveTransform(pts_warped, H_inv)
        # Normalisation par les dimensions de proc_img (pas orig pour conserver la cohérence
        # avec l'homographie calculée sur proc_img)
        pts_norm = pts_proc.reshape(-1, 2) / np.array([proc_w, proc_h], dtype=np.float32)
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
