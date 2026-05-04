"""
export_road_raw.py — raw 도로중심선 N3L_A0020000_11 을 viewer 로 손실 없이 export

기존 export_viewer_data.py 는 link_to_block 결과(boundary/edge/outside)에 따라
inside(블록 내부 골목, 전체 414k 중 약 330k 개)를 viewer 에서 제거했음.
도로 위계를 raw 그대로 보고 싶다는 요구에 따라 414k link 모두 보존.

산출:
  data/viewer/roads_raw.fgb   - 414k link, 슬림 컬럼 (lanes, width, scls, rddv, name)
  manifest.json                - road_raw_count 갱신
"""
import os, json, time
import geopandas as gpd
from shapely import set_precision

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
CL = os.path.join(ROOT, 'data', 'raw', 'roads', 'centerline', 'N3L_A0020000_11.shp')
OUT = os.path.join(ROOT, 'data', 'viewer')
OUT_FGB = os.path.join(OUT, 'roads_raw.fgb')
MANIFEST = os.path.join(OUT, 'manifest.json')

t0 = time.time()
print('[1/3] Loading raw centerline...')
cl = gpd.read_file(CL, columns=['UFID', 'NAME', 'RDDV', 'RDLN', 'RVWD', 'SCLS'])
print(f'  rows={len(cl)}  crs={cl.crs}')

print('[2/3] Slimming + reprojecting (5179 → 4326)...')
cl = cl.to_crs(4326).reset_index(drop=True)
cl.insert(0, 'link_id', range(len(cl)))
cl = cl.rename(columns={'SCLS': 'scls', 'RDDV': 'rddv',
                        'RDLN': 'lanes', 'RVWD': 'width_m', 'NAME': 'name'})
cl['name']    = cl['name'].fillna('').astype(str)
cl['scls']    = cl['scls'].fillna('').astype(str)
cl['rddv']    = cl['rddv'].fillna('').astype(str)
cl['lanes']   = cl['lanes'].fillna(0).astype('int16')
cl['width_m'] = cl['width_m'].fillna(0).astype('float32')
# UFID 그대로 보존 (디버그용)
cl['ufid'] = cl['UFID'].fillna('').astype(str)
cl = cl[['link_id', 'ufid', 'scls', 'rddv', 'lanes', 'width_m', 'name', 'geometry']]
# 좌표 정밀도 1e-5 (~ 1m). 서울 화면에서 시각적으로 충분.
cl['geometry'] = set_precision(cl.geometry.values, 1e-5)
# set_precision 으로 짧은 segment 가 한 점으로 collapse → empty geometry. 필터링.
before = len(cl)
cl = cl[~cl.geometry.is_empty & cl.geometry.notna()].reset_index(drop=True)
print(f'  dropped empty geom: {before - len(cl)} (kept {len(cl)})')

# 위계 빠른 통계
print('  scls top:')
print(cl['scls'].value_counts().head(8).to_string())
print('  lanes:')
print(cl['lanes'].describe().to_string())
print('  width_m:')
print(cl['width_m'].describe().to_string())

print('[3/3] Writing FlatGeobuf...')
if os.path.exists(OUT_FGB):
    os.remove(OUT_FGB)
cl.to_file(OUT_FGB, driver='FlatGeobuf')
print(f'  {OUT_FGB}  {len(cl)} feats  {os.path.getsize(OUT_FGB)/1e6:.1f} MB')

# manifest 갱신
manifest = {}
if os.path.exists(MANIFEST):
    with open(MANIFEST, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
manifest['road_raw_count'] = int(len(cl))
manifest['road_raw_lanes_quantiles'] = {
    'p50': int(cl['lanes'].quantile(0.5)),
    'p90': int(cl['lanes'].quantile(0.9)),
    'p99': int(cl['lanes'].quantile(0.99)),
    'max': int(cl['lanes'].max()),
}
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f'\nDone in {time.time()-t0:.1f}s')
