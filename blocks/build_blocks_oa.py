"""
build_blocks_oa.py — Superblock v2 (polygonize barrier + OA aggregation)

알고리즘:
  1. arterial (ROA_CLS_SE ∈ {1,2,3}) endpoints SNAP (cm-단위 정밀도 누락 보정)
     → polygonize → 도로로 둘러싸인 cell 들
  2. OA × parcels overlay → OA별 jimok_kind 비율 → 산/강 OA 라벨
  3. 산(임야 ≥ 50%) / 강(하천 ≥ 50%) OA 는 분석에서 제외
  4. 도시 OA → cell max-overlap 매칭 (실패 시 sjoin_nearest fallback)
  5. 같은 cell 에 들어간 도시 OA 들 dissolve → superblock

도로명주소 segment SHP 의 디지타이징 정밀도 누락 보정:
  - 학동로↔신반포로 끝점이 0.157m, 봉은사로↔사평대로 0.247m 떨어져
    polygonize cycle 닫지 못하던 문제. 1m 톨러런스로 endpoint 클러스터링 후
    좌표 통합 → polygonize 가 cycle 을 닫음.

산출:  data/derived/seoul_blocks.fgb           (도시 superblock 만)
       data/derived/seoul_blocks_preview.geojson
       data/derived/oa_to_block.parquet         (kind, block_id)
       data/derived/seoul_oa.fgb                (kind, block_id 컬럼 포함)
       data/derived/seoul_oa_excluded.fgb       (산·강 OA 별도 보존)
"""
import os, sys, time, json
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import make_valid, set_precision
from shapely.geometry import LineString, MultiLineString
from shapely.ops import polygonize, unary_union

sys.stdout.reconfigure(line_buffering=True)

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
OA_SHP  = os.path.join(ROOT, 'data', 'raw', 'sgis_oa', 'bnd_oa_11_2025_2Q.shp')
SEG_SHP = os.path.join(ROOT, 'data', 'raw', 'roads', 'segment', 'TL_SPRD_MANAGE_11_202601.shp')
PARC    = os.path.join(ROOT, 'data', 'derived', 'seoul_parcels.fgb')

OUT_BLK     = os.path.join(ROOT, 'data', 'derived', 'seoul_blocks.fgb')
OUT_PREVIEW = os.path.join(ROOT, 'data', 'derived', 'seoul_blocks_preview.geojson')
OUT_MAP     = os.path.join(ROOT, 'data', 'derived', 'oa_to_block.parquet')
OUT_OA      = os.path.join(ROOT, 'data', 'derived', 'seoul_oa.fgb')
OUT_EXCL    = os.path.join(ROOT, 'data', 'derived', 'seoul_oa_excluded.fgb')
VIEWER      = os.path.join(ROOT, 'data', 'viewer')
VIEWER_OA   = os.path.join(VIEWER, 'oa.fgb')
MANIFEST    = os.path.join(VIEWER, 'manifest.json')

EXCLUDE_KINDS = {'임야', '하천'}   # 산·강
EXCLUDE_THRESHOLD = 0.5

SNAP_TOL_M = 1.0   # 1m 이내 떨어진 endpoint 를 같은 노드로 합침

t0 = time.time()
def log(msg): print(f'[{time.time()-t0:6.1f}s] {msg}', flush=True)

log('1/6 OA + segment load')
oa = gpd.read_file(OA_SHP)
if oa.crs is None or oa.crs.to_epsg() != 5179:
    oa = oa.set_crs(5179, allow_override=True)
oa = oa[['ADM_CD', 'TOT_OA_CD', 'geometry']].rename(
    columns={'ADM_CD':'adm_cd', 'TOT_OA_CD':'oa_cd'}).copy()
oa['adm_cd'] = oa['adm_cd'].astype(str)
oa['oa_cd']  = oa['oa_cd'].astype(str)
oa['geometry'] = oa.geometry.apply(make_valid)
oa = oa.reset_index(drop=True)
oa['oa_idx'] = oa.index.astype('int64')

seg = gpd.read_file(SEG_SHP, columns=['ROA_CLS_SE'])
if seg.crs.to_epsg() != 5179:
    seg = seg.to_crs(5179)
