"""
서울 용도지역 — 필지 단위 보존 (no dissolve).

입력:  AL_D154_11_20260412.shp  (EPSG:5186, 899,432필지)
출력:  seoul_parcels.fgb        (FlatGeobuf, EPSG:4326)
       seoul_parcels_sample.geojson  (앞 1,000개, 확인용)

스키마: pnu(A0), zone_class, zone_code, jimok, jimok_kind, area_m2, sgg(시군구코드)
좌표: 6자리, simplify(0.3m, in 5186)
"""
import re
import sys
from pathlib import Path
from collections import Counter

import geopandas as gpd
import pyogrio
from shapely import make_valid
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SHP = ROOT / "data" / "raw" / "lsmd_zoning" / "AL_D154_11_20260412" / "AL_D154_11_20260412.shp"
OUT_DIR = ROOT / "data" / "derived"
OUT_FGB = OUT_DIR / "seoul_parcels.fgb"
OUT_SAMPLE = OUT_DIR / "seoul_parcels_sample.geojson"

# export_zoning.py와 동일한 분류
ZONE_CLASS_MAP = {
    "UQA111": "전용주거", "UQA112": "전용주거",
    "UQA121": "일반주거_저밀(1종)",
    "UQA122": "일반주거_중밀(2종)",
    "UQA123": "일반주거_고밀(3종)",
    "UQA130": "준주거",
    "UQA210": "중심·일반상업", "UQA220": "중심·일반상업",
    "UQA230": "근린·유통상업", "UQA240": "근린·유통상업",
    "UQA310": "전용공업",
    "UQA320": "일반·준공업", "UQA330": "일반·준공업",
    "UQA410": "보전·자연녹지", "UQA430": "보전·자연녹지",
    "UQA420": "생산녹지",
    "UQA510": "관리·농림·자연환경", "UQA520": "관리·농림·자연환경",
    "UQA530": "관리·농림·자연환경",
    "UQA610": "관리·농림·자연환경", "UQA710": "관리·농림·자연환경",
}
SPECIFIC_PREFIXES = ("UQA1", "UQA2", "UQA3", "UQA4", "UQA5", "UQA6", "UQA7")
GENERIC_URBAN = {"UQA01X", "UQA001", "UQA002"}

# 지목 → 대분류. 한국 토지대장 28종 지목 코드 약자 기준.
# A6 컬럼의 마지막 한글 부분이 지목 (예 "336-1 도" → "도", "473-1대" → "대").
_JIMOK_RE = re.compile(r"[가-힣]+\s*$")
JIMOK_KIND = {
    # 도로/하천/철도/구거 = 비건축, 교통·수자원 인프라
    "도": "도로", "도도": "도로",
    "철": "철도", "산도": "도로", "산철": "철도",
    "천": "하천", "구": "하천", "유": "하천",
    # 건축/생활 토지 = 일반
    "대": "대지",
    # 농지·임야·녹지
    "전": "농지", "답": "농지", "과": "농지", "목": "농지",
    "임": "임야", "산임": "임야",
    # 기타 비건축
    "공": "공원·공장", "체": "공원·공장",
    "묘": "기타", "주": "기타", "장": "기타", "잡": "기타",
    "학": "공공", "종": "공공", "사": "공공", "제": "공공",
    "차": "교통", "수": "기타",
}


def extract_jimok(a6: str) -> tuple[str, str]:
    """A6에서 지목 한글 부분과 대분류를 추출."""
    if not a6:
        return ("", "미지정")
    m = _JIMOK_RE.search(a6)
    if not m:
        return ("", "미지정")
    j = m.group(0).strip()
    return (j, JIMOK_KIND.get(j, "기타"))


def pick_zone_class(a7: str) -> tuple[str, str]:
    if not a7:
        return ("", "미지정")
    codes = [c.strip() for c in a7.split(",") if c.strip()]
    for c in codes:
        if c in ZONE_CLASS_MAP:
            return (c, ZONE_CLASS_MAP[c])
    for c in codes:
        if c.startswith(SPECIFIC_PREFIXES) and len(c) >= 5:
            d = c[3]
            if d == "1":
                return (c, "일반주거_중밀(2종)" if c[4] == "2" else "일반주거_기타")
            if d == "2":
                return (c, "중심·일반상업")
            if d == "3":
                return (c, "일반·준공업")
            if d == "4":
                return (c, "보전·자연녹지")
    for c in codes:
        if c in GENERIC_URBAN:
            return (c, "도시지역_세부미지정")
    return ("", "미지정")


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
        flat = []
        for p in polys:
            if isinstance(p, MultiPolygon):
                flat.extend(list(p.geoms))
            else:
                flat.append(p)
        return MultiPolygon(flat)
    return None


print(f"[1/5] reading {SHP}")
gdf = gpd.read_file(SHP, encoding="cp949")
print(f"      {len(gdf):,} features, crs={gdf.crs}")

print("[2/5] classifying zones + jimok")
codes, classes = zip(*(pick_zone_class(v) for v in gdf["A7"].fillna("")))
gdf["zone_code"] = codes
gdf["zone_class"] = classes
print("      zone class distribution:")
for k, v in Counter(classes).most_common():
    print(f"        {k:30s} {v:>8,}")

jimoks, jimok_kinds = zip(*(extract_jimok(v) for v in gdf["A6"].fillna("")))
gdf["jimok"] = jimoks
gdf["jimok_kind"] = jimok_kinds
print("      jimok_kind distribution:")
for k, v in Counter(jimok_kinds).most_common():
    print(f"        {k:30s} {v:>8,}")

print("[3/5] sanitizing geometries (polygon-only)")
gdf["geometry"] = gdf.geometry.apply(to_polygon_only)
gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()

print("[4/5] area + simplify(0.3m) in EPSG:5186")
gdf["area_m2"] = gdf.geometry.area.round(0).astype("int64")
gdf["geometry"] = gdf.geometry.simplify(tolerance=0.3, preserve_topology=True)
# simplify 후 None/empty 다시 정리
gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()

# 컬럼 슬림화: pnu, zone_class, zone_code, jimok, jimok_kind, area_m2, sgg
out = gdf.rename(columns={"A0": "pnu", "A12": "sgg"})[
    ["pnu", "zone_class", "zone_code", "jimok", "jimok_kind", "area_m2", "sgg", "geometry"]
].copy()

print("[5/5] reproject 4326 + write FGB")
out = out.to_crs(epsg=4326)

if OUT_FGB.exists():
    OUT_FGB.unlink()
# FlatGeobuf with spatial index (default in pyogrio)
pyogrio.write_dataframe(out, OUT_FGB, driver="FlatGeobuf")

# 샘플 GeoJSON (확인용)
if OUT_SAMPLE.exists():
    OUT_SAMPLE.unlink()
pyogrio.write_dataframe(
    out.head(1000), OUT_SAMPLE, driver="GeoJSON",
    layer_options={"COORDINATE_PRECISION": "6"},
)

fgb_mb = OUT_FGB.stat().st_size / 1_000_000
sample_kb = OUT_SAMPLE.stat().st_size / 1_000
bounds = out.total_bounds.tolist()

print(f"\nsaved: {OUT_FGB} ({fgb_mb:.2f} MB)")
print(f"saved: {OUT_SAMPLE} ({sample_kb:.1f} KB)")
print(f"bounds (lon,lat): {bounds}")
print(f"features written: {len(out):,}")
