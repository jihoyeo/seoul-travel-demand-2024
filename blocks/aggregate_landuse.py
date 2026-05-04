"""
aggregate_landuse.py — 필지 → 블록 단위 토지이용 집계

전략:
- 필지 centroid → 블록 spatial join (필지 한 장은 한 블록에만 귀속)
- jimok_kind ∈ {도로, 철도, 하천, 교통}은 *비건축 인프라*로 분리:
    · 별도 면적비 (road_share, rail_share, water_share, transit_share, public_share)
    · zone_class 집계에서는 제외 → buildable_area_m2가 분모
- 블록 단위로 zone_class별 면적 합 → major_lu (가장 큰 면적), major_share
- 추가로 zone_class 면적비를 long-format parquet으로 저장 (모델 입력용, buildable 기준)

산출:
  data/derived/seoul_blocks.fgb 갱신
  data/derived/block_landuse.parquet  (block_id, zone_class, area_m2, area_share)  ← buildable only
  data/viewer/blocks.fgb 갱신
  data/viewer/manifest.json (lu_palette + 새 fill mode 키)
"""
import os, time, json
import geopandas as gpd
import pandas as pd
from shapely import set_precision

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
DERIVED = os.path.join(ROOT, 'data', 'derived')
VIEWER = os.path.join(ROOT, 'data', 'viewer')
PARCELS = os.path.join(DERIVED, 'seoul_parcels.fgb')
BLK = os.path.join(DERIVED, 'seoul_blocks.fgb')
OUT_BLK = BLK
OUT_LU = os.path.join(DERIVED, 'block_landuse.parquet')
VIEWER_BLK = os.path.join(VIEWER, 'blocks.fgb')
MANIFEST = os.path.join(VIEWER, 'manifest.json')

# 비건축 인프라 jimok_kind. 이들은 zone_class mix 집계에서 제외하고 별도 share 변수.
INFRA_KINDS = {
    'road':   {'도로'},
    'rail':   {'철도'},
    'water':  {'하천'},
    'transit':{'교통'},
    'public': {'공공', '공원·공장'},   # 학교/종교/공원 등 대규모 공공시설 — 발생 패턴이 일반 토지와 달라 별도
}
# 통행 발생 모델의 "건축 가능 토지" = 위 인프라/공공 *외* 모든 jimok_kind
NON_BUILDABLE = set().union(*INFRA_KINDS.values())

LU_COLOR = {
    '전용주거':              [255, 230, 153, 200],
    '일반주거_저밀(1종)':     [255, 200, 120, 200],
    '일반주거_중밀(2종)':     [255, 165,  80, 200],
    '일반주거_고밀(3종)':     [225, 120,  50, 200],
    '일반주거_기타':          [220, 150,  90, 200],
    '준주거':                [200,  90, 100, 200],
    '중심·일반상업':          [220,  60,  60, 200],
    '근린·유통상업':          [240, 110, 140, 200],
    '전용공업':              [120,  90, 200, 200],
    '일반·준공업':            [150, 110, 220, 200],
    '보전·자연녹지':          [110, 180, 110, 200],
    '생산녹지':              [160, 210, 100, 200],
    '관리·농림·자연환경':      [160, 200, 160, 200],
    '도시지역_세부미지정':     [180, 180, 180, 180],
    '미지정':                [120, 120, 120, 150],
    '_없음':                 [60,  60,  60, 100],
}

t0 = time.time()
print('[1/6] Loading blocks + parcels...')
blk_raw = gpd.read_file(BLK)
print(f'  blocks={len(blk_raw)} crs={blk_raw.crs}')

# 기존 토지이용 컬럼 모두 제거 (재계산하므로) — geometry/원래 형상 변수만 유지
keep = ['block_id', 'area_m2', 'perimeter_m', 'shape_idx', 'geometry']
blk = blk_raw[[c for c in keep if c in blk_raw.columns]].copy()
blk_area = blk[['block_id', 'area_m2']].rename(columns={'area_m2': 'block_area_m2'})

parcels = gpd.read_file(PARCELS)
print(f'  parcels={len(parcels)} crs={parcels.crs}')
if parcels.crs.to_epsg() != blk.crs.to_epsg():
    parcels = parcels.to_crs(blk.crs)

print('[2/6] Spatial join (parcel centroid → block)...')
t1 = time.time()
parc_pts = parcels[['zone_class', 'jimok_kind', 'area_m2', 'geometry']].copy()
parc_pts['geometry'] = parcels.geometry.centroid
joined = gpd.sjoin(parc_pts, blk[['block_id', 'geometry']],
                   how='inner', predicate='within')
joined['jimok_kind'] = joined['jimok_kind'].fillna('미지정')
print(f'  matched parcels: {len(joined)}/{len(parcels)} ({time.time()-t1:.1f}s)')

# 비건축/건축 분리
build_mask = ~joined['jimok_kind'].isin(NON_BUILDABLE)
joined_build = joined[build_mask].copy()
joined_infra = joined[~build_mask].copy()
print(f'  buildable parcels: {len(joined_build)}, non-buildable: {len(joined_infra)}')

print('[3/6] Aggregating zone_class (buildable only)...')
g = (joined_build.groupby(['block_id', 'zone_class'])
                  .agg(area_m2=('area_m2', 'sum'))
                  .reset_index())
buildable_area = (g.groupby('block_id')['area_m2'].sum()
                   .rename('buildable_area_m2').reset_index())
g = g.merge(buildable_area, on='block_id')
g['area_share'] = g['area_m2'] / g['buildable_area_m2']

