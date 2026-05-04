"""
서울 용도지역 11클래스 dissolve → GeoJSON
입력: F:/research/TAZ/AL_D154_11_20260412/AL_D154_11_20260412.shp (EPSG:5186, 899,432 필지)
출력: seoul_zoning.geojson (EPSG:4326, 클래스별 dissolve)
"""
import sys
import json
from pathlib import Path
from collections import Counter

import geopandas as gpd
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SHP = ROOT / "data" / "raw" / "lsmd_zoning" / "AL_D154_11_20260412" / "AL_D154_11_20260412.shp"
OUT_DIR = ROOT / "data" / "derived"
OUT_GEOJSON = OUT_DIR / "seoul_zoning.geojson"
OUT_STATS = OUT_DIR / "zoning_stats.json"

# 우선순위가 높은(specific) 코드부터 검사. 매칭 시점에 그 코드를 primary로 채택.
# UQA1xx 주거 → UQA2xx 상업 → UQA3xx 공업 → UQA4xx 녹지 → 관리/농림/자연환경 → 도시지역 일반(폴백)
ZONE_CLASS_MAP = {
    # 전용주거
    "UQA111": "전용주거",
    "UQA112": "전용주거",
    # 일반주거
    "UQA121": "일반주거_저밀(1종)",
    "UQA122": "일반주거_중밀(2종)",
    "UQA123": "일반주거_고밀(3종)",
    # 준주거
    "UQA130": "준주거",
    # 상업
    "UQA210": "중심·일반상업",
    "UQA220": "중심·일반상업",
    "UQA230": "근린·유통상업",
    "UQA240": "근린·유통상업",
    # 공업
    "UQA310": "전용공업",
    "UQA320": "일반·준공업",
    "UQA330": "일반·준공업",
    # 녹지
    "UQA410": "보전·자연녹지",
    "UQA430": "보전·자연녹지",
    "UQA420": "생산녹지",
    # 관리·농림·자연환경 (서울엔 거의 없음)
    "UQA510": "관리·농림·자연환경",
    "UQA520": "관리·농림·자연환경",
    "UQA530": "관리·농림·자연환경",
    "UQA610": "관리·농림·자연환경",
    "UQA710": "관리·농림·자연환경",
}

# specific 코드 우선 검색 순서 (도시지역 일반 폴백은 별도 처리)
SPECIFIC_PREFIXES = ("UQA1", "UQA2", "UQA3", "UQA4", "UQA5", "UQA6", "UQA7")
GENERIC_URBAN = {"UQA01X", "UQA001", "UQA002"}


def pick_zone_class(a7: str) -> tuple[str, str]:
    """A7 코드 리스트에서 (zone_code, zone_class) 반환."""
    if not a7:
        return ("", "미지정")
    codes = [c.strip() for c in a7.split(",") if c.strip()]
    # 1) specific 코드 우선 (UQA1xx~7xx)
    for c in codes:
        if c in ZONE_CLASS_MAP:
            return (c, ZONE_CLASS_MAP[c])
    # 2) prefix만 맞는 알 수 없는 변형은 prefix-기반 fallback
    for c in codes:
        if c.startswith(SPECIFIC_PREFIXES) and len(c) >= 5:
            digit = c[3]
            if digit == "1":
                return (c, "일반주거_중밀(2종)" if c[4] == "2" else "일반주거_기타")
            if digit == "2":
                return (c, "중심·일반상업")
            if digit == "3":
                return (c, "일반·준공업")
            if digit == "4":
                return (c, "보전·자연녹지")
    # 3) 도시지역 일반 (UQA01X 등) — 세부 미지정
    for c in codes:
        if c in GENERIC_URBAN:
            return (c, "도시지역_세부미지정")
    return ("", "미지정")


print(f"[1/5] reading shapefile: {SHP}")
gdf = gpd.read_file(SHP, encoding="cp949")
print(f"      loaded: {len(gdf):,} features, crs={gdf.crs}")

print("[2/5] classifying zones from A7")
zone_codes, zone_classes = zip(*(pick_zone_class(v) for v in gdf["A7"].fillna("")))
gdf["zone_code"] = zone_codes
gdf["zone_class"] = zone_classes

class_counts = Counter(gdf["zone_class"])
print("      class distribution:")
for k, v in class_counts.most_common():
    print(f"        {k:30s} {v:>8,}")

print("[3/5] clean + dissolve by zone_class (in EPSG:5186)")
import numpy as np
import shapely
from shapely import make_valid
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection

# 도시지역_세부미지정 / 미지정은 시각화에서 빼고 별도 통계로만
viz = gdf[~gdf["zone_class"].isin(["도시지역_세부미지정", "미지정"])].copy()
viz["zone_class"] = viz["zone_class"].astype(str)

