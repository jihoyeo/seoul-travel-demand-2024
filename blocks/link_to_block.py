"""
link_to_block.py — 도로중심선 링크 ↔ 블록 귀속 매핑

전략:
- 블록은 OA dissolve 결과이므로 도로 면적이 양옆 OA 중 한쪽으로 흡수돼 있음.
  중심선 ±고정 거리 점만 보면 광로(폭 30m+)에서는 양쪽 모두 흡수한 OA 안에
  들어가버려 `inside` 로 오분류 → 블록 경계로 잡혀야 할 간선이 누락.
- 해법: 오프셋을 **링크별 도로폭에 비례** 시킴 (= RVWD/2 + 여유 1m).
  광로면 ±16m, 좁은 골목이면 ±1.5m 로 양옆 점이 항상 도로 가장자리 바깥 OA 에
  떨어지게 함.

각 링크의 양쪽 오프셋 점이 어느 블록에 들어가는지 sjoin으로 확인:
    · 양쪽이 같은 블록 → 골목 (그 블록에 weight=1.0)
    · 양쪽이 다른 블록 → 경계 (각 블록에 weight=0.5)
    · 한쪽만 매칭 → 가장자리/외부 인접 (매칭된 블록에 weight=1.0)
    · 둘 다 매칭 안 됨 → 서울 외곽/한강 등 (block_id=NaN, weight=1.0)

입력:  data/raw/roads/centerline/N3L_A0020000_11.shp  (그래프 골격, EPSG:5179)
       data/derived/seoul_blocks.fgb                  (블록 폴리곤, EPSG:5179)
출력:  data/derived/link_to_block.parquet
         schema: link_id (int), block_id (Int64, nullable),
                 weight (float, 0.5 or 1.0),
                 side ('inside' | 'left' | 'right' | 'outside')
"""
import os
import time
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
CL = os.path.join(ROOT, 'data', 'raw', 'roads', 'centerline', 'N3L_A0020000_11.shp')
BLK = os.path.join(ROOT, 'data', 'derived', 'seoul_blocks.fgb')
OUT = os.path.join(ROOT, 'data', 'derived', 'link_to_block.parquet')

OFFSET_BASE_M = 1.5  # 좁은 도로 (폭 정보 없음/0) 기본 오프셋
OFFSET_PAD_M  = 1.0  # 도로 가장자리에서 추가로 더 떨어뜨릴 여유

t0 = time.time()
print('[1/5] Loading centerline + blocks...')
cl = gpd.read_file(CL)
if cl.crs is None or cl.crs.to_epsg() != 5179:
    cl = cl.to_crs(epsg=5179)
cl = cl.reset_index(drop=True)
cl.insert(0, 'link_id', range(len(cl)))
# Per-link offset: 도로 폭 (RVWD) 절반 + padding. 도로 폭 정보가 없거나
# 비정상이면 BASE 오프셋. 50m 광로면 ±26m 까지 점이 밀려 양옆 OA 에 들어감.
rvwd = cl['RVWD'].fillna(0).astype(float).clip(lower=0, upper=120).values
offset_arr = np.maximum(OFFSET_BASE_M, rvwd / 2.0 + OFFSET_PAD_M).astype('float64')
print(f'  links={len(cl)} crs={cl.crs}')
print(f'  offset per link: min={offset_arr.min():.2f}m  median={np.median(offset_arr):.2f}m  '
      f'p90={np.percentile(offset_arr, 90):.2f}m  max={offset_arr.max():.2f}m')

blk = gpd.read_file(BLK)[['block_id', 'geometry']]
print(f'  blocks={len(blk)}')

print('[2/5] Computing midpoint and tangent...')
# Use shapely vectorized: get midpoint and a near-midpoint to get tangent direction.
mids = cl.geometry.interpolate(0.5, normalized=True)
# A small fraction along the line for tangent (length-aware)
EPS_FRAC = 0.4  # 0.4 ~ 0.5 to avoid kinks at exact midpoint
near = cl.geometry.interpolate(EPS_FRAC, normalized=True)

dx = mids.x.values - near.x.values
dy = mids.y.values - near.y.values
L = np.hypot(dx, dy)
L[L < 1e-9] = 1.0  # avoid div-by-zero (degenerate links)
# Unit normal (rotate tangent 90deg): n = (-dy, dx) / L
nx = -dy / L
ny = dx / L

mx = mids.x.values
my = mids.y.values

print('[3/5] Building offset point GeoDataFrames (width-aware)...')
left_pts = gpd.GeoDataFrame(
    {'link_id': cl['link_id']},
    geometry=gpd.points_from_xy(mx + nx * offset_arr, my + ny * offset_arr),
    crs=5179,
)
right_pts = gpd.GeoDataFrame(
    {'link_id': cl['link_id']},
    geometry=gpd.points_from_xy(mx - nx * offset_arr, my - ny * offset_arr),
    crs=5179,
)

print('[4/5] Spatial join (point-in-polygon)...')
t1 = time.time()
left_j = gpd.sjoin(left_pts, blk, how='left', predicate='within')[['link_id', 'block_id']]
right_j = gpd.sjoin(right_pts, blk, how='left', predicate='within')[['link_id', 'block_id']]
# In case a point lies exactly on a boundary and matches 2 blocks, take first
left_j = left_j.drop_duplicates(subset='link_id', keep='first').rename(columns={'block_id': 'left_block'})
right_j = right_j.drop_duplicates(subset='link_id', keep='first').rename(columns={'block_id': 'right_block'})
print(f'  sjoin done in {time.time()-t1:.1f}s')

merged = left_j.merge(right_j, on='link_id', how='outer')

# Build long-format mapping
rows = []
inside = same = boundary = edge = outside = 0
for _, r in merged.iterrows():
    lid = int(r['link_id'])
    lb = r['left_block']
    rb = r['right_block']
    lb_isnan = pd.isna(lb)
    rb_isnan = pd.isna(rb)
    if not lb_isnan and not rb_isnan:
        if lb == rb:
            rows.append((lid, int(lb), 1.0, 'inside'))
            inside += 1
        else:
            rows.append((lid, int(lb), 0.5, 'left'))
            rows.append((lid, int(rb), 0.5, 'right'))
            boundary += 1
    elif not lb_isnan and rb_isnan:
        rows.append((lid, int(lb), 1.0, 'left'))
        edge += 1
    elif lb_isnan and not rb_isnan:
        rows.append((lid, int(rb), 1.0, 'right'))
        edge += 1
    else:
        rows.append((lid, pd.NA, 1.0, 'outside'))
        outside += 1

out = pd.DataFrame(rows, columns=['link_id', 'block_id', 'weight', 'side'])
out['link_id'] = out['link_id'].astype('int64')
out['block_id'] = out['block_id'].astype('Int64')
out['weight'] = out['weight'].astype('float32')

print(f'\n  Link classification:')
print(f'    inside (block 내부 골목길)        : {inside:>7}')
print(f'    boundary (양옆 다른 블록 = 간선)   : {boundary:>7}')
print(f'    edge (한쪽만 블록, 외곽)          : {edge:>7}')
print(f'    outside (둘 다 외부)              : {outside:>7}')
print(f'    total links                       : {inside+boundary+edge+outside:>7}')

print('[5/5] Saving...')
out.to_parquet(OUT, index=False)
print(f'  {OUT}  ({os.path.getsize(OUT)/1e6:.1f} MB, {len(out)} rows)')

print(f'\nDone in {time.time()-t0:.1f}s.')
