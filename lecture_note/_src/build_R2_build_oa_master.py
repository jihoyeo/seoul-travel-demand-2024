"""R2_build_oa_master.ipynb — blocks/build_oa_master.py 풀이 (~6분)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbgen import MD, CODE, write_notebook

cells = [
MD("""# R2 — `oa_master.parquet` 빌드 풀이

`blocks/build_oa_master.py` 그대로 단계별 실행.
산출: `data/derived/oa_master.parquet` (19,097 OA × 150 cols).

**소요 약 6분** (LOCAL_PEOPLE 31일 zip 스트리밍이 대부분).
처음에 `build_oa_master.py` 의 docstring 참조."""),

MD("""## 1. 마스터 spine — 2025 OA 폴리곤 + block_id"""),

CODE("""import os, time, zipfile
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import make_valid

ROOT = r'F:\\research\\TAZ'
DATA = os.path.join(ROOT, 'data')

OA2025_SHP = os.path.join(DATA, 'raw', 'sgis_oa', 'bnd_oa_11_2025_2Q.shp')
OA_TO_BLK  = os.path.join(DATA, 'derived', 'oa_to_block.parquet')
OA1625_MAP = os.path.join(DATA, 'derived', 'oa2016_to_oa2025.parquet')
CENSUS_DIR = os.path.join(DATA, 'raw', 'sgis_census')
LP_ZIP     = os.path.join(DATA, 'raw', 'seoul_living_pop', 'LOCAL_PEOPLE_202412.zip')

t0 = time.time()
master = gpd.read_file(OA2025_SHP).set_crs(5179, allow_override=True)
master = master[['TOT_OA_CD','ADM_CD','geometry']].copy()
master['TOT_OA_CD'] = master['TOT_OA_CD'].astype(str)
master['ADM_CD']    = master['ADM_CD'].astype(str)
master['geometry']  = master.geometry.apply(make_valid)
master['area_m2']   = master.geometry.area.astype('float32')

oa2blk = pd.read_parquet(OA_TO_BLK)[['oa_cd','block_id']].rename(columns={'oa_cd':'TOT_OA_CD'})
oa2blk['TOT_OA_CD'] = oa2blk['TOT_OA_CD'].astype(str)
master = master.merge(oa2blk, on='TOT_OA_CD', how='left')
print(f'master rows={len(master)}, block_id null={master["block_id"].isna().sum()}')"""),

MD("""## 2. SGIS 통계 10종 → wide pivot → join"""),

CODE("""ALIAS = {
    'to_in_001':'pop_total','to_in_007':'pop_male','to_in_008':'pop_female',
    'to_in_003':'pop_density','to_in_004':'aging_idx',
    'to_ga_001':'hh_count','to_ga_002':'hh_avg_size','to_ho_001':'ho_total',
}
CENSUS_FILES = [f for f in sorted(os.listdir(CENSUS_DIR)) if f.endswith('.csv')]
print('CSV files:'); [print(f'  {f}') for f in CENSUS_FILES]

parts = []
for fname in CENSUS_FILES:
    p = os.path.join(CENSUS_DIR, fname)
    df = pd.read_csv(p, header=None, names=['year','TOT_OA_CD','var','value'],
                     encoding='cp949',
                     dtype={'TOT_OA_CD':str,'var':str,'value':str})
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    parts.append(df[['TOT_OA_CD','var','value']])

long = pd.concat(parts, ignore_index=True)
wide = long.pivot_table(index='TOT_OA_CD', columns='var',
                        values='value', aggfunc='first').rename(columns=ALIAS)
wide.columns.name = None
wide = wide.reset_index()
wide['TOT_OA_CD'] = wide['TOT_OA_CD'].astype(str)
print(f'wide pivot: {wide.shape[0]} OA × {wide.shape[1]-1} variables')

master = master.merge(wide, on='TOT_OA_CD', how='left')"""),

