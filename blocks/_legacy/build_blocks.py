"""
build_blocks.py — 간선(ROA_CLS_SE<=3)으로 polygonize한 서울 superblock

분석 단위 = TAZ에 준하는 superblock. 간선/지방도/특·광역시도(9,042건)만 경계로 사용.
시군구도로(4급)와 골목길은 superblock 내부에 위치 → 분석 시 그 블록의 통행 발생량에 귀속.

입력:  data/roads/segment/TL_SPRD_MANAGE_11_202601.shp  (EPSG:5179)
출력:  blocks/seoul_blocks.fgb                          (EPSG:5179)
       blocks/seoul_blocks_preview.geojson              (EPSG:4326, 미리보기용)
"""
import os
import time
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union, polygonize

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
SEG = os.path.join(ROOT, 'data', 'raw', 'roads', 'segment', 'TL_SPRD_MANAGE_11_202601.shp')
OUT_DIR = os.path.join(ROOT, 'data', 'derived')
OUT_FGB = os.path.join(OUT_DIR, 'seoul_blocks.fgb')
OUT_GJ = os.path.join(OUT_DIR, 'seoul_blocks_preview.geojson')
MIN_AREA_M2 = 1000.0   # superblock에서는 1000m^2 이하는 노이즈로 간주
ARTERIAL_LEVELS = {1, 2, 3}   # 고속 / 국도 / 지방도·특·광역시도

t0 = time.time()
print('[1/5] Loading 도로구간...')
seg = gpd.read_file(SEG, encoding='cp949')
print(f'  rows={len(seg)} crs={seg.crs}')
if seg.crs is None or seg.crs.to_epsg() != 5179:
    seg = seg.to_crs(epsg=5179)

before = len(seg)
seg = seg[seg['ROA_CLS_SE'].astype(int).isin(ARTERIAL_LEVELS)].copy()
print(f'  arterial filter (ROA_CLS_SE in {sorted(ARTERIAL_LEVELS)}): {len(seg)}/{before}')

print('[2/5] Unary union of all road lines...')
t1 = time.time()
merged = unary_union(seg.geometry.values)
print(f'  done in {time.time()-t1:.1f}s, type={merged.geom_type}')

print('[3/5] Polygonize...')
t1 = time.time()
polys = list(polygonize(merged))
print(f'  raw polygons={len(polys)} ({time.time()-t1:.1f}s)')

gdf = gpd.GeoDataFrame(geometry=polys, crs=5179)
gdf['area_m2'] = gdf.geometry.area
gdf['perimeter_m'] = gdf.geometry.length

print('[4/5] Filtering slivers...')
before = len(gdf)
gdf = gdf[gdf['area_m2'] >= MIN_AREA_M2].copy().reset_index(drop=True)
print(f'  kept {len(gdf)}/{before} (area >= {MIN_AREA_M2} m^2)')

gdf.insert(0, 'block_id', range(len(gdf)))
gdf['shape_idx'] = (gdf['perimeter_m'] ** 2) / (4 * 3.141592653589793 * gdf['area_m2'])

print('  Area distribution (m^2):')
print(gdf['area_m2'].describe(percentiles=[0.05, 0.5, 0.95, 0.99]).round(1).to_string())

print('[5/5] Saving...')
gdf.to_file(OUT_FGB, driver='FlatGeobuf')
print(f'  {OUT_FGB}  ({os.path.getsize(OUT_FGB)/1e6:.1f} MB)')

prev = gdf.sample(min(2000, len(gdf)), random_state=0).to_crs(epsg=4326)
prev.to_file(OUT_GJ, driver='GeoJSON')
print(f'  {OUT_GJ}  (sample {len(prev)} blocks, EPSG:4326)')

print(f'\nDone in {time.time()-t0:.1f}s. Total blocks: {len(gdf)}')
