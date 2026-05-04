"""
build_oa_master.py — 2025 SGIS OA(TOT_OA_CD 14) 단일 키로 모든 통계 합본.

산출:
  derived/oa_master.parquet  (geometry 포함 GeoParquet, 19,097 행)
  derived/oa_master.fgb      (시각화용 동일 데이터, EPSG:5179)

수록 컬럼:
  [공간·식별]
    TOT_OA_CD(str14), ADM_CD(str8), block_id(Int64), area_m2, geometry

  [SGIS 2024 통계, wide pivot per OA — value='N/A' 는 NaN]
    인구총괄: pop_total(to_in_001), pop_male(007), pop_female(008),
             pop_density(to_in_003), aging_idx(to_in_004)
    가구총괄: hh_count(to_ga_001), hh_avg_size(to_ga_002)
    주택총괄: ho_total(to_ho_001)
    세대구성별: hh_sd_1세대(ga_sd_001) … hh_sd_비친족(ga_sd_006)
    주택유형: ho_단독(ho_gb_001) … ho_기타(ho_gb_006)
    연건평별: ho_ar_001 … ho_ar_009 (9 area bands)
    건축년도별: ho_yr_001 … ho_yr_020 (20 year bands)
    성연령별: in_age_001 … in_age_081 (81 codes, SGIS 변수사전 참조)

  [LOCAL_PEOPLE 2024-12 시간대 풀 평균, 2016→2025 면적가중 disaggregate]
    lp_pool_resident_02_05, lp_pool_morning_07_10, lp_pool_midday_11_15,
    lp_pool_evening_18_21,  lp_pool_late_22_01,    lp_pool_24h
    (각 시간 슬롯의 평균 총생활인구. 평일/주말 미분리, 31일 통합 평균.)

    lp_demo_total_24h
    lp_demo_m_0_9, lp_demo_m_10_14, … lp_demo_m_70p   (14 남자 연령)
    lp_demo_f_0_9, lp_demo_f_10_14, … lp_demo_f_70p   (14 여자 연령)
    (24시간 평균값. 평일/주말 미분리.)

가정·근사:
  - LOCAL_PEOPLE 의 2016 OA 단위 카운트를 area-weighted 로 2025 OA 에 분배
    (2016 OA 내부 균일분포 가정). population-density 가중으로 정교화하려면
    SGIS 인구를 미리 조인해 가중치를 다시 계산.
  - 'N/A' (SGIS 통계 보호 셀) 는 NaN 으로 보존. 0 imputation 금지.
"""
import os, time, zipfile, io
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import make_valid

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
DATA = os.path.join(ROOT, 'data')

OA2025_SHP = os.path.join(DATA, 'raw', 'sgis_oa', 'bnd_oa_11_2025_2Q.shp')
OA_TO_BLK  = os.path.join(DATA, 'derived', 'oa_to_block.parquet')
OA1625_MAP = os.path.join(DATA, 'derived', 'oa2016_to_oa2025.parquet')

CENSUS_DIR = os.path.join(DATA, 'raw', 'sgis_census')
CENSUS_FILES = [
    '11_2024년_인구총괄(총인구).csv',
    '11_2024년_인구총괄(인구밀도).csv',
    '11_2024년_인구총괄(노령화지수).csv',
    '11_2024년_가구총괄.csv',
    '11_2024년_세대구성별가구.csv',
    '11_2024년_주택총괄_총주택(거처)수.csv',
    '11_2024년_주택유형별주택.csv',
    '11_2024년_연건평별주택.csv',
    '11_2024년_건축년도별주택.csv',
    '11_2024년_성연령별인구.csv',
]

LP_ZIP = os.path.join(DATA, 'raw', 'seoul_living_pop', 'LOCAL_PEOPLE_202412.zip')

OUT_PARQ = os.path.join(DATA, 'derived', 'oa_master.parquet')
OUT_FGB  = os.path.join(DATA, 'derived', 'oa_master.fgb')

