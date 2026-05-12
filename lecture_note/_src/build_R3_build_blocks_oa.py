"""R3_build_blocks_oa.ipynb — blocks/build_blocks_oa.py 풀이."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbgen import MD, CODE, write_notebook

cells = [
MD("""# R3 — `seoul_blocks.fgb` 빌드 풀이 (Superblock v2)

`blocks/build_blocks_oa.py` 풀이.

알고리즘:
1. arterial polygonize (`ROA_CLS_SE ∈ {1,2,3}`)
2. OA × parcels overlay → jimok_kind 비율 → 산/강 라벨
3. 도시 OA → cell max-overlap 매칭
4. dissolve → superblock

**소요 약 60초** (parcels overlay 가 대부분)."""),

MD("""## 1. 데이터 로드"""),

CODE("""import os, time
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import make_valid
from shapely.ops import polygonize, unary_union

ROOT = r'F:\\research\\TAZ'
DATA = os.path.join(ROOT, 'data')
OA_SHP  = os.path.join(DATA, 'raw', 'sgis_oa', 'bnd_oa_11_2025_2Q.shp')
SEG_SHP = os.path.join(DATA, 'raw', 'roads', 'segment', 'TL_SPRD_MANAGE_11_202601.shp')
PARC    = os.path.join(DATA, 'derived', 'seoul_parcels.fgb')

t0 = time.time()
oa = gpd.read_file(OA_SHP).set_crs(5179, allow_override=True)
oa = oa[['ADM_CD','TOT_OA_CD','geometry']].rename(
    columns={'ADM_CD':'adm_cd','TOT_OA_CD':'oa_cd'}).copy()
oa['adm_cd'] = oa['adm_cd'].astype(str)
oa['oa_cd']  = oa['oa_cd'].astype(str)
oa['geometry'] = oa.geometry.apply(make_valid)
oa = oa.reset_index(drop=True)
oa['oa_idx'] = oa.index.astype('int64')

seg = gpd.read_file(SEG_SHP, columns=['ROA_CLS_SE'])
if seg.crs.to_epsg() != 5179:
    seg = seg.to_crs(5179)
arterial = seg[seg['ROA_CLS_SE'].astype(str).isin(['1','2','3'])].reset_index(drop=True)
print(f'oa={len(oa)}  arterial={len(arterial)}')"""),

MD("""## 2. polygonize → cell"""),

CODE("""union_lines = unary_union(arterial.geometry.values)
all_cells = list(polygonize(union_lines))
cells_geom = [c for c in all_cells if c.area >= 1000.0]
print(f'cells: {len(all_cells)} raw → {len(cells_geom)} after ≥1000 m² filter')
cells_gdf = gpd.GeoDataFrame({'cell_id': np.arange(len(cells_geom), dtype='int64')},
                             geometry=cells_geom, crs=5179)"""),

MD("""## 3. OA × parcels overlay → 산/강 라벨"""),

CODE("""parc = gpd.read_file(PARC, columns=['jimok_kind','geometry'])
if parc.crs.to_epsg() != 5179:
    parc = parc.to_crs(5179)
print(f'parcels={len(parc)}')

oa_x_parc = gpd.overlay(oa[['oa_idx','geometry']],
                        parc[['jimok_kind','geometry']],
                        how='intersection', keep_geom_type=True)
oa_x_parc['ix_area'] = oa_x_parc.geometry.area
print(f'overlay rows={len(oa_x_parc)}')

ratio = (oa_x_parc.groupby(['oa_idx','jimok_kind'])['ix_area']
                  .sum().unstack(fill_value=0.0))
oa_area_arr = oa.set_index('oa_idx')['geometry'].area
for k in ratio.columns:
    ratio[k] = ratio[k] / oa_area_arr.reindex(ratio.index).values

EXCLUDE_THRESHOLD = 0.5
def label_row(r):
    if r.get('임야', 0) >= EXCLUDE_THRESHOLD: return '산지'
    if r.get('하천', 0) >= EXCLUDE_THRESHOLD: return '수계'
    return '도시'
oa_kind = ratio.apply(label_row, axis=1).rename('kind')
oa = oa.merge(oa_kind, left_on='oa_idx', right_index=True, how='left')
oa['kind'] = oa['kind'].fillna('도시')

print(f'kind dist: {oa["kind"].value_counts().to_dict()}')
oa_city = oa[oa['kind'] == '도시'].copy()"""),

