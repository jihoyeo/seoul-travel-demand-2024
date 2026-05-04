"""
export_parcel_points.py — 필지 폴리곤을 centroid Point로 다운샘플

89.9만 폴리곤을 그리는 viewer는 무거움. 시각화 전용 보조 산출물로
representative point + 슬림 속성만 가진 FGB를 만든다.

입력:  data/derived/seoul_parcels.fgb        (Polygon, 343 MB)
출력:  data/derived/seoul_parcels_pts.fgb    (Point, ~ 40 MB 예상)

스키마: pnu, zone_class, zone_code, jimok, jimok_kind, area_m2, sgg
좌표:   EPSG:4326, 6자리. centroid 계산은 5179 투영에서 (geographic centroid 회피).
"""
import os, time, sys
from pathlib import Path

import geopandas as gpd
import pyogrio
from shapely import set_precision

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'derived' / 'seoul_parcels.fgb'
OUT = ROOT / 'data' / 'derived' / 'seoul_parcels_pts.fgb'

t0 = time.time()
print(f'[1/4] Loading {SRC.name}...')
g = gpd.read_file(SRC)
print(f'  rows={len(g):,} crs={g.crs}')

print('[2/4] Reproject 4326 → 5179, compute centroids...')
g5179 = g.to_crs(5179)
# representative_point()는 항상 폴리곤 *내부*. centroid는 빠르지만 길쭉/L자형 폴리곤에서 외부로 나갈 수 있음.
# 시각화 용도이고 89.9만건이라 centroid가 더 빠름 → 일관성 위해 centroid 사용.
pts5179 = g5179.geometry.centroid
print(f'  done ({time.time()-t0:.1f}s)')

print('[3/4] Build slim point gdf + reproject 4326...')
attrs = g[['pnu', 'zone_class', 'zone_code', 'jimok', 'jimok_kind', 'area_m2', 'sgg']].copy()
out = gpd.GeoDataFrame(attrs, geometry=pts5179, crs=5179).to_crs(4326)
out['geometry'] = set_precision(out.geometry.values, 1e-6)
out['area_m2'] = out['area_m2'].astype('int32')
out['sgg'] = out['sgg'].astype(str)

print('[4/4] Write FGB...')
if OUT.exists(): OUT.unlink()
pyogrio.write_dataframe(out, OUT, driver='FlatGeobuf')
print(f'  {OUT.name}  {os.path.getsize(OUT)/1e6:.1f} MB · {len(out):,} points')
print(f'\nDone in {time.time()-t0:.1f}s')
