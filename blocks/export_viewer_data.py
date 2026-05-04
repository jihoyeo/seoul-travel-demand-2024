"""
export_viewer_data.py — deck.gl viewer용 데이터 산출 (LOD 분할 + 슬림화)

산출:
  blocks/viewer/blocks.fgb      - 블록 폴리곤 (WGS84)
  blocks/viewer/arterial.fgb    - boundary 도로 (간선, 줌 무관 항상 로드)
  blocks/viewer/local.fgb       - inside 도로 (블록 내부 골목, 줌 13+에서만)
  blocks/viewer/aux.fgb         - edge + outside (줌 14+에서만)
  blocks/viewer/manifest.json   - 색상 범례, viewport center, LOD 임계값
"""
import os, json, time
import geopandas as gpd
import pandas as pd
from shapely import set_precision

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
CL = os.path.join(ROOT, 'data', 'raw', 'roads', 'centerline', 'N3L_A0020000_11.shp')
BLK_FGB = os.path.join(ROOT, 'data', 'derived', 'seoul_blocks.fgb')
MAP = os.path.join(ROOT, 'data', 'derived', 'link_to_block.parquet')
OUT = os.path.join(ROOT, 'data', 'viewer')
os.makedirs(OUT, exist_ok=True)

t0 = time.time()
print('[1/5] Loading...')
cl = gpd.read_file(CL)
if cl.crs.to_epsg() != 5179:
    cl = cl.to_crs(5179)
cl = cl.reset_index(drop=True)
cl.insert(0, 'link_id', range(len(cl)))
mp = pd.read_parquet(MAP)
print(f'  links={len(cl)}, mappings={len(mp)}')

print('[2/5] Per-link primary side label...')
counts = mp.groupby('link_id').size()
mp['_dup'] = mp['link_id'].map(counts)
def label(r):
    if r['_dup'] >= 2:
        return 'boundary'
    if r['side'] in ('left', 'right'):
        return 'edge'
    return r['side']
mp['kind'] = mp.apply(label, axis=1)
side_pri = {'boundary': 4, 'inside': 3, 'left': 2, 'right': 2, 'outside': 1}
mp['_pri'] = mp['side'].map(side_pri)
primary = (mp.sort_values(['link_id', '_pri'], ascending=[True, False])
             .drop_duplicates('link_id')[['link_id', 'block_id', 'kind']])
print(primary['kind'].value_counts().to_string())

print('[3/5] Joining + slimming + reprojecting...')
roads = cl[['link_id', 'SCLS', 'RDDV', 'RDLN', 'RVWD', 'NAME', 'geometry']].merge(
    primary, on='link_id', how='left')
roads['kind'] = roads['kind'].fillna('outside')
roads['block_id'] = roads['block_id'].astype('Int64')
roads = roads.rename(columns={'SCLS': 'scls', 'RDDV': 'rddv',
                              'RDLN': 'lanes', 'RVWD': 'width_m',
                              'NAME': 'name'})
# Slim: drop nullables, shorter strings
roads['name'] = roads['name'].fillna('').astype(str)
roads['lanes'] = roads['lanes'].fillna(0).astype('int16')
roads['width_m'] = roads['width_m'].fillna(0).astype('float32')
roads['scls'] = roads['scls'].fillna('').astype(str)
roads['rddv'] = roads['rddv'].fillna('').astype(str)
roads_wgs = roads.to_crs(4326)
# Reduce coordinate precision to ~10cm (6 decimal degrees) — set_precision in shapely 2
roads_wgs['geometry'] = set_precision(roads_wgs.geometry.values, 1e-6)

cols_keep = ['link_id', 'block_id', 'kind', 'scls', 'rddv',
             'lanes', 'width_m', 'name', 'geometry']

# 2-way split (inside/local 골목길은 viewer에서 제외 — 분석용 parquet에는 보존)
arterial = roads_wgs[roads_wgs['kind'] == 'boundary'][cols_keep]
aux = roads_wgs[roads_wgs['kind'].isin(['edge', 'outside'])][cols_keep]

for fn, gdf in [('arterial.fgb', arterial), ('aux.fgb', aux)]:
    p = os.path.join(OUT, fn)
    gdf.to_file(p, driver='FlatGeobuf')
    print(f'  {fn}  {len(gdf)} feats  {os.path.getsize(p)/1e6:.1f} MB')

# Remove stale local.fgb if exists
local_p = os.path.join(OUT, 'local.fgb')
if os.path.exists(local_p):
    os.remove(local_p)
    print('  removed stale local.fgb')

print('[4/5] Block aggregation...')
agg = (mp.groupby('block_id', dropna=True)
         .agg(n_links=('link_id', 'nunique'),
              n_inside=('kind', lambda s: (s == 'inside').sum()),
              n_boundary=('kind', lambda s: (s == 'boundary').sum()))
         .reset_index())
agg['block_id'] = agg['block_id'].astype('Int64')
blk = gpd.read_file(BLK_FGB).merge(agg, on='block_id', how='left').fillna(
    {'n_links': 0, 'n_inside': 0, 'n_boundary': 0})
for c in ['n_links', 'n_inside', 'n_boundary']:
    blk[c] = blk[c].astype('int32')
blk_wgs = blk.to_crs(4326)
blk_wgs['geometry'] = set_precision(blk_wgs.geometry.values, 1e-6)
out_blk = os.path.join(OUT, 'blocks.fgb')
# 모든 컬럼 보존 (aggregate_landuse 가 이미 LU 컬럼들 다 채워둔 derived/seoul_blocks.fgb 가 입력)
keep_cols = [c for c in blk_wgs.columns if c != 'geometry'] + ['geometry']
blk_wgs[keep_cols].to_file(out_blk, driver='FlatGeobuf')
print(f'  blocks.fgb  {len(blk_wgs)} feats  {os.path.getsize(out_blk)/1e6:.1f} MB  '
      f'(cols: {len(keep_cols)})')

# Center via projected centroid
blk_proj = blk.to_crs(5179)
ctr = blk_proj.geometry.centroid.unary_union.centroid
ctr_wgs = gpd.GeoSeries([ctr], crs=5179).to_crs(4326).iloc[0]

print('[5/5] manifest.json (merge update)...')
mp = os.path.join(OUT, 'manifest.json')
manifest = {}
if os.path.exists(mp):
    with open(mp, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
manifest.update({
    'center': [round(ctr_wgs.x, 6), round(ctr_wgs.y, 6)],
    'block_count': int(len(blk_wgs)),
    'arterial_count': int(len(arterial)),
    'aux_count': int(len(aux)),
    'lod_aux_min_zoom': 13,
})
manifest.setdefault('colors', {
    'boundary': [240, 100, 100, 220],
    'edge':     [240, 200, 80, 220],
    'outside':  [150, 150, 150, 160],
})
with open(mp, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f'\nDone in {time.time()-t0:.1f}s')
