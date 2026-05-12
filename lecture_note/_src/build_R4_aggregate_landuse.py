"""R4_aggregate_landuse.ipynb — blocks/aggregate_landuse.py 풀이."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbgen import MD, CODE, write_notebook

cells = [
MD("""# R4 — `block_landuse.parquet` 빌드 풀이

`blocks/aggregate_landuse.py` 풀이.

전략: 필지 centroid → block spatial join → buildable / non-buildable 분리 → zone_class 집계.
산출:
- `data/derived/block_landuse.parquet` (long format)
- `data/derived/seoul_blocks.fgb` (LU 컬럼 추가)

소요 약 30~60초."""),

MD("""## 1. 데이터 로드"""),

CODE("""import os, time
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT = r'F:\\research\\TAZ'
DATA = os.path.join(ROOT, 'data')
DRV  = os.path.join(DATA, 'derived')
PARCELS = os.path.join(DRV, 'seoul_parcels.fgb')
BLK     = os.path.join(DRV, 'seoul_blocks.fgb')

INFRA_KINDS = {
    'road':   {'도로'}, 'rail': {'철도'}, 'water': {'하천'},
    'transit':{'교통'}, 'public': {'공공','공원·공장'},
}
NON_BUILDABLE = set().union(*INFRA_KINDS.values())

t0 = time.time()
blk_raw = gpd.read_file(BLK)
keep = ['block_id','area_m2','perimeter_m','shape_idx','geometry']
blk = blk_raw[[c for c in keep if c in blk_raw.columns]].copy()
print(f'blocks : {len(blk)}')

parcels = gpd.read_file(PARCELS)
print(f'parcels: {len(parcels)}')
if parcels.crs.to_epsg() != blk.crs.to_epsg():
    parcels = parcels.to_crs(blk.crs)"""),

MD("""## 2. 필지 centroid → block spatial join"""),

CODE("""parc_pts = parcels[['zone_class','jimok_kind','area_m2','geometry']].copy()
parc_pts['geometry'] = parcels.geometry.centroid

joined = gpd.sjoin(parc_pts, blk[['block_id','geometry']],
                   how='inner', predicate='within')
joined['jimok_kind'] = joined['jimok_kind'].fillna('미지정')
print(f'matched parcels: {len(joined)}/{len(parcels)}')

build_mask = ~joined['jimok_kind'].isin(NON_BUILDABLE)
joined_build = joined[build_mask].copy()
joined_infra = joined[~build_mask].copy()
print(f'  buildable: {len(joined_build)}, non-buildable: {len(joined_infra)}')"""),

MD("""## 3. zone_class 집계 (buildable only)"""),

CODE("""g = (joined_build.groupby(['block_id','zone_class'])
                  .agg(area_m2=('area_m2','sum'))
                  .reset_index())
buildable_area = (g.groupby('block_id')['area_m2'].sum()
                   .rename('buildable_area_m2').reset_index())
g = g.merge(buildable_area, on='block_id')
g['area_share'] = g['area_m2'] / g['buildable_area_m2']

major = (g.sort_values(['block_id','area_m2'], ascending=[True, False])
           .drop_duplicates('block_id')
           [['block_id','zone_class','area_share']])
major = major.rename(columns={'zone_class':'major_lu','area_share':'major_share'})

build_counts = (joined_build.groupby('block_id').size()
                .rename('buildable_parcel_count').reset_index())

print(f'blocks with buildable: {len(major)}/{len(blk)}')
print(major['major_lu'].value_counts())"""),

MD("""## 4. infra share (5종) 집계"""),

CODE("""kind_to_cat = {}
for cat, kinds in INFRA_KINDS.items():
    for k in kinds:
        kind_to_cat[k] = cat
joined_infra['cat'] = joined_infra['jimok_kind'].map(kind_to_cat)

infra_g = (joined_infra.groupby(['block_id','cat'])
                        .agg(area_m2=('area_m2','sum'),
                             n=('cat','size'))
                        .reset_index())
infra_wide_area = infra_g.pivot(index='block_id', columns='cat', values='area_m2').fillna(0)
infra_wide_n    = infra_g.pivot(index='block_id', columns='cat', values='n').fillna(0).astype(int)
for cat in INFRA_KINDS:
    if cat not in infra_wide_area.columns: infra_wide_area[cat] = 0.0
    if cat not in infra_wide_n.columns:    infra_wide_n[cat] = 0
infra_wide_area = infra_wide_area.rename(columns={c:f'{c}_area_m2' for c in INFRA_KINDS})
infra_wide_n    = infra_wide_n.rename(columns={c:f'{c}_parcel_count' for c in INFRA_KINDS})
infra_wide = infra_wide_area.join(infra_wide_n).reset_index()

print(f'infra wide cols: {list(infra_wide.columns)[:5]}...')"""),

MD("""## 5. 블록 마스터 merge + 저장"""),

CODE("""blk = blk.merge(buildable_area, on='block_id', how='left')
blk = blk.merge(major,         on='block_id', how='left')
blk = blk.merge(build_counts,  on='block_id', how='left')
blk = blk.merge(infra_wide,    on='block_id', how='left')

blk['major_lu'] = blk['major_lu'].fillna('_없음')
blk['major_share'] = blk['major_share'].fillna(0.0).astype('float32')
blk['buildable_area_m2'] = blk['buildable_area_m2'].fillna(0.0).astype('float32')
blk['buildable_parcel_count'] = blk['buildable_parcel_count'].fillna(0).astype('int32')

for cat in INFRA_KINDS:
    a = f'{cat}_area_m2'; s = f'{cat}_share'; n = f'{cat}_parcel_count'
    blk[a] = blk[a].fillna(0.0).astype('float32')
    blk[n] = blk[n].fillna(0).astype('int32')
    blk[s] = (blk[a] / blk['area_m2'].clip(lower=1)).astype('float32')

blk['buildable_share'] = (blk['buildable_area_m2'] / blk['area_m2'].clip(lower=1)).astype('float32')

# Save back to seoul_blocks.fgb
blk.to_file(BLK, driver='FlatGeobuf')
print(f'updated : {BLK}  ({os.path.getsize(BLK)/1e6:.2f} MB)')

# block_landuse.parquet (long-format zone share, buildable only)
OUT_LU = os.path.join(DRV, 'block_landuse.parquet')
g[['block_id','zone_class','area_m2','area_share']].to_parquet(OUT_LU, index=False)
print(f'saved   : {OUT_LU}  ({os.path.getsize(OUT_LU)/1e6:.2f} MB, {len(g)} rows)')

print(f'\\nDone in {time.time()-t0:.1f}s')
print('OK')"""),
]

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'reproduce', 'R4_aggregate_landuse.ipynb')
    write_notebook(cells, out)