# 인간이 읽기 쉬운 컬럼 별칭 (SGIS code 표기 그대로 두면 모델·뷰어에서 의미 잃음)
ALIAS = {
    'to_in_001': 'pop_total',
    'to_in_007': 'pop_male',
    'to_in_008': 'pop_female',
    'to_in_003': 'pop_density',
    'to_in_004': 'aging_idx',
    'to_ga_001': 'hh_count',
    'to_ga_002': 'hh_avg_size',
    'to_ho_001': 'ho_total',
}

# LOCAL_PEOPLE 시간 풀 정의 (24h 표기, 끝 inclusive 가 아닌 hour-set 멤버십)
HOUR_POOLS = {
    'lp_pool_resident_02_05': {'02','03','04','05'},
    'lp_pool_morning_07_10':  {'07','08','09','10'},
    'lp_pool_midday_11_15':   {'11','12','13','14','15'},
    'lp_pool_evening_18_21':  {'18','19','20','21'},
    'lp_pool_late_22_01':     {'22','23','00','01'},
    'lp_pool_24h':            {f'{h:02d}' for h in range(24)},
}

LP_DEMO_COLS = (['lp_demo_total_24h']
    + [f'lp_demo_m_{lab}' for lab in
       ['0_9','10_14','15_19','20_24','25_29','30_34','35_39',
        '40_44','45_49','50_54','55_59','60_64','65_69','70p']]
    + [f'lp_demo_f_{lab}' for lab in
       ['0_9','10_14','15_19','20_24','25_29','30_34','35_39',
        '40_44','45_49','50_54','55_59','60_64','65_69','70p']])
# 29 columns total

t0 = time.time()

# -----------------------------------------------------------------------------
print('[1/5] Master spine: 2025 OA polygons + block_id...')
master = gpd.read_file(OA2025_SHP)
if master.crs is None or master.crs.to_epsg() != 5179:
    master = master.set_crs(5179, allow_override=True)
master = master[['TOT_OA_CD', 'ADM_CD', 'geometry']].copy()
master['TOT_OA_CD'] = master['TOT_OA_CD'].astype(str)
master['ADM_CD']    = master['ADM_CD'].astype(str)
master['geometry']  = master.geometry.apply(make_valid)
master['area_m2']   = master.geometry.area.astype('float32')

oa2blk = pd.read_parquet(OA_TO_BLK)[['oa_cd', 'block_id']].rename(columns={'oa_cd':'TOT_OA_CD'})
oa2blk['TOT_OA_CD'] = oa2blk['TOT_OA_CD'].astype(str)
master = master.merge(oa2blk, on='TOT_OA_CD', how='left')
print(f'  rows={len(master)}  block_id null={master["block_id"].isna().sum()}')

# -----------------------------------------------------------------------------
print('[2/5] SGIS 2024 census (10 csvs) → wide pivot → join...')
parts = []
for fname in CENSUS_FILES:
    p = os.path.join(CENSUS_DIR, fname)
    df = pd.read_csv(p, header=None, names=['year','TOT_OA_CD','var','value'],
                     encoding='cp949', dtype={'TOT_OA_CD': str, 'var': str, 'value': str})
    df['value'] = pd.to_numeric(df['value'], errors='coerce')  # 'N/A' → NaN
    parts.append(df[['TOT_OA_CD','var','value']])
    print(f'  {fname}: {len(df)} rows')

long = pd.concat(parts, ignore_index=True)
wide = long.pivot_table(index='TOT_OA_CD', columns='var', values='value', aggfunc='first')
# Apply human-readable alias for the small core variables
wide = wide.rename(columns=ALIAS)
wide.columns.name = None
wide = wide.reset_index()
wide['TOT_OA_CD'] = wide['TOT_OA_CD'].astype(str)
print(f'  wide pivot: {wide.shape[0]} OA × {wide.shape[1]-1} variables')

master = master.merge(wide, on='TOT_OA_CD', how='left')

# -----------------------------------------------------------------------------
print('[3/5] LOCAL_PEOPLE 31일 streaming → per-2016-OA pool/demo accumulators...')
t1 = time.time()

pool_keys = list(HOUR_POOLS.keys())
# Use dicts keyed by oa16 string. Numpy via index for speed: build oa16→idx after first pass.
# To avoid two-pass, we'll discover oa16 codes incrementally.
oa16_to_idx = {}
def get_idx(oa, sums_grow):
    i = oa16_to_idx.get(oa)
    if i is None:
        i = len(oa16_to_idx)
        oa16_to_idx[oa] = i
        sums_grow.append(i)
    return i

