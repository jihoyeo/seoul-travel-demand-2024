"""
oa2016_to_oa2025.py — 2016 SGIS 집계구 → 2025 SGIS 집계구 면적가중 매핑.

서울 LOCAL_PEOPLE 생활인구는 2016 SGIS 경계 (TOT_REG_CD 13자리) 로 발급된다.
SGIS 통계는 2025-2Q 경계 (TOT_OA_CD 14자리). 두 경계는 약 50개 OA 가 재구획되어
직접 매칭이 불가하므로 공간 교차로 면적가중 매핑을 산출한다.

검증된 사실:
  - LOCAL_PEOPLE.집계구코드(13) ↔ raw/sgis_oa_2016/집계구.shp.TOT_REG_CD(13) 100% 일치
  - 2016 OA = 19,153 / 2025 OA = 19,097 (약 50개 재구획)
  - 2016 SHP 에 .prj 없음 → readme 기준 EPSG:5179 (UTM-K GRS80) 명시 부여

산출:
  derived/oa2016_to_oa2025.parquet
    TOT_REG_CD(str13)  TOT_OA_CD(str14)  weight(float32, 합=1 per TOT_REG_CD)
    inter_area_m2(float32)  oa2016_area_m2(float32)

면적가중 가정: 2016 OA 내부에서 인구·세대 등이 균일 분포라 가정. (population-density
weighting 으로 정교화하려면 후속에서 SGIS 인구를 조인 후 재계산.)
"""
import os, time
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import make_valid

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
OA2016 = os.path.join(ROOT, 'data', 'raw', 'sgis_oa_2016', '집계구.shp')
OA2025 = os.path.join(ROOT, 'data', 'raw', 'sgis_oa', 'bnd_oa_11_2025_2Q.shp')
OUT    = os.path.join(ROOT, 'data', 'derived', 'oa2016_to_oa2025.parquet')

t0 = time.time()
print('[1/4] Load 2016 / 2025 OA polygons...')
oa16 = gpd.read_file(OA2016, encoding='cp949')
if oa16.crs is None:
    oa16 = oa16.set_crs(5179, allow_override=True)
elif oa16.crs.to_epsg() != 5179:
    oa16 = oa16.to_crs(5179)
oa16 = oa16[['TOT_REG_CD', 'geometry']].copy()
oa16['TOT_REG_CD'] = oa16['TOT_REG_CD'].astype(str)
oa16['geometry']   = oa16.geometry.apply(make_valid)
oa16['oa2016_area_m2'] = oa16.geometry.area.astype('float32')

oa25 = gpd.read_file(OA2025)
if oa25.crs is None or oa25.crs.to_epsg() != 5179:
    oa25 = oa25.set_crs(5179, allow_override=True)
oa25 = oa25[['TOT_OA_CD', 'geometry']].copy()
oa25['TOT_OA_CD'] = oa25['TOT_OA_CD'].astype(str)
oa25['geometry']  = oa25.geometry.apply(make_valid)
print(f'  oa2016={len(oa16)}  oa2025={len(oa25)}')

print('[2/4] Spatial overlay (intersection)...')
t1 = time.time()
inter = gpd.overlay(oa16, oa25, how='intersection', keep_geom_type=True)
inter['inter_area_m2'] = inter.geometry.area.astype('float32')
# Drop sliver fragments (digitization noise). 50 m² threshold covers thin
# vertex mismatches between 2016/2025 boundaries; meaningful splits are
# always orders of magnitude larger.
inter = inter[inter['inter_area_m2'] > 50.0].copy()
print(f'  intersections (>50m^2)={len(inter)}  ({time.time()-t1:.1f}s)')

print('[3/4] Compute area-weighted weights (sum=1 per TOT_REG_CD)...')
denom = inter.groupby('TOT_REG_CD')['inter_area_m2'].sum().rename('denom')
inter = inter.merge(denom, on='TOT_REG_CD')
inter['weight'] = (inter['inter_area_m2'] / inter['denom']).astype('float32')

# Stats
n_unchanged = (inter.groupby('TOT_REG_CD').size() == 1).sum()
n_split     = (inter.groupby('TOT_REG_CD').size() >  1).sum()
print(f'  TOT_REG_CD 1:1 match = {n_unchanged}')
print(f'  TOT_REG_CD split into multiple 2025 OA = {n_split}')

uncovered = set(oa16['TOT_REG_CD']) - set(inter['TOT_REG_CD'])
if uncovered:
    print(f'  [WARN] {len(uncovered)} TOT_REG_CD with no 2025 OA overlap (will be missing): '
          f'samples={list(uncovered)[:5]}')

# weight sum check
ws = inter.groupby('TOT_REG_CD')['weight'].sum()
print(f'  weight sum: min={ws.min():.4f}  max={ws.max():.4f}  '
      f'(expect ~1.0 modulo overlay floating)')

# Dominant overlap distribution (how concentrated each 2016 OA maps to 2025)
top1 = inter.sort_values('weight', ascending=False).groupby('TOT_REG_CD')['weight'].first()
print(f'  dominant 2025 OA captures: '
      f'>=0.99 of 2016 OA in {(top1>=0.99).sum()} cases / '
      f'>=0.90 in {(top1>=0.90).sum()} / '
      f'<0.50 in {(top1<0.50).sum()}')

print('[4/4] Save...')
out = inter[['TOT_REG_CD', 'TOT_OA_CD', 'weight',
             'inter_area_m2', 'oa2016_area_m2']].reset_index(drop=True)
out['weight'] = out['weight'].astype('float32')
out.to_parquet(OUT, index=False)
print(f'  {OUT}  ({os.path.getsize(OUT)/1e6:.2f} MB, {len(out)} rows)')
print(f'\nTotal {time.time()-t0:.1f}s.')