MD("""## 4. 도시 OA → cell max-overlap 매칭"""),

CODE("""inter = gpd.overlay(oa_city[['oa_idx','geometry']], cells_gdf,
                    how='intersection', keep_geom_type=True)
inter['inter_area'] = inter.geometry.area
major = (inter.sort_values('inter_area', ascending=False)
              .drop_duplicates('oa_idx')[['oa_idx','cell_id']])
oa_city = oa_city.merge(major, on='oa_idx', how='left')
print(f'step A overlay match: {oa_city["cell_id"].notna().sum()}/{len(oa_city)}')

# nearest fallback for unmatched OAs
miss = oa_city[oa_city['cell_id'].isna()][['oa_idx','geometry']].copy()
if len(miss):
    near = gpd.sjoin_nearest(miss, cells_gdf, how='left', distance_col='dist_m')
    near = near.drop_duplicates('oa_idx', keep='first')[['oa_idx','cell_id','dist_m']]
    fill = dict(zip(near['oa_idx'], near['cell_id']))
    oa_city.loc[oa_city['cell_id'].isna(), 'cell_id'] = (
        oa_city.loc[oa_city['cell_id'].isna(), 'oa_idx'].map(fill))
    print(f'step B nearest fallback: {len(miss)} OA, mean dist={near["dist_m"].mean():.1f}m')

oa_city['block_id'] = oa_city['cell_id'].astype('int64')
oa_city = oa_city.drop(columns=['cell_id'])
uniq, inv = np.unique(oa_city['block_id'].values, return_inverse=True)
oa_city['block_id'] = inv.astype('int64')
K = len(uniq)
print(f'blocks={K}')

oa = oa.merge(oa_city[['oa_idx','block_id']], on='oa_idx', how='left')
oa['block_id'] = oa['block_id'].fillna(-1).astype('int64')"""),

MD("""## 5. dissolve + 저장"""),

CODE("""blk = oa_city.dissolve(by='block_id', as_index=False)[['block_id','geometry']]
blk['geometry'] = blk.geometry.apply(make_valid)
blk['area_m2'] = blk.geometry.area.astype('float32')
blk['perimeter_m'] = blk.geometry.length.astype('float32')
blk['shape_idx'] = (blk['perimeter_m'] / (2 * np.sqrt(np.pi * blk['area_m2']))).astype('float32')
oa_n = oa_city.groupby('block_id')['oa_cd'].count().rename('oa_count')
adm_n = oa_city.groupby('block_id')['adm_cd'].nunique().rename('adm_n')
blk = blk.merge(oa_n, on='block_id').merge(adm_n, on='block_id')

print(f'area median: {blk["area_m2"].median():,.0f}  total: {blk["area_m2"].sum()/1e6:.1f} km²')

OUT_BLK = os.path.join(DATA, 'derived', 'seoul_blocks.fgb')
blk.to_file(OUT_BLK, driver='FlatGeobuf')
print(f'saved : {OUT_BLK}  ({os.path.getsize(OUT_BLK)/1e6:.2f} MB)')

# oa_to_block.parquet
mp = oa[['oa_cd','adm_cd','kind','block_id']].copy()
mp['oa_area_m2']    = oa.geometry.area.astype('float32').values
mp['inter_area_m2'] = mp['oa_area_m2']
mp['weight']        = np.float32(1.0)
mp['block_id'] = mp['block_id'].astype('Int64')
OUT_MAP = os.path.join(DATA, 'derived', 'oa_to_block.parquet')
mp.to_parquet(OUT_MAP, index=False)
print(f'saved : {OUT_MAP}')

print(f'\\nTotal {time.time()-t0:.1f}s')
print('OK')"""),
]

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'reproduce', 'R3_build_blocks_oa.ipynb')
    write_notebook(cells, out)
