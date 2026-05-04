"""
oa_to_block.py — 통계청 집계구 ↔ superblock 면적가중 매핑

집계구(SGIS Output Area) 19,097개와 superblock 1,647개를 overlay 해서
"집계구 i 면적의 몇 %가 superblock j 안에 들어가는가"를 산출한다.
SGIS 인구·가구 통계(TOT_OA_CD 단위)를 superblock으로 disaggregate 할 때
이 weight 를 그대로 쓰면 된다.

설계:
- 집계구는 도로 폭까지 포함해 서울을 빠짐없이 덮지만, superblock은 간선 도로 면적이
  빠져 있어 합이 ~431 km² (집계구 합 605 km² < block 합과 차이 약 174 km²).
- 따라서 일부 집계구 면적은 어느 superblock에도 들어가지 않음 (= 도로 면적).
  block_id NaN 행으로 보존해 잔여 면적을 명시.
- 동일 키(oa_cd, block_id) 의 weight 합 = 1.0  (NaN 포함).

입력:  data/raw/sgis_oa/bnd_oa_11_2025_2Q.shp   (EPSG:5179, 폴리곤 19,097)
       data/derived/seoul_blocks.fgb            (EPSG:5179, 폴리곤 1,647)

출력:  data/derived/oa_to_block.parquet
         schema: oa_cd (str14), adm_cd (str8), block_id (Int64, nullable),
                 oa_area_m2 (float32), inter_area_m2 (float32), weight (float32)
       data/derived/seoul_oa.fgb                (EPSG:5179, geometry + oa_cd/adm_cd/major_block)
       data/viewer/oa.fgb                       (EPSG:4326, slim, viewer용)
"""
import os, time, json
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import set_precision, make_valid

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
OA  = os.path.join(ROOT, 'data', 'raw', 'sgis_oa', 'bnd_oa_11_2025_2Q.shp')
BLK = os.path.join(ROOT, 'data', 'derived', 'seoul_blocks.fgb')
OUT_MAP = os.path.join(ROOT, 'data', 'derived', 'oa_to_block.parquet')
OUT_OA  = os.path.join(ROOT, 'data', 'derived', 'seoul_oa.fgb')
VIEWER  = os.path.join(ROOT, 'data', 'viewer')
MANIFEST = os.path.join(VIEWER, 'manifest.json')

t0 = time.time()
print('[1/5] Loading...')
oa = gpd.read_file(OA)
# .prj 가 deprecated 표기라 EPSG가 None으로 잡힐 수 있음 → 강제 부여
if oa.crs is None or oa.crs.to_epsg() != 5179:
    oa = oa.set_crs(5179, allow_override=True)
oa = oa[['ADM_CD', 'TOT_OA_CD', 'geometry']].copy()
oa['ADM_CD']    = oa['ADM_CD'].astype(str)
oa['TOT_OA_CD'] = oa['TOT_OA_CD'].astype(str)
oa['geometry'] = oa.geometry.apply(make_valid)
print(f'  oa={len(oa)}  crs={oa.crs.to_epsg()}')

blk = gpd.read_file(BLK)[['block_id', 'geometry']]
if blk.crs.to_epsg() != 5179:
    blk = blk.to_crs(5179)
blk['block_id'] = blk['block_id'].astype('int64')
blk['geometry'] = blk.geometry.apply(make_valid)
print(f'  blocks={len(blk)}  crs={blk.crs.to_epsg()}')

print('[2/5] Per-OA total area...')
oa['oa_area_m2'] = oa.geometry.area.astype('float32')

print('[3/5] overlay (intersection)...')
t1 = time.time()
inter = gpd.overlay(oa, blk, how='intersection', keep_geom_type=True)
print(f'  intersection rows={len(inter)} ({time.time()-t1:.1f}s)')
inter['inter_area_m2'] = inter.geometry.area.astype('float32')

print('[4/5] Building mapping table (with road-residual rows)...')
keep = inter[['TOT_OA_CD', 'ADM_CD', 'block_id', 'oa_area_m2', 'inter_area_m2']].copy()

# 집계구별 잔여 면적 = oa_area - sum(inter) → 도로/외곽 등 어떤 block 에도 안 들어간 부분
covered = (keep.groupby('TOT_OA_CD')['inter_area_m2']
              .sum().rename('covered_m2').reset_index())