MD("""## 3. LOCAL_PEOPLE 31일 스트리밍 (5~6분 소요)

`build_oa_master.py` 의 핵심 — 31 × 24h 데이터를 6 시간 풀 + 24h 성연령 평균으로 압축.
원본 코드 그대로."""),

CODE("""HOUR_POOLS = {
    'lp_pool_resident_02_05': {'02','03','04','05'},
    'lp_pool_morning_07_10':  {'07','08','09','10'},
    'lp_pool_midday_11_15':   {'11','12','13','14','15'},
    'lp_pool_evening_18_21':  {'18','19','20','21'},
    'lp_pool_late_22_01':     {'22','23','00','01'},
    'lp_pool_24h':            {f'{h:02d}' for h in range(24)},
}
LP_DEMO_COLS = (['lp_demo_total_24h']
    + [f'lp_demo_m_{l}' for l in
       ['0_9','10_14','15_19','20_24','25_29','30_34','35_39',
        '40_44','45_49','50_54','55_59','60_64','65_69','70p']]
    + [f'lp_demo_f_{l}' for l in
       ['0_9','10_14','15_19','20_24','25_29','30_34','35_39',
        '40_44','45_49','50_54','55_59','60_64','65_69','70p']])

pool_keys = list(HOUR_POOLS.keys())
oa16_to_idx = {}
N0 = 20000
pool_sum   = np.zeros((N0, len(pool_keys)), dtype=np.float64)
pool_count = np.zeros((N0, len(pool_keys)), dtype=np.int32)
demo_sum   = np.zeros((N0, len(LP_DEMO_COLS)), dtype=np.float64)
demo_count = np.zeros((N0,), dtype=np.int32)

z = zipfile.ZipFile(LP_ZIP)
day_files = sorted(n for n in z.namelist() if n.startswith('LOCAL_PEOPLE_'))
print(f'days : {len(day_files)}')
oa16_seen = []

t1 = time.time()
for di, day in enumerate(day_files):
    with z.open(day) as fh:
        df = pd.read_csv(fh, encoding='cp949', dtype=str)
    cols = list(df.columns)
    df = df.rename(columns={cols[0]:'date',cols[1]:'hour',cols[2]:'adm_mois',cols[3]:'oa16'})
    df['hour'] = df['hour'].astype(str).str.zfill(2)
    df['oa16'] = df['oa16'].astype(str)
    val_cols = list(df.columns[4:33])
    df[val_cols] = df[val_cols].apply(pd.to_numeric, errors='coerce')

    new_oas = [oa for oa in df['oa16'].unique() if oa not in oa16_to_idx]
    for oa in new_oas:
        oa16_to_idx[oa] = len(oa16_to_idx)
        oa16_seen.append(oa)
    df['_idx'] = df['oa16'].map(oa16_to_idx).to_numpy(dtype=np.int64)

    needed = len(oa16_to_idx)
    if needed > pool_sum.shape[0]:
        new_n = max(int(needed*1.5), N0*2)
        pool_sum   = np.vstack([pool_sum,   np.zeros((new_n - pool_sum.shape[0], len(pool_keys)))])
        pool_count = np.vstack([pool_count, np.zeros((new_n - pool_count.shape[0], len(pool_keys)), dtype=np.int32)])
        demo_sum   = np.vstack([demo_sum,   np.zeros((new_n - demo_sum.shape[0], len(LP_DEMO_COLS)))])
        demo_count = np.concatenate([demo_count, np.zeros(new_n - demo_count.shape[0], dtype=np.int32)])

    grp = df.groupby('_idx', sort=False)
    day_demo_sum = grp[val_cols].sum().to_numpy(dtype=np.float64)
    day_demo_n   = grp.size().to_numpy(dtype=np.int32)
    day_idx      = grp.size().index.to_numpy(dtype=np.int64)
    demo_sum[day_idx]   += day_demo_sum
    demo_count[day_idx] += day_demo_n

    hours  = df['hour'].to_numpy()
    totals = df[val_cols[0]].astype(np.float64).to_numpy()
    for pi, pkey in enumerate(pool_keys):
        mask = np.isin(hours, list(HOUR_POOLS[pkey]))
        if not mask.any(): continue
        sub_idx = df.loc[mask, '_idx'].to_numpy(dtype=np.int64)
        sub_tot = totals[mask]
        psum = np.bincount(sub_idx, weights=sub_tot, minlength=pool_sum.shape[0])
        pcnt = np.bincount(sub_idx,                  minlength=pool_count.shape[0])
        pool_sum[:,   pi] += psum[:pool_sum.shape[0]]
        pool_count[:, pi] += pcnt[:pool_count.shape[0]].astype(np.int32)

    if (di + 1) % 5 == 0 or di == len(day_files) - 1:
        print(f'  {di+1}/{len(day_files)} ({time.time()-t1:.1f}s) OA so far={len(oa16_to_idx)}')"""),