arterial = seg[seg['ROA_CLS_SE'].astype(str).isin(['1','2','3'])].reset_index(drop=True)
log(f'    oa={len(oa)}  arterial={len(arterial)}')

log(f'2/7 endpoint snap (tol={SNAP_TOL_M}m) + polygonize + size filter')

# Collect every line's endpoint (and intermediate vertices stay as-is). Cluster
# coordinates within SNAP_TOL_M (~ DBSCAN with grid binning) so neighbouring
# endpoints fall onto a single canonical (x, y).
all_lines = []
for g in arterial.geometry.values:
    if g is None or g.is_empty: continue
    if g.geom_type == 'LineString':
        all_lines.append(g)
    elif g.geom_type == 'MultiLineString':
        all_lines.extend(g.geoms)

# Endpoint pool (start + end of each line)
ep_xy = np.array([(ls.coords[0][0], ls.coords[0][1]) for ls in all_lines]
                 + [(ls.coords[-1][0], ls.coords[-1][1]) for ls in all_lines])
log(f'    lines={len(all_lines)}  endpoints={len(ep_xy)}')

# Grid-bucket clustering: bin endpoints into SNAP_TOL grid cells. Two endpoints in
# the same or adjacent cells within SNAP_TOL get the same canonical coord (centroid
# of their cluster). This collapses sub-meter digitization noise without merging
# truly-different intersections (which sit > SNAP_TOL apart).
from collections import defaultdict
buckets = defaultdict(list)
for i, (x, y) in enumerate(ep_xy):
    bx, by = int(x // SNAP_TOL_M), int(y // SNAP_TOL_M)
    buckets[(bx, by)].append(i)

# Union-find: merge endpoints that are within SNAP_TOL across neighbouring buckets
parent = np.arange(len(ep_xy))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[max(ra, rb)] = min(ra, rb)

for (bx, by), idxs in buckets.items():
    # candidates = this bucket + 8 neighbours
    cand = list(idxs)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0: continue
            cand.extend(buckets.get((bx + dx, by + dy), []))
    pts_here = ep_xy[idxs]
    pts_cand = ep_xy[cand]
    # pairwise compare (small bucket sizes — sub-meter, tens of points typical)
    for k, i in enumerate(idxs):
        d = np.hypot(pts_cand[:, 0] - pts_here[k, 0], pts_cand[:, 1] - pts_here[k, 1])
        for m, j in enumerate(cand):
            if d[m] <= SNAP_TOL_M:
                union(i, j)

# Canonical coord per cluster = first-seen point in the cluster
roots = np.array([find(i) for i in range(len(ep_xy))])
canon = {}
for i, r in enumerate(roots):
    canon.setdefault(r, ep_xy[i])
canon_xy = np.array([canon[r] for r in roots])

n_clusters = len(canon)
n_collapsed = len(ep_xy) - n_clusters
log(f'    endpoint clusters: {n_clusters}  (collapsed {n_collapsed} near-duplicates)')

# Rebuild lines with snapped endpoints. Start endpoint = canon_xy[i], end = canon_xy[i+L]
L = len(all_lines)
snapped_lines = []
for i, ls in enumerate(all_lines):
    coords = list(ls.coords)
    coords[0]  = (float(canon_xy[i, 0]),     float(canon_xy[i, 1]))
    coords[-1] = (float(canon_xy[i + L, 0]), float(canon_xy[i + L, 1]))
    if len(coords) >= 2 and coords[0] != coords[-1]:
        snapped_lines.append(LineString(coords))
    elif len(coords) >= 2:
        # collapsed to a point — drop
        pass

log(f'    snapped lines: {len(snapped_lines)} / {L}')

union_lines = unary_union(snapped_lines)
all_cells = list(polygonize(union_lines))
cells = [c for c in all_cells if c.area >= 1000.0]
log(f'    cells: {len(all_cells)} raw -> {len(cells)} after >=1000 m^2 filter')

cells_gdf = gpd.GeoDataFrame(
    {'cell_id': np.arange(len(cells), dtype='int64')},
    geometry=cells, crs=5179)

log('3/7 OA x parcels overlay -> jimok_kind ratio (산/강 라벨)')
parc = gpd.read_file(PARC, columns=['jimok_kind', 'geometry'])
if parc.crs.to_epsg() != 5179:
    parc = parc.to_crs(5179)
log(f'    parcels={len(parc)}')

# OA × parcel overlay (메모리·시간 절감 위해 jimok_kind 면적만 누적)
oa_x_parc = gpd.overlay(oa[['oa_idx', 'geometry']],
                        parc[['jimok_kind', 'geometry']],
                        how='intersection', keep_geom_type=True)
oa_x_parc['ix_area'] = oa_x_parc.geometry.area
log(f'    overlay rows={len(oa_x_parc)}')

ratio = (oa_x_parc.groupby(['oa_idx', 'jimok_kind'])['ix_area']
                  .sum().unstack(fill_value=0.0))
oa_area_arr = oa.set_index('oa_idx')['geometry'].area
for k in ratio.columns:
    ratio[k] = ratio[k] / oa_area_arr.reindex(ratio.index).values

# OA 라벨 결정
def label_row(r):
    if r.get('임야', 0) >= EXCLUDE_THRESHOLD: return '산지'
    if r.get('하천', 0) >= EXCLUDE_THRESHOLD: return '수계'
    return '도시'
oa_kind = ratio.apply(label_row, axis=1).rename('kind')
oa = oa.merge(oa_kind, left_on='oa_idx', right_index=True, how='left')
oa['kind'] = oa['kind'].fillna('도시')   # parcel 매칭 안 된 OA (외곽) → 도시 default

n_excl = (oa['kind'] != '도시').sum()
n_city = (oa['kind'] == '도시').sum()
excl_area = oa.loc[oa['kind']!='도시'].geometry.area.sum() / 1e6
log(f'    kind dist: {oa["kind"].value_counts().to_dict()}')
log(f'    excluded area: {excl_area:.1f} km²  (도시 OA={n_city})')

oa_city = oa[oa['kind'] == '도시'].copy()

log('4/7 도시 OA -> cell (max-overlap + nearest fallback)')
inter = gpd.overlay(oa_city[['oa_idx', 'geometry']], cells_gdf,
                    how='intersection', keep_geom_type=True)
inter['inter_area'] = inter.geometry.area
major = (inter.sort_values('inter_area', ascending=False)
              .drop_duplicates('oa_idx')[['oa_idx', 'cell_id']])
oa_city = oa_city.merge(major, on='oa_idx', how='left')
log(f'    step A overlay match: {oa_city["cell_id"].notna().sum()}/{len(oa_city)}')

miss = oa_city[oa_city['cell_id'].isna()][['oa_idx', 'geometry']].copy()
if len(miss):
    near = gpd.sjoin_nearest(miss, cells_gdf, how='left', distance_col='dist_m')
    near = near.drop_duplicates('oa_idx', keep='first')[['oa_idx', 'cell_id', 'dist_m']]
    fill = dict(zip(near['oa_idx'], near['cell_id']))
    oa_city.loc[oa_city['cell_id'].isna(), 'cell_id'] = (
        oa_city.loc[oa_city['cell_id'].isna(), 'oa_idx'].map(fill))
    log(f'    step B nearest fallback: {len(miss)} OA  '
        f'mean dist={near["dist_m"].mean():.1f}m  max={near["dist_m"].max():.1f}m')

oa_city['block_id'] = oa_city['cell_id'].astype('int64')
oa_city = oa_city.drop(columns=['cell_id'])
uniq, inv = np.unique(oa_city['block_id'].values, return_inverse=True)
oa_city['block_id'] = inv.astype('int64')
K = len(uniq)
log(f'    blocks={K}')

# 산/강 OA 에는 block_id = -1
oa = oa.merge(oa_city[['oa_idx', 'block_id']], on='oa_idx', how='left')
oa['block_id'] = oa['block_id'].fillna(-1).astype('int64')

log('5/7 dissolve city OA -> blocks + stats')
blk = oa_city.dissolve(by='block_id', as_index=False)[['block_id', 'geometry']]
blk['geometry'] = blk.geometry.apply(make_valid)
blk['area_m2'] = blk.geometry.area.astype('float32')
blk['perimeter_m'] = blk.geometry.length.astype('float32')
blk['shape_idx'] = (blk['perimeter_m'] / (2 * np.sqrt(np.pi * blk['area_m2']))).astype('float32')
oa_n  = oa_city.groupby('block_id')['oa_cd'].count().rename('oa_count')
adm_n = oa_city.groupby('block_id')['adm_cd'].nunique().rename('adm_n')
blk = blk.merge(oa_n, on='block_id').merge(adm_n, on='block_id')
log(f'    area  median={blk["area_m2"].median():.0f}  '
    f'p10={np.percentile(blk["area_m2"],10):.0f}  '
    f'p90={np.percentile(blk["area_m2"],90):.0f}  max={blk["area_m2"].max():.0f}')
log(f'    total {blk["area_m2"].sum()/1e6:.1f} km²  '
    f'oa_count median={int(blk["oa_count"].median())} mean={blk["oa_count"].mean():.1f} max={int(blk["oa_count"].max())}  '
    f'singleton(oa=1)={int((blk["oa_count"]==1).sum())} ({(blk["oa_count"]==1).mean()*100:.1f}%)')
log(f'    cross-adm blocks={int((blk["adm_n"]>1).sum())}')

log('6/7 save derived/')
blk.to_file(OUT_BLK, driver='FlatGeobuf')
log(f'    {OUT_BLK} ({os.path.getsize(OUT_BLK)/1e6:.2f} MB)')

rng = np.random.default_rng(0)
sample = blk.iloc[rng.choice(len(blk), size=min(200, len(blk)), replace=False)].to_crs(4326)
sample['geometry'] = set_precision(sample.geometry.values, 1e-6)
sample.to_file(OUT_PREVIEW, driver='GeoJSON')
log(f'    {OUT_PREVIEW}')

mp = oa[['oa_cd', 'adm_cd', 'kind', 'block_id']].copy()
mp['oa_area_m2']    = oa.geometry.area.astype('float32').values
mp['inter_area_m2'] = mp['oa_area_m2']
mp['weight']        = np.float32(1.0)
# 산/강 OA 는 block_id=-1 (analysis 에서 자동 제외)
mp['block_id'] = mp['block_id'].astype('Int64')
mp.to_parquet(OUT_MAP, index=False)
log(f'    {OUT_MAP} ({os.path.getsize(OUT_MAP)/1e6:.2f} MB)')

oa_out = oa[['oa_cd', 'adm_cd', 'kind', 'block_id', 'geometry']].copy()
oa_out['oa_area_m2'] = oa.geometry.area.astype('float32').values
oa_out = oa_out.rename(columns={'block_id': 'major_block'})
oa_out['major_block'] = oa_out['major_block'].astype('Int64')
oa_out.to_file(OUT_OA, driver='FlatGeobuf')
log(f'    {OUT_OA} ({os.path.getsize(OUT_OA)/1e6:.2f} MB)')

# 7/7 산/강 OA 별도 보존
excl = oa[oa['kind'] != '도시'][['oa_cd', 'adm_cd', 'kind', 'geometry']].copy()
excl['oa_area_m2'] = excl.geometry.area.astype('float32')
excl.to_file(OUT_EXCL, driver='FlatGeobuf')
log(f'    {OUT_EXCL} ({os.path.getsize(OUT_EXCL)/1e6:.2f} MB, {len(excl)} OA)')

# viewer 슬림 사본 (WGS84) + manifest oa_count 갱신
os.makedirs(VIEWER, exist_ok=True)
oa_v = oa_out.to_crs(4326).copy()
oa_v['geometry'] = set_precision(oa_v.geometry.values, 1e-6)
oa_v[['oa_cd', 'adm_cd', 'kind', 'major_block', 'oa_area_m2', 'geometry']].to_file(
    VIEWER_OA, driver='FlatGeobuf')
log(f'    {VIEWER_OA} ({os.path.getsize(VIEWER_OA)/1e6:.2f} MB)')

mfst = {}
if os.path.exists(MANIFEST):
    with open(MANIFEST, 'r', encoding='utf-8') as f:
        mfst = json.load(f)
mfst['oa_count'] = int(len(oa_v))
mfst['oa_base_date'] = '2025-06-30'
mfst['oa_kinds'] = oa['kind'].value_counts().to_dict()
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(mfst, f, indent=2, ensure_ascii=False)
log(f'    manifest oa_count={mfst["oa_count"]}  kinds={mfst["oa_kinds"]}')

log(f'Total {time.time()-t0:.1f}s')