oa_meta = oa[['TOT_OA_CD', 'ADM_CD', 'oa_area_m2']].merge(covered, on='TOT_OA_CD', how='left')
oa_meta['covered_m2'] = oa_meta['covered_m2'].fillna(0).astype('float32')
oa_meta['residual_m2'] = (oa_meta['oa_area_m2'] - oa_meta['covered_m2']).clip(lower=0).astype('float32')
# 부동소수 노이즈 제거: 1 m² 미만은 버림
oa_meta = oa_meta[oa_meta['residual_m2'] >= 1.0].copy()
oa_meta['block_id'] = pd.NA
oa_meta['inter_area_m2'] = oa_meta['residual_m2']
keep = pd.concat([
    keep,
    oa_meta[['TOT_OA_CD', 'ADM_CD', 'block_id', 'oa_area_m2', 'inter_area_m2']]
], ignore_index=True)

keep['weight'] = (keep['inter_area_m2'] / keep['oa_area_m2']).astype('float32')
keep = keep.rename(columns={'TOT_OA_CD': 'oa_cd', 'ADM_CD': 'adm_cd'})
keep['oa_cd']    = keep['oa_cd'].astype(str)
keep['adm_cd']   = keep['adm_cd'].astype(str)
keep['block_id'] = keep['block_id'].astype('Int64')
keep = keep[['oa_cd', 'adm_cd', 'block_id', 'oa_area_m2', 'inter_area_m2', 'weight']]

# Sanity
ws = keep.groupby('oa_cd')['weight'].sum()
print(f'  rows={len(keep)}  unique_oa={keep["oa_cd"].nunique()}')
print(f'  weight sum per OA  min={ws.min():.4f} median={ws.median():.4f} max={ws.max():.4f}')
print(f'  rows with NaN block_id (residual): {keep["block_id"].isna().sum()}  '
      f'area={keep.loc[keep["block_id"].isna(),"inter_area_m2"].sum()/1e6:.1f} km²')

# 집계구 → 가장 큰 비중의 superblock (지배 블록) — viewer 색상용
non_null = keep.dropna(subset=['block_id'])
major = (non_null.sort_values('inter_area_m2', ascending=False)
                 .drop_duplicates('oa_cd')[['oa_cd', 'block_id']]
                 .rename(columns={'block_id': 'major_block'}))
major['major_block'] = major['major_block'].astype('Int64')

print('[5/5] Saving...')
keep.to_parquet(OUT_MAP, index=False)
print(f'  {OUT_MAP}  ({os.path.getsize(OUT_MAP)/1e6:.2f} MB)')

# OA 폴리곤 산출 (EPSG:5179) — major_block 결합
oa_out = oa[['TOT_OA_CD', 'ADM_CD', 'oa_area_m2', 'geometry']].merge(
    major, left_on='TOT_OA_CD', right_on='oa_cd', how='left'
).drop(columns=['oa_cd'])
oa_out = oa_out.rename(columns={'TOT_OA_CD': 'oa_cd', 'ADM_CD': 'adm_cd'})
oa_out['major_block'] = oa_out['major_block'].astype('Int64')
oa_out.to_file(OUT_OA, driver='FlatGeobuf')
print(f'  {OUT_OA}  ({os.path.getsize(OUT_OA)/1e6:.2f} MB, {len(oa_out)} feats)')

# Viewer 슬림 사본 (WGS84, 좌표 정밀도 1e-6)
os.makedirs(VIEWER, exist_ok=True)
oa_wgs = oa_out.to_crs(4326)
oa_wgs['geometry'] = set_precision(oa_wgs.geometry.values, 1e-6)
out_v = os.path.join(VIEWER, 'oa.fgb')
oa_wgs[['oa_cd', 'adm_cd', 'major_block', 'oa_area_m2', 'geometry']].to_file(
    out_v, driver='FlatGeobuf')
print(f'  {out_v}  ({os.path.getsize(out_v)/1e6:.2f} MB)')

# manifest 업데이트 (oa_count 추가)
if os.path.exists(MANIFEST):
    with open(MANIFEST, 'r', encoding='utf-8') as f:
        m = json.load(f)
else:
    m = {}
m['oa_count'] = int(len(oa_wgs))
m['oa_base_date'] = '2025-06-30'
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(m, f, indent=2, ensure_ascii=False)
print(f'  manifest.json updated  oa_count={m["oa_count"]}')

print(f'\nDone in {time.time()-t0:.1f}s.')