# Major LU (buildable 면적 기준)
major = (g.sort_values(['block_id', 'area_m2'], ascending=[True, False])
           .drop_duplicates('block_id')
           [['block_id', 'zone_class', 'area_share']])
major = major.rename(columns={'zone_class': 'major_lu', 'area_share': 'major_share'})

# 건축 가능 필지 수
build_counts = (joined_build.groupby('block_id')
                              .size().rename('buildable_parcel_count').reset_index())

print(f'  blocks with buildable parcels: {len(major)}/{len(blk)}')
print('  major LU distribution:')
print(major['major_lu'].value_counts().to_string())

print('[4/6] Aggregating infra kinds (road/rail/water/transit/public)...')
# infra category mapping
kind_to_cat = {}
for cat, kinds in INFRA_KINDS.items():
    for k in kinds:
        kind_to_cat[k] = cat
joined_infra['cat'] = joined_infra['jimok_kind'].map(kind_to_cat)
infra_g = (joined_infra.groupby(['block_id', 'cat'])
                        .agg(area_m2=('area_m2', 'sum'),
                             n=('cat', 'size'))
                        .reset_index())
# pivot to wide
infra_wide_area = infra_g.pivot(index='block_id', columns='cat', values='area_m2').fillna(0)
infra_wide_n = infra_g.pivot(index='block_id', columns='cat', values='n').fillna(0).astype(int)
for cat in INFRA_KINDS:
    if cat not in infra_wide_area.columns:
        infra_wide_area[cat] = 0.0
    if cat not in infra_wide_n.columns:
        infra_wide_n[cat] = 0
infra_wide_area = infra_wide_area.rename(columns={c: f'{c}_area_m2' for c in INFRA_KINDS})
infra_wide_n = infra_wide_n.rename(columns={c: f'{c}_parcel_count' for c in INFRA_KINDS})
infra_wide = infra_wide_area.join(infra_wide_n).reset_index()

print('  infra totals (m²):')
for cat in INFRA_KINDS:
    col = f'{cat}_area_m2'
    print(f'    {col:25s} {infra_wide[col].sum():>13,.0f}')

print('[5/6] Building block fgb merge...')
blk = blk.merge(buildable_area, on='block_id', how='left')
blk = blk.merge(major, on='block_id', how='left')
blk = blk.merge(build_counts, on='block_id', how='left')
blk = blk.merge(infra_wide, on='block_id', how='left')

# 결측 채우기
blk['major_lu'] = blk['major_lu'].fillna('_없음')
blk['major_share'] = blk['major_share'].fillna(0.0).astype('float32')
blk['buildable_area_m2'] = blk['buildable_area_m2'].fillna(0.0).astype('float32')
blk['buildable_parcel_count'] = blk['buildable_parcel_count'].fillna(0).astype('int32')

# share = infra_area / 블록 총 면적
for cat in INFRA_KINDS:
    a = f'{cat}_area_m2'
    s = f'{cat}_share'
    n = f'{cat}_parcel_count'
    blk[a] = blk[a].fillna(0.0).astype('float32')
    blk[n] = blk[n].fillna(0).astype('int32')
    blk[s] = (blk[a] / blk['area_m2'].clip(lower=1)).astype('float32')

# 추가: buildable_share (건축 가능 면적 / 블록 총 면적). 0~1.
blk['buildable_share'] = (blk['buildable_area_m2'] / blk['area_m2'].clip(lower=1)).astype('float32')

# Save 5179 master
blk.to_file(OUT_BLK, driver='FlatGeobuf')
print(f'  {OUT_BLK}  ({os.path.getsize(OUT_BLK)/1e6:.2f} MB)')

# Long-format zone_class share (buildable 기준) — 모델 입력
print('[6/6] Writing block_landuse.parquet (long, buildable only)...')
g[['block_id', 'zone_class', 'area_m2', 'area_share']].to_parquet(OUT_LU, index=False)
print(f'  {OUT_LU}  ({os.path.getsize(OUT_LU)/1e6:.2f} MB, {len(g)} rows)')

# WGS84 viewer copy
blk_wgs = blk.to_crs(4326)
blk_wgs['geometry'] = set_precision(blk_wgs.geometry.values, 1e-6)
viewer_cols = [
    'block_id', 'area_m2', 'perimeter_m', 'shape_idx',
    'major_lu', 'major_share',
    'buildable_area_m2', 'buildable_share', 'buildable_parcel_count',
    'road_share', 'rail_share', 'water_share', 'transit_share', 'public_share',
    'road_area_m2', 'rail_area_m2', 'water_area_m2', 'transit_area_m2', 'public_area_m2',
    'geometry'
]
viewer_cols = [c for c in viewer_cols if c in blk_wgs.columns]
blk_wgs[viewer_cols].to_file(VIEWER_BLK, driver='FlatGeobuf')
print(f'  {VIEWER_BLK}  ({os.path.getsize(VIEWER_BLK)/1e6:.2f} MB)')

# Manifest patch
manifest = json.load(open(MANIFEST, 'r', encoding='utf-8'))
manifest['lu_palette'] = LU_COLOR
manifest['lu_classes_in_data'] = sorted(blk['major_lu'].unique().tolist())
manifest['fill_modes'] = [
    'major_lu', 'major_share',
    'buildable_share',
    'road_share', 'rail_share', 'water_share', 'public_share',
    'area', 'none'
]
json.dump(manifest, open(MANIFEST, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print(f'  manifest.json patched (lu_palette + fill_modes)')

print(f'\nDone in {time.time()-t0:.1f}s')