# null/empty 제거
viz = viz[~viz.geometry.isna() & ~viz.geometry.is_empty].copy()

# make_valid 후 폴리곤만 추출 (GeometryCollection → 폴리곤 부분만)
def to_polygon_only(g):
    if g is None or g.is_empty:
        return None
    if not g.is_valid:
        g = make_valid(g)
    if isinstance(g, (Polygon, MultiPolygon)):
        return g
    if isinstance(g, GeometryCollection):
        polys = [p for p in g.geoms if isinstance(p, (Polygon, MultiPolygon)) and not p.is_empty]
        if not polys:
            return None
        if len(polys) == 1:
            return polys[0]
        # flatten
        flat = []
        for p in polys:
            if isinstance(p, MultiPolygon):
                flat.extend(list(p.geoms))
            else:
                flat.append(p)
        return MultiPolygon(flat)
    return None  # LineString/Point 등

print("      sanitizing geometries (make_valid + polygon-only)...")
viz["geometry"] = viz.geometry.apply(to_polygon_only)
viz = viz[viz.geometry.notna() & ~viz.geometry.is_empty].copy()

# 면적은 dissolve 전 raw에서 계산 (5186에서)
viz["_area"] = viz.geometry.area

print("      dissolving each class via WKB round-trip + shapely.union_all...")
from shapely import wkb as _wkb
from shapely.geometry.base import BaseGeometry

def clean_array(geoms_iter):
    out = []
    bad = 0
    for g in geoms_iter:
        if g is None:
            bad += 1
            continue
        if not isinstance(g, BaseGeometry):
            bad += 1
            continue
        if g.is_empty:
            bad += 1
            continue
        # WKB roundtrip — guarantees clean shapely instance, drops Z dim if any
        try:
            out.append(_wkb.loads(_wkb.dumps(g, output_dimension=2)))
        except Exception:
            bad += 1
    return out, bad

records = []
for cls, sub in viz.groupby("zone_class", sort=False):
    geoms, bad = clean_array(sub.geometry.values)
    arr = np.empty(len(geoms), dtype=object)
    for i, g in enumerate(geoms):
        arr[i] = g
    merged = shapely.union_all(arr)
    records.append({
        "zone_class": cls,
        "parcel_count": int(len(sub)),
        "area_m2": int(round(float(sub["_area"].sum()))),
        "geometry": merged,
    })
    print(f"        {cls:30s} parcels={len(sub):>8,}  clean={len(geoms):>8,}  dropped={bad}")

dissolved = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:5186")

print("[4/5] simplify (1m in 5186) + reproject to EPSG:4326")
# 1m tolerance = 시각적 거의 무손실, 파일 크기 큰 폭 감소
dissolved["geometry"] = dissolved.geometry.simplify(tolerance=1.0, preserve_topology=True)
dissolved = dissolved.to_crs(epsg=4326)

print(f"      dissolved into {len(dissolved)} classes")

print(f"[5/5] writing {OUT_GEOJSON} (coord precision=6)")
if OUT_GEOJSON.exists():
    OUT_GEOJSON.unlink()
out_gdf = dissolved[["zone_class", "parcel_count", "area_m2", "geometry"]]
# pyogrio가 GeoJSON에서 COORDINATE_PRECISION layer-creation 옵션 지원
try:
    import pyogrio
    pyogrio.write_dataframe(
        out_gdf, OUT_GEOJSON, driver="GeoJSON",
        layer_options={"COORDINATE_PRECISION": "6"},
    )
except Exception as e:
    print(f"      pyogrio path failed ({e}); falling back to to_file")
    out_gdf.to_file(OUT_GEOJSON, driver="GeoJSON", encoding="utf-8")

bounds = dissolved.total_bounds.tolist()
center = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]

stats = {
    "source": str(SHP),
    "feature_total": len(gdf),
    "feature_kept_for_viz": int(len(viz)),
    "class_counts": dict(class_counts),
    "dissolved": [
        {
            "zone_class": r["zone_class"],
            "parcel_count": int(r["parcel_count"]),
            "area_m2": int(r["area_m2"]),
        }
        for _, r in dissolved.iterrows()
    ],
    "bounds_4326": bounds,
    "center_4326": center,
}
OUT_STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

size_mb = OUT_GEOJSON.stat().st_size / 1_000_000
print(f"\nsaved: {OUT_GEOJSON} ({size_mb:.2f} MB)")
print(f"saved: {OUT_STATS}")
print(f"bounds (lon,lat): {bounds}")
print(f"center (lon,lat): {center}")
