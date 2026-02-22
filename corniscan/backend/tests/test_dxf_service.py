"""Tests Story 5.1 — dxf_service.generate_dxf()."""

import io

import ezdxf
import pytest


CONTOUR_4PTS = [[0.1, 0.2], [0.9, 0.2], [0.9, 0.8], [0.1, 0.8]]


def _parse_dxf(dxf_bytes: bytes) -> ezdxf.document.Drawing:
    return ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8")))


def test_generate_dxf_returns_bytes() -> None:
    """AC#1 — La fonction retourne des bytes non vides."""
    from app.services.dxf_service import generate_dxf

    result = generate_dxf(CONTOUR_4PTS, width_mm=30.5, height_mm=20.0)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_generate_dxf_contains_lwpolyline() -> None:
    """AC#1 (FR25) — Le DXF contient une LWPOLYLINE."""
    from app.services.dxf_service import generate_dxf

    doc = _parse_dxf(generate_dxf(CONTOUR_4PTS, width_mm=30.5, height_mm=20.0))
    polylines = [e for e in doc.modelspace() if e.dxftype() == "LWPOLYLINE"]
    assert len(polylines) == 1


def test_generate_dxf_polyline_is_closed() -> None:
    """AC#3 (NFR-I2) — La LWPOLYLINE est fermée."""
    from app.services.dxf_service import generate_dxf

    doc = _parse_dxf(generate_dxf(CONTOUR_4PTS, width_mm=30.5, height_mm=20.0))
    polyline = next(e for e in doc.modelspace() if e.dxftype() == "LWPOLYLINE")
    assert polyline.is_closed is True


def test_generate_dxf_units_are_mm() -> None:
    """AC#2 (NFR-I1) — Les unités DXF sont en mm ($INSUNITS = 4)."""
    from app.services.dxf_service import generate_dxf

    doc = _parse_dxf(generate_dxf(CONTOUR_4PTS, width_mm=30.5, height_mm=20.0))
    assert doc.header.get("$INSUNITS") == 4


def test_generate_dxf_bounding_box_matches_dimensions() -> None:
    """AC#2 (NFR-I1) — La boîte englobante = width_mm × height_mm."""
    from app.services.dxf_service import generate_dxf

    width_mm, height_mm = 30.5, 20.0
    doc = _parse_dxf(generate_dxf(CONTOUR_4PTS, width_mm=width_mm, height_mm=height_mm))
    polyline = next(e for e in doc.modelspace() if e.dxftype() == "LWPOLYLINE")

    xs = [pt[0] for pt in polyline.get_points()]
    ys = [pt[1] for pt in polyline.get_points()]
    assert abs((max(xs) - min(xs)) - width_mm) < 0.1
    assert abs((max(ys) - min(ys)) - height_mm) < 0.1


def test_generate_dxf_raises_on_fewer_than_3_points() -> None:
    """AC#4 — Moins de 3 points → ValueError."""
    from app.services.dxf_service import generate_dxf

    with pytest.raises(ValueError, match="au moins 3 points"):
        generate_dxf([[0.1, 0.2], [0.9, 0.8]], width_mm=30.0, height_mm=20.0)


def test_generate_dxf_works_with_3_points() -> None:
    """AC#1 — Triangle (3 points) — cas minimal valide."""
    from app.services.dxf_service import generate_dxf

    result = generate_dxf([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]], width_mm=10.0, height_mm=10.0)
    assert isinstance(result, bytes)
