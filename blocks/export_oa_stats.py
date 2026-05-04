"""
export_oa_stats.py — Stats 탭용 OA 슬림 사본 산출

oa_master 의 150 cols 중 시각화에 쓸 핵심 통계만 추려 viewer/oa_stats.fgb 로 export.

추출 컬럼:
  oa_cd / adm_cd / kind / block_id / oa_area_m2  -- 매핑·라벨
  pop_total / pop_density / pop_male / pop_female -- SGIS 인구
  ga_total / ho_total                             -- 가구·주택 합
  lp_resident_02_05 / morning_07_10 / midday_11_15 /
  evening_18_21 / late_22_01 / lp_24h             -- 시간대 풀 생활인구
"""
import os, sys, time, json
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely import set_precision

sys.stdout.reconfigure(line_buffering=True)

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, '..'))
MASTER = os.path.join(ROOT, 'data', 'derived', 'oa_master.fgb')
SEOUL_OA = os.path.join(ROOT, 'data', 'derived', 'seoul_oa.fgb')
OUT = os.path.join(ROOT, 'data', 'viewer', 'oa_stats.fgb')
MANIFEST = os.path.join(ROOT, 'data', 'viewer', 'manifest.json')

t0 = time.time()
def log(m): print(f'[{time.time()-t0:5.1f}s] {m}', flush=True)

log('1/4 load oa_master.fgb + seoul_oa.fgb')
m = gpd.read_file(MASTER)
log(f'    master rows={len(m)} cols={len(m.columns)}')

oa_kind = gpd.read_file(SEOUL_OA, columns=['oa_cd', 'kind', 'major_block'])
oa_kind = pd.DataFrame(oa_kind.drop(columns='geometry'))
oa_kind = oa_kind.rename(columns={'major_block': 'block_id_v2'})
log(f'    oa_kind rows={len(oa_kind)}')

log('2/4 derive aggregates (가구·주택 합)')
ga_cols = [c for c in m.columns if c.startswith('ga_sd_')]
ho_cols = [c for c in m.columns if c.startswith('ho_gb_')]
m['ga_total'] = m[ga_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1).astype('float32')
m['ho_total'] = m[ho_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1).astype('float32')
log(f'    ga sum cols={ga_cols}')
log(f'    ho sum cols={ho_cols}')

log('3/4 select + rename + merge kind/block_id')
keep = ['TOT_OA_CD', 'ADM_CD', 'area_m2',
        'pop_total', 'pop_density', 'pop_male', 'pop_female',
        'ga_total', 'ho_total',
        'lp_pool_resident_02_05', 'lp_pool_morning_07_10', 'lp_pool_midday_11_15',
        'lp_pool_evening_18_21', 'lp_pool_late_22_01', 'lp_pool_24h',
        'geometry']
slim = m[keep].copy()
slim = slim.rename(columns={
    'TOT_OA_CD': 'oa_cd', 'ADM_CD': 'adm_cd', 'area_m2': 'oa_area_m2',
    'lp_pool_resident_02_05': 'lp_resident',
    'lp_pool_morning_07_10':  'lp_morning',
    'lp_pool_midday_11_15':   'lp_midday',
    'lp_pool_evening_18_21':  'lp_evening',
    'lp_pool_late_22_01':     'lp_late',
    'lp_pool_24h':            'lp_24h',
})
# numeric coerce + downcast
num_cols = [c for c in slim.columns if c not in ('oa_cd', 'adm_cd', 'geometry')]
for c in num_cols:
    slim[c] = pd.to_numeric(slim[c], errors='coerce').astype('float32')
slim['oa_cd']  = slim['oa_cd'].astype(str)
slim['adm_cd'] = slim['adm_cd'].astype(str)

# v2 superblock + kind 결합
slim = slim.merge(oa_kind, on='oa_cd', how='left')
slim['kind'] = slim['kind'].fillna('도시')
slim = slim.rename(columns={'block_id_v2': 'block_id'})
slim['block_id'] = slim['block_id'].fillna(-1).astype('int32')
log(f'    slim rows={len(slim)} cols={len(slim.columns)}')

log('4/4 reproject + save (WGS84, precision 1e-6)')
slim = slim.to_crs(4326)
slim['geometry'] = set_precision(slim.geometry.values, 1e-6)
# 컬럼 순서
order = ['oa_cd', 'adm_cd', 'kind', 'block_id', 'oa_area_m2',
         'pop_total', 'pop_density', 'pop_male', 'pop_female',
         'ga_total', 'ho_total',
         'lp_resident', 'lp_morning', 'lp_midday',
         'lp_evening', 'lp_late', 'lp_24h', 'geometry']
slim[order].to_file(OUT, driver='FlatGeobuf')
log(f'    {OUT}  {os.path.getsize(OUT)/1e6:.2f} MB')

# 4b: 행정동 dissolve → viewer/adm.fgb (Stats 탭 경계 표시용)
ADM_OUT = os.path.join(ROOT, 'data', 'viewer', 'adm.fgb')
log('4b/4 dissolve OA -> 행정동')
adm_pop = (slim.groupby('adm_cd')
                .agg(pop_total=('pop_total', 'sum'),
                     ga_total=('ga_total', 'sum'),
                     ho_total=('ho_total', 'sum'),
                     oa_count=('oa_cd', 'count'))
                .reset_index())
adm_geom = slim[['adm_cd', 'geometry']].dissolve(by='adm_cd', as_index=False)
adm = adm_geom.merge(adm_pop, on='adm_cd', how='left')
adm['adm_cd'] = adm['adm_cd'].astype(str)
for c in ['pop_total', 'ga_total', 'ho_total']:
    adm[c] = adm[c].astype('float32')
adm['oa_count'] = adm['oa_count'].astype('int32')
adm['geometry'] = set_precision(adm.geometry.values, 1e-6)
adm.to_file(ADM_OUT, driver='FlatGeobuf')
log(f'    {ADM_OUT}  {os.path.getsize(ADM_OUT)/1e6:.2f} MB ({len(adm)} 행정동)')

# manifest 갱신
mfst = {}
if os.path.exists(MANIFEST):
    with open(MANIFEST, 'r', encoding='utf-8') as f:
        mfst = json.load(f)
mfst['adm_count'] = int(len(adm))
mfst['stats_metrics'] = [
    {'key': 'pop_total',   'label': '총 인구',         'unit': '명'},
    {'key': 'pop_density', 'label': '인구 밀도',       'unit': '명/km²'},
    {'key': 'ga_total',    'label': '총 가구',         'unit': '가구'},
    {'key': 'ho_total',    'label': '총 주택',         'unit': '호'},
    {'key': 'lp_resident', 'label': '생활인구 02-05',  'unit': '명'},
    {'key': 'lp_morning',  'label': '생활인구 07-10',  'unit': '명'},
    {'key': 'lp_midday',   'label': '생활인구 11-15',  'unit': '명'},
    {'key': 'lp_evening',  'label': '생활인구 18-21',  'unit': '명'},
    {'key': 'lp_late',     'label': '생활인구 22-01',  'unit': '명'},
    {'key': 'lp_24h',      'label': '생활인구 24h평균', 'unit': '명'},
]
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(mfst, f, indent=2, ensure_ascii=False)
log(f'    manifest stats_metrics={len(mfst["stats_metrics"])}')

log(f'Total {time.time()-t0:.1f}s')