# Pre-allocate generously: ~19,200 OA known
N0 = 20000
pool_sum   = np.zeros((N0, len(pool_keys)), dtype=np.float64)
pool_count = np.zeros((N0, len(pool_keys)), dtype=np.int32)
demo_sum   = np.zeros((N0, len(LP_DEMO_COLS)), dtype=np.float64)
demo_count = np.zeros((N0, ), dtype=np.int32)

# Map hour-string to membership bitmask over pool index
HOUR_STR = [f'{h:02d}' for h in range(24)]
hour_pool_mask = {h: np.array([h in HOUR_POOLS[k] for k in pool_keys]) for h in HOUR_STR}

# Demo column order in CSV (header) = total + male14 + female14 → 29 floats
DEMO_RAW_ORDER = ['lp_demo_total_24h'] + LP_DEMO_COLS[1:15] + LP_DEMO_COLS[15:29]

z = zipfile.ZipFile(LP_ZIP)
day_files = sorted(i for i in z.namelist() if i.startswith('LOCAL_PEOPLE_'))
print(f'  daily files: {len(day_files)}')

oa16_seen = []  # ordered list (parallels oa16_to_idx)

for di, day in enumerate(day_files):
    with z.open(day) as fh:
        df = pd.read_csv(fh, encoding='cp949', dtype=str)
    # 33 columns in fixed positional order: 0=date, 1=hour, 2=adm_dong(행안부),
    # 3=oa16, 4=total, 5..18 = male 14 ages, 19..32 = female 14 ages.
    # 헤더 이름은 BOM·인코딩 잔재로 안정적이지 않아 위치로 처리.
    cols = list(df.columns)
    df = df.rename(columns={cols[0]: 'date', cols[1]: 'hour',
                            cols[2]: 'adm_mois', cols[3]: 'oa16'})
    df['hour'] = df['hour'].astype(str).str.zfill(2)
    df['oa16'] = df['oa16'].astype(str)

    # 29 numeric columns by position (4..32). Header order = total + male14 + female14.
    val_cols = list(df.columns[4:33])
    df[val_cols] = df[val_cols].apply(pd.to_numeric, errors='coerce')

    # Resolve OA → integer index, growing oa16_seen
    new_oas = [oa for oa in df['oa16'].unique() if oa not in oa16_to_idx]
    for oa in new_oas:
        oa16_to_idx[oa] = len(oa16_to_idx)
        oa16_seen.append(oa)
    df['_idx'] = df['oa16'].map(oa16_to_idx).to_numpy(dtype=np.int64)

    # Grow pre-allocations if needed
    needed = len(oa16_to_idx)
    if needed > pool_sum.shape[0]:
        new_n = max(int(needed * 1.5), N0 * 2)
        pool_sum   = np.vstack([pool_sum,   np.zeros((new_n - pool_sum.shape[0], len(pool_keys)))])
        pool_count = np.vstack([pool_count, np.zeros((new_n - pool_count.shape[0], len(pool_keys)), dtype=np.int32)])
        demo_sum   = np.vstack([demo_sum,   np.zeros((new_n - demo_sum.shape[0], len(LP_DEMO_COLS)))])
        demo_count = np.concatenate([demo_count, np.zeros(new_n - demo_count.shape[0], dtype=np.int32)])

    # ---- Demo accumulation (24h sum per OA, +1 count per row group): use groupby
    grp = df.groupby('_idx', sort=False)
    day_demo_sum = grp[val_cols].sum().to_numpy(dtype=np.float64)  # (k, 29)
    day_demo_n   = grp.size().to_numpy(dtype=np.int32)             # (k,)
    day_idx      = grp.size().index.to_numpy(dtype=np.int64)
    demo_sum[day_idx]  += day_demo_sum
    demo_count[day_idx] += day_demo_n

    # ---- Pool accumulation: for each pool, sum totals across rows whose hour ∈ pool
    hours  = df['hour'].to_numpy()
    totals = df[val_cols[0]].astype(np.float64).to_numpy()  # 총생활인구수
    for pi, pkey in enumerate(pool_keys):
        hours_in = HOUR_POOLS[pkey]
        mask = np.isin(hours, list(hours_in))
        if not mask.any(): continue
        sub_idx = df.loc[mask, '_idx'].to_numpy(dtype=np.int64)
        sub_tot = totals[mask]
        # bincount-based scatter-add (faster than np.add.at)
        psum = np.bincount(sub_idx, weights=sub_tot, minlength=pool_sum.shape[0])
        pcnt = np.bincount(sub_idx,                  minlength=pool_count.shape[0])
        pool_sum[:,   pi] += psum[:pool_sum.shape[0]]
        pool_count[:, pi] += pcnt[:pool_count.shape[0]].astype(np.int32)

    if (di + 1) % 5 == 0 or di == len(day_files) - 1:
        print(f'  ... {di+1}/{len(day_files)}  ({time.time()-t1:.1f}s)  '
              f'OA so far={len(oa16_to_idx)}')