MD("""## 4. LOCAL_PEOPLE 평균 + 2016→2025 disaggregation"""),

CODE("""pool_avg = np.where(pool_count > 0, pool_sum / np.maximum(pool_count, 1), np.nan)
demo_avg = np.where(demo_count[:, None] > 0,
                    demo_sum / np.maximum(demo_count[:, None], 1), np.nan)

n_oa16 = len(oa16_to_idx)
pool_avg = pool_avg[:n_oa16]
demo_avg = demo_avg[:n_oa16]

lp16 = pd.DataFrame({'TOT_REG_CD': oa16_seen})
for ci, col in enumerate(pool_keys):
    lp16[col] = pool_avg[:, ci].astype('float32')
for ci, col in enumerate(LP_DEMO_COLS):
    lp16[col] = demo_avg[:, ci].astype('float32')
print(f'lp16 : {lp16.shape}')

# 2016 → 2025 disaggregation (area-weighted)
mp = pd.read_parquet(OA1625_MAP)[['TOT_REG_CD','TOT_OA_CD','weight']]
mp['TOT_REG_CD'] = mp['TOT_REG_CD'].astype(str)
mp['TOT_OA_CD']  = mp['TOT_OA_CD'].astype(str)
mp = mp.merge(lp16, on='TOT_REG_CD', how='left')

lp_cols = pool_keys + LP_DEMO_COLS
for c in lp_cols:
    mp[c] = mp[c] * mp['weight']

lp25 = mp.groupby('TOT_OA_CD', as_index=False)[lp_cols].sum(min_count=1)
print(f'lp25 (2025 OA): {lp25.shape}')

master = master.merge(lp25, on='TOT_OA_CD', how='left')"""),

MD("""## 5. 저장 + 검증"""),

CODE("""master['block_id'] = master['block_id'].astype('Int64')

OUT_PARQ = os.path.join(DATA, 'derived', 'oa_master.parquet')
OUT_FGB  = os.path.join(DATA, 'derived', 'oa_master.fgb')
master.to_parquet(OUT_PARQ, index=False)
master.to_file(OUT_FGB, driver='FlatGeobuf')
print(f'  {OUT_PARQ}  ({os.path.getsize(OUT_PARQ)/1e6:.2f} MB)')
print(f'  {OUT_FGB}   ({os.path.getsize(OUT_FGB)/1e6:.2f} MB)')

n_lp = master[pool_keys].notna().any(axis=1).sum()
print(f'\\n{len(master)} OA × {len(master.columns)} cols')
print(f'rows with LP: {n_lp}')
for c in ['pop_total','hh_count','ho_total','lp_pool_24h']:
    s = master[c]
    print(f'  {c}: nonnull={s.notna().sum()} mean={s.mean():.1f} median={s.median():.1f} max={s.max():.1f}')
print(f'\\nTotal {time.time()-t0:.1f}s')
print('OK')"""),
]

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'reproduce', 'R2_build_oa_master.ipynb')
    write_notebook(cells, out)
