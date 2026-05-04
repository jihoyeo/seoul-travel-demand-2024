"""
국토부 LSMD_CONT_UQ111 (도시지역 용도지역 폴리곤) → GeoJSON (dissolve 없음)
입력: data/raw/lsmd_zoning_uq111/LSMD_CONT_UQ111_11_202604.shp (EPSG:5186, 6,715 폴리곤)
출력: derived/seoul_zoning_uq111.geojson + zoning_uq111_stats.json

raw 폴리곤이 6.7k개로 작아 dissolve 없이 그대로 내보냄.
한 클래스가 여러 고시 폴리곤으로 나뉘어 보이므로 고시 단위 검수·메타 확인에 유리.
AL_D154 (필지 단위, 89.9만)와의 차이는 README 참조.
"""
import sys
import json
import re
from pathlib import Path
from collections import Counter

import geopandas as gpd
from shapely import make_valid
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SHP = ROOT / "data" / "raw" / "lsmd_zoning_uq111" / "LSMD_CONT_UQ111_11_202604.shp"
OUT_DIR = ROOT / "data" / "derived"
OUT_GEOJSON = OUT_DIR / "seoul_zoning_uq111.geojson"
OUT_STATS = OUT_DIR / "zoning_uq111_stats.json"

# AL_D154 export_zoning.py 의 ZONE_CLASS_MAP 와 동일 키 체계로 매핑.
# UQ111 의 MNUM 안에 박힌 UQAxxx 코드 1개를 추출해 분류.
ZONE_CLASS_MAP = {
    "UQA111": "전용주거",
    "UQA112": "전용주거",
    "UQA110": "전용주거",  # 미분류
    "UQA121": "일반주거_저밀(1종)",
    "UQA122": "일반주거_중밀(2종)",
    "UQA123": "일반주거_고밀(3종)",
    "UQA120": "일반주거_기타",  # 미분류
    "UQA130": "준주거",
    "UQA210": "중심·일반상업",
    "UQA220": "중심·일반상업",
    "UQA230": "근린·유통상업",
    "UQA240": "근린·유통상업",
    "UQA310": "전용공업",
    "UQA320": "일반·준공업",
    "UQA330": "일반·준공업",
    "UQA410": "보전·자연녹지",
    "UQA430": "보전·자연녹지",
    "UQA420": "생산녹지",
}

CODE_RE = re.compile(r"(UQA\d{3})")


def code_of(mnum: str) -> str:
    if not mnum:
        return ""
    m = CODE_RE.search(mnum)
    return m.group(1) if m else ""


print(f"[1/4] reading {SHP}")
gdf = gpd.read_file(SHP, encoding="cp949")
print(f"      loaded: {len(gdf):,} polygons, crs={gdf.crs}")

print("[2/4] classify + sanitize geometry (no dissolve)")
gdf["zone_code"] = gdf["MNUM"].fillna("").apply(code_of)
gdf["zone_class"] = gdf["zone_code"].map(ZONE_CLASS_MAP).fillna("미지정")

class_counts = Counter(gdf["zone_class"])
print("      class distribution:")
for k, v in class_counts.most_common():
    print(f"        {k:30s} {v:>6,}")

viz = gdf[gdf["zone_class"] != "미지정"].copy()
viz = viz[~viz.geometry.isna() & ~viz.geometry.is_empty].copy()

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

viz["geometry"] = viz.geometry.apply(to_polygon_only)
viz = viz[viz.geometry.notna() & ~viz.geometry.is_empty].copy()
viz["area_m2"] = viz.geometry.area.round().astype("int64")

print("[3/4] simplify (1m) + reproject to EPSG:4326")
viz["geometry"] = viz.geometry.simplify(tolerance=1.0, preserve_topology=True)
viz = viz.to_crs(epsg=4326)

# 메타 컬럼 보존: NTFDATE(고시일), ALIAS(별칭), REMARK(비고), SGG_OID, COL_ADM_SE(시군구코드), MNUM
out_cols = ["zone_class", "zone_code", "area_m2", "MNUM", "NTFDATE", "ALIAS", "REMARK", "COL_ADM_SE", "SGG_OID", "geometry"]
out_gdf = viz[out_cols].rename(columns={
    "MNUM": "mnum", "NTFDATE": "ntfdate", "ALIAS": "alias",
    "REMARK": "remark", "COL_ADM_SE": "sgg_cd", "SGG_OID": "sgg_oid",
})

print(f"[4/4] writing {OUT_GEOJSON}")
if OUT_GEOJSON.exists():
    OUT_GEOJSON.unlink()
try:
    import pyogrio
    pyogrio.write_dataframe(
        out_gdf, OUT_GEOJSON, driver="GeoJSON",
        layer_options={"COORDINATE_PRECISION": "6"},
    )
except Exception as e:
    print(f"      pyogrio path failed ({e}); falling back to to_file")
    out_gdf.to_file(OUT_GEOJSON, driver="GeoJSON", encoding="utf-8")

bounds = viz.total_bounds.tolist()
center = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]

# 클래스별 raw 합 (중복 고시 포함될 수 있음)
class_summary = {}
for cls, sub in viz.groupby("zone_class"):
    class_summary[cls] = {
        "polygon_count": int(len(sub)),
        "area_m2_raw_sum": int(sub["area_m2"].sum()),
    }

stats = {
    "source": str(SHP),
    "feature_total": len(gdf),
    "feature_kept_for_viz": int(len(viz)),
    "class_counts": dict(class_counts),
    "by_class": class_summary,
    "bounds_4326": bounds,
    "center_4326": center,
}
OUT_STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

size_mb = OUT_GEOJSON.stat().st_size / 1_000_000
total_km2 = sum(v["area_m2_raw_sum"] for v in class_summary.values()) / 1e6
print(f"\nsaved: {OUT_GEOJSON} ({size_mb:.2f} MB, {len(viz):,} polygons)")
print(f"saved: {OUT_STATS}")
print(f"raw area sum (중복 고시 포함 가능): {total_km2:.2f} km²")
print(f"bounds (lon,lat): {bounds}")
print(f"center (lon,lat): {center}")