# Compute averages
pool_avg = np.where(pool_count > 0, pool_sum / np.maximum(pool_count, 1), np.nan)
demo_avg = np.where(demo_count[:, None] > 0,
                    demo_sum / np.maximum(demo_count[:, None], 1), np.nan)

n_oa16 = len(oa16_to_idx)
pool_avg = pool_avg[:n_oa16]
demo_avg = demo_avg[:n_oa16]
print(f'  OA in LOCAL_PEOPLE: {n_oa16}')
print(f'  pool means computed in {time.time()-t1:.1f}s')

# Build a 2016 OA-keyed DataFrame
lp16 = pd.DataFrame({'TOT_REG_CD': oa16_seen})
for ci, col in enumerate(pool_keys):
    lp16[col] = pool_avg[:, ci].astype('float32')
for ci, col in enumerate(LP_DEMO_COLS):
    lp16[col] = demo_avg[:, ci].astype('float32')

# -----------------------------------------------------------------------------
print('[4/5] LOCAL_PEOPLE 2016→2025 disaggregation (area-weighted)...')
mp = pd.read_parquet(OA1625_MAP)[['TOT_REG_CD', 'TOT_OA_CD', 'weight']]
mp['TOT_REG_CD'] = mp['TOT_REG_CD'].astype(str)
mp['TOT_OA_CD']  = mp['TOT_OA_CD'].astype(str)

mp = mp.merge(lp16, on='TOT_REG_CD', how='left')
lp_cols = pool_keys + LP_DEMO_COLS
for c in lp_cols:
    mp[c] = mp[c] * mp['weight']
lp25 = mp.groupby('TOT_OA_CD', as_index=False)[lp_cols].sum(min_count=1)

# Note: with min_count=1, OA where all incoming 2016 OA had NaN remain NaN.
# This preserves 'no data' rather than zero-imputing.
print(f'  lp25 rows: {len(lp25)}  (master rows: {len(master)})')
master = master.merge(lp25, on='TOT_OA_CD', how='left')

# -----------------------------------------------------------------------------
print('[5/5] Save master parquet + fgb...')
# Cast block_id properly
master['block_id'] = master['block_id'].astype('Int64')
# GeoParquet
master.to_parquet(OUT_PARQ, index=False)
print(f'  {OUT_PARQ}  ({os.path.getsize(OUT_PARQ)/1e6:.2f} MB)')
master.to_file(OUT_FGB, driver='FlatGeobuf')
print(f'  {OUT_FGB}  ({os.path.getsize(OUT_FGB)/1e6:.2f} MB)')

# Summary
n_cols = len(master.columns)
n_lp_present = master[pool_keys].notna().any(axis=1).sum()
print(f'\n  {len(master)} OA × {n_cols} columns')
print(f'  rows with any LOCAL_PEOPLE value: {n_lp_present}')
for c in ['pop_total','hh_count','ho_total','lp_pool_24h']:
    if c in master.columns:
        s = master[c]
        print(f'  {c}: nonnull={s.notna().sum()}  '
              f'mean={s.mean():.1f}  median={s.median():.1f}  max={s.max():.1f}')
print(f'\nTotal {time.time()-t0:.1f}s.')
