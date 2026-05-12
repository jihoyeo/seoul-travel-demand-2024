# Lecture 3 — 통행 발생 (Trip Generation)

> 각 admdong 의 "출발 통행수 P_i, 도착 통행수 A_j" 를
> OA 변수 (인구·가구·LP) 에서 회귀로 추정한다.

**왜** : 4단계 모형 1단계의 핵심 산출. P_i, A_j 가 다음 Lecture 4
gravity model 의 row/col marginal 이 된다.

**4단계 모형 위치** : 1단계 — Trip Generation

**사전지식** : `oa_master.parquet` (Lecture 2), OLS · LightGBM 기초

**이번 시간 산출** : `pi_aj_v1.parquet` — admdong × (P_obs, A_obs, 예측치)

```
Lecture 3 의 위치 — 통행 수요 메인 시작
─────────────────────────────────────────────────────────────
Lec1 ──→ Lec2 (oa_master) ──→ Lec3 ──→ Lec4     (통행 수요 메인)
                              P/A     OD
                              ↑
                              본 모듈
                  (Lec5 superblock 은 별도 부록 트랙)
```

분석 단위 : admdong 426 (서울)
이유     : 관측 OD (`admdong_od_20240327`) 가 admdong 단위로 공개됨

다룰 항목:
- `admdong_od_20240327` 의 row/col sum → 진짜 P_obs, A_obs
- OA → admdong 공간 조인 (인구·LP 변수 합산)
- 코드 체계 변환 — 행안부 vs SGIS admdong (boundary geojson 매개)
- 회귀 (OLS + LightGBM) + spatial CV

## 1. 분석 단위 — 왜 admdong?

| 단위 | 개수 | 관측 OD 데이터? |
|---|---:|---|
| superblock | 907 | ✗ (도로 단위라 OD 데이터 없음) |
| **admdong** | **426** | ✓ admdong_od_20240327 |
| 자치구 | 25 | ✓ gu_hourly_od_202310 |

- 본 강좌 통행 모델 = admdong (관측 OD 의 자연 단위)
- 자치구는 검증용 (Lecture 4 leave-one-gu-out)
- Lecture 5 의 superblock 은 도시 형태 부록 트랙, 본 모듈에선 사용 X

## 2. ⚠️ 코드 체계 두 종류 — 행안부 vs SGIS

```
같은 동, 다른 코드
──────────────────────────────────
종로구 청운효자동
  행안부 (admdong_od.O_ADMDONG_CD) : 11110515
  SGIS  (oa_master.ADM_CD)         : 11010515
                                       ↑
                          시군구 segment 가 다름
                          (행안부 종로 11110, SGIS 종로 11010)
```

변환표 = `admdong_2023.geojson` (한 행에 두 코드가 함께 들어 있음)

| 컬럼 | 길이 | 예 |
|---|---|---|
| `adm_cd2[:8]` | 8 | 11110515 (행안부 = admdong_od 의 키) |
| `adm_cd8` | 8 | 11010530 (SGIS 8자리) |
| `adm_cd` | 7 | 1101053 (SGIS 단축) |
| `adm_nm` | str | 서울특별시 종로구 청운효자동 |

## 0. Imports & paths

```python
import os, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

warnings.filterwarnings('ignore')
%matplotlib inline
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

ROOT = r'F:\research\TAZ'
RAW  = os.path.join(ROOT, 'data', 'raw')
DRV  = os.path.join(ROOT, 'data', 'derived')
OUT_DIR = os.path.join(DRV, 'lecture_outputs')
os.makedirs(OUT_DIR, exist_ok=True)
print('OK')
```

## 3. admdong 경계 로드 + 두 코드 체계 변환표 만들기

```python
boundary = gpd.read_file(os.path.join(RAW, 'admdong_boundary', 'admdong_2023.geojson'))
seoul = boundary[boundary['sidonm'].str.contains('서울', na=False)].copy()
print(f'서울 admdong : {len(seoul)}')

# 두 체계 키 동시 보관 (int 로 변환해서 join 편하게)
seoul['adm_cd_haengan'] = seoul['adm_cd2'].astype(str).str[:8].astype(int)
seoul['adm_cd_sgis']    = seoul['adm_cd8'].astype(int)
seoul = seoul.to_crs(5179)
seoul['area_m2'] = seoul.geometry.area

# 변환표 시각화
print(seoul[['adm_nm','adm_cd_haengan','adm_cd_sgis','area_m2']].head())
print(f'\n서울 면적 합 : {seoul["area_m2"].sum()/1e6:.1f} km²')
```

## 4. OA → admdong 변수 집계

```
공간 조인 흐름
──────────────────────────────────────────────────
oa_master (19,097 OA)
   │
   │ adm_cd_sgis = TOT_OA_CD[:8]
   │     (예: 11010530010001 → 11010530)
   ↓
groupby adm_cd_sgis (426 admdong)
   ├ sum  : pop_total, hh_count, ho_total, lp_pool_*
   └ wmean: aging_idx, hh_avg_size (인구가중)
```

```python
m = pd.read_parquet(os.path.join(DRV, 'oa_master.parquet'))
m['adm_cd_sgis'] = m['TOT_OA_CD'].astype(str).str[:8].astype(int)
print(f'oa_master : {m.shape}')
print(f'admdong unique : {m["adm_cd_sgis"].nunique()}')

# sum 집계
sum_cols = ['pop_total','hh_count','ho_total',
            'lp_pool_resident_02_05','lp_pool_morning_07_10',
            'lp_pool_midday_11_15','lp_pool_evening_18_21','lp_pool_24h']
adm = m.groupby('adm_cd_sgis')[sum_cols].sum().reset_index()

# 인구가중 mean
def wmean(g, val, w='pop_total'):
    ww = g[w].fillna(0); v = g[val]
    return float((v*ww).sum() / ww.sum()) if ww.sum() > 0 else v.mean()

for c in ['aging_idx','hh_avg_size']:
    s = m.groupby('adm_cd_sgis').apply(lambda g: wmean(g, c)).rename(f'{c}_w')
    adm = adm.merge(s.reset_index(), on='adm_cd_sgis')

# 경계 + 변환표와 join
adm_g = seoul[['adm_cd_haengan','adm_cd_sgis','adm_nm','sgg','sggnm','area_m2','geometry']].merge(
    adm, on='adm_cd_sgis', how='left')
print(f'\nadm_g shape : {adm_g.shape}')
print(adm_g[['adm_nm','pop_total','hh_count','lp_pool_24h']].head(3))
```

## 5. 관측 OD 로드 + 시간대별 P_obs / A_obs

```
admdong_od_20240327.parquet
─────────────────────────────────
6.7M 행 (전국)
컬럼: O_ADMDONG_CD, D_ADMDONG_CD, ST_TIME_CD,
       FNS_TIME_CD, IN_FORN_DIV_NM, MOVE_PURPOSE,
       MOVE_DIST, MOVE_TIME, CNT
```

처리:
- 서울 O×D 만 (코드가 11 로 시작)
- 내국인만 (`IN_FORN_DIV_NM == 1`)
- 시간대별 P/A 산출 — proxy 와 정합 비교용

```
P_obs (출발) = groupby(O) → CNT.sum()
A_obs (도착) = groupby(D) → CNT.sum()
```

```python
od = pd.read_parquet(os.path.join(RAW, 'seoul_living_movement', 'admdong_od_20240327.parquet'))

# 서울 O×D + 내국인
o_seoul = od['O_ADMDONG_CD'].astype(str).str.startswith('11')
d_seoul = od['D_ADMDONG_CD'].astype(str).str.startswith('11')
od = od[o_seoul & d_seoul & (od['IN_FORN_DIV_NM'] == 1)].copy()
print(f'서울 O×D 내국인 : {od.shape}')
```

```python
# 시간대별 P/A (출발 / 도착 시간대로 분리)
BANDS = [('total', 0, 23), ('morning', 7, 9), ('midday', 10, 15), ('evening', 17, 19)]
for lbl, lo, hi in BANDS:
    p = od[od['ST_TIME_CD'].between(lo, hi)].groupby('O_ADMDONG_CD')['CNT'].sum().rename(f'P_{lbl}')
    a = od[od['ST_TIME_CD'].between(lo, hi)].groupby('D_ADMDONG_CD')['CNT'].sum().rename(f'A_{lbl}')
    adm_g = adm_g.merge(p.reset_index().rename(columns={'O_ADMDONG_CD':'adm_cd_haengan'}),
                        on='adm_cd_haengan', how='left')
    adm_g = adm_g.merge(a.reset_index().rename(columns={'D_ADMDONG_CD':'adm_cd_haengan'}),
                        on='adm_cd_haengan', how='left')

# 기본 P_obs / A_obs = 전 시간대
adm_g['P_obs'] = adm_g['P_total']
adm_g['A_obs'] = adm_g['A_total']

print(f'P_total sum   : {adm_g["P_total"].sum():,.0f}')
print(f'P_morning sum : {adm_g["P_morning"].sum():,.0f}  ({adm_g["P_morning"].sum()/adm_g["P_total"].sum()*100:.0f}%)')
print(f'P/A 비        : {adm_g["P_total"].sum() / adm_g["A_total"].sum():.6f}  (≈1.0 — 동일 인구의 출발=도착)')
```

## 6. LP-차이 proxy — 슬라이드 예측 검증

```
proxy 정의
───────────────────────────────────────────────
out_A_signed  = lp_resident − lp_morning      (signed)
outflow_A     = max(0, signed)                (clipped)
inflow_A      = max(0, -signed)               (workplace)
```

가설: outflow_A 가 출근 통행 P_morning 과 강하게 상관.
검증: 실측 데이터로 확인.

```python
r       = adm_g['lp_pool_resident_02_05']
m_pool  = adm_g['lp_pool_morning_07_10']
d_pool  = adm_g['lp_pool_midday_11_15']
mean24  = adm_g['lp_pool_24h']

adm_g['out_A_signed'] = r - m_pool
adm_g['out_B_signed'] = r - d_pool
adm_g['out_C_signed'] = mean24 - d_pool
adm_g['outflow_A'] = adm_g['out_A_signed'].clip(lower=0)
adm_g['outflow_B'] = adm_g['out_B_signed'].clip(lower=0)
adm_g['outflow_C'] = adm_g['out_C_signed'].clip(lower=0)
adm_g['inflow_A']  = (-adm_g['out_A_signed']).clip(lower=0)
adm_g['inflow_B']  = (-adm_g['out_B_signed']).clip(lower=0)
adm_g['inflow_C']  = (-adm_g['out_C_signed']).clip(lower=0)

print('signed proxy 음수 (출근시간 인구 ↑ — workplace) 비율:')
for c in ['out_A_signed','out_B_signed','out_C_signed']:
    print(f'  {c:<14} : {(adm_g[c] < 0).sum()}/{len(adm_g)}  ({(adm_g[c] < 0).mean()*100:.0f}%)')
```

```python
# proxy vs 관측 시간대별 상관표
print('=== outflow proxy vs P_obs (Pearson r) ===')
print(f'{"proxy":<14}{"P_morning":>12}{"P_midday":>12}{"P_evening":>12}{"P_total":>12}')
for proxy in ['out_A_signed','outflow_A','out_B_signed','outflow_B','out_C_signed','outflow_C']:
    line = f'  {proxy:<12}'
    for col in ['P_morning','P_midday','P_evening','P_total']:
        v = adm_g[[proxy, col]].dropna()
        line += f'  {v[proxy].corr(v[col]):>+10.3f}'
    print(line)

print('\n--- baseline (raw LP) vs P_total ---')
for proxy in ['lp_pool_resident_02_05','lp_pool_24h']:
    v = adm_g[[proxy, 'P_total']].dropna()
    print(f'  {proxy:<28}  r = {v[proxy].corr(v["P_total"]):+.3f}')
```

**관찰** — 예상과 다른 결과 :

1. `outflow_A` (clipped) ↔ `P_morning` 의 상관이 약함 (0.3 수준)
2. `out_A_signed` (clip 전) ↔ `P_total` 강한 음의 상관 (-0.78)
   - 음수 = workplace admdong, P_total 큼
3. 가장 강한 단순 예측자 = `lp_24h_mean` (r=+0.88)

**교훈** :
- **Stock 차이 ≠ flow 합** — proxy 와 P_obs 는 차원이 다름
- **clip(0) 이 정보 손실** — workplace 신호가 0 으로 뭉개짐
- **단순 raw 인구가 가장 강함** — 복잡한 proxy 만들기 전에 baseline 확인

```python
# scatter — signed proxy A vs P_total + clipped vs P_morning
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

axes[0].scatter(adm_g['out_A_signed'], adm_g['P_total'], s=20, alpha=0.5, color='steelblue')
axes[0].axvline(0, color='gray', alpha=0.5, linestyle='--')
axes[0].set_xlabel('out_A_signed (= lp_resident − lp_morning)')
axes[0].set_ylabel('P_total (관측 전 시간대)')
axes[0].set_yscale('log')
axes[0].set_title('signed proxy ↔ P_total\n음수 = workplace, P 큼')
axes[0].grid(alpha=0.3)

axes[1].scatter(adm_g['outflow_A'], adm_g['P_morning'], s=20, alpha=0.5, color='indianred')
axes[1].set_xlabel('outflow_A (clipped ≥ 0)')
axes[1].set_ylabel('P_morning (관측 7-9시)')
axes[1].set_xscale('symlog'); axes[1].set_yscale('log')
axes[1].set_title('clipped proxy A ↔ P_morning\n약한 양의 상관')
axes[1].grid(alpha=0.3)
plt.tight_layout(); plt.show()
```

## 7. signed proxy 공간 분포 — workplace 진단

```python
fig, ax = plt.subplots(figsize=(13, 11))
adm_g.plot(column='out_A_signed', cmap='RdBu_r', ax=ax,
           vmin=-10000, vmax=10000, linewidth=0.3, edgecolor='white',
           legend=True, legend_kwds={'label':'lp_resident − lp_morning','shrink':0.6},
           missing_kwds={'color':'lightgray'})
ax.set_title('signed proxy A — 음수(붉음)=출근시간 인구 ↑ = workplace')
ax.set_axis_off(); plt.show()

print('--- 가장 음수 (강한 workplace) ---')
print(adm_g.nsmallest(8, 'out_A_signed')[['adm_nm','sggnm','out_A_signed','P_total']].to_string(index=False))
print('\n--- 가장 양수 (강한 residential) ---')
print(adm_g.nlargest(8, 'out_A_signed')[['adm_nm','sggnm','out_A_signed','P_total']].to_string(index=False))
```

## 8. 회귀 모델 — P_obs / A_obs ~ 인구·구조 변수

```
회귀 흐름
────────────────────────────────────
feature (X)         target (y)
────────────────    ────────────
pop_total           log(P_obs + 1)
hh_count
hh_avg_size_w
aging_idx_w         log(A_obs + 1)
ho_total
area_m2
dist_cbd_km

→ OLS    (계수 해석)
→ LGBM   (비선형 예측)
→ Spatial CV (옆 admdong 누수 차단)
```

```python
# CBD 거리 (시청, 광화문 부근)
cbd = gpd.GeoSeries([Point(126.9784, 37.5665)], crs=4326).to_crs(5179).iloc[0]
adm_g['dist_cbd_km'] = adm_g.geometry.centroid.distance(cbd) / 1000

FEATURES = ['pop_total','hh_count','hh_avg_size_w','aging_idx_w',
            'ho_total','area_m2','dist_cbd_km']
df_model = adm_g[['adm_cd_haengan','adm_cd_sgis','adm_nm','sgg','sggnm',
                  'P_obs','A_obs'] + FEATURES + ['geometry']].dropna()
print(f'모델링 admdong : {len(df_model)} / {len(adm_g)}')
```

```python
# OLS — log(P_obs + 1) ~ log(features)
import statsmodels.api as sm

X = df_model[FEATURES].copy()
for c in ['pop_total','hh_count','ho_total','area_m2','dist_cbd_km']:
    X[f'log_{c}'] = np.log1p(X[c]); X = X.drop(columns=c)
X = sm.add_constant(X)

y_P = np.log1p(df_model['P_obs'])
y_A = np.log1p(df_model['A_obs'])

ols_P = sm.OLS(y_P, X).fit()
ols_A = sm.OLS(y_A, X).fit()
print(f'OLS R² (log P_obs) : {ols_P.rsquared:.3f}')
print(f'OLS R² (log A_obs) : {ols_A.rsquared:.3f}')
print()
print(ols_P.summary().tables[1])
```

```python
# LightGBM
import lightgbm as lgb
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, GroupKFold

X_gbm = df_model[FEATURES]

gbm_P = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05,
                          num_leaves=31, random_state=0, verbose=-1)
gbm_P.fit(X_gbm, y_P)
gbm_A = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05,
                          num_leaves=31, random_state=0, verbose=-1)
gbm_A.fit(X_gbm, y_A)

print(f'LGBM in-sample R² (P): {r2_score(y_P, gbm_P.predict(X_gbm)):.3f}')
print(f'LGBM in-sample R² (A): {r2_score(y_A, gbm_A.predict(X_gbm)):.3f}')

imp = pd.DataFrame({'feat': FEATURES,
                    'imp_P': gbm_P.feature_importances_,
                    'imp_A': gbm_A.feature_importances_}).sort_values('imp_P', ascending=False)
print(f'\nFeature importance (LGBM):')
print(imp.to_string(index=False))
```

## 9. Spatial CV — 옆 admdong 누수 차단

```
random 5-fold vs spatial GroupKFold
──────────────────────────────────────────────
random      : 같은 자치구 옆 admdong 이 train/test 에 섞임
              → R² 과대평가 (낙관적)
spatial     : 자치구(sgg) 단위 분할
              → 모르는 자치구 예측 능력 측정 (정직)
```

```python
def cv_score(X, y, splitter, groups=None, label=''):
    rs = []
    for tr, te in splitter.split(X, y, groups=groups):
        m = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05,
                              num_leaves=31, random_state=0, verbose=-1)
        m.fit(X.iloc[tr], y.iloc[tr])
        rs.append(r2_score(y.iloc[te], m.predict(X.iloc[te])))
    print(f'  {label:<25} R² mean={np.mean(rs):.3f}  std={np.std(rs):.3f}')
    return rs

groups = df_model['sgg'].values

print('P_obs CV:')
_ = cv_score(X_gbm, y_P, KFold(n_splits=5, shuffle=True, random_state=0), label='random 5-fold')
_ = cv_score(X_gbm, y_P, GroupKFold(n_splits=5), groups=groups, label='spatial (sgg)')

print('\nA_obs CV:')
_ = cv_score(X_gbm, y_A, KFold(n_splits=5, shuffle=True, random_state=0), label='random 5-fold')
_ = cv_score(X_gbm, y_A, GroupKFold(n_splits=5), groups=groups, label='spatial (sgg)')
```

## 10. 잔차 choropleth — 다음 feature 후보

```python
df_model['P_pred_ols'] = ols_P.predict(X)
df_model['resid_P'] = y_P - df_model['P_pred_ols']
df_model['resid_A'] = y_A - ols_A.predict(X)

fig, axes = plt.subplots(1, 2, figsize=(18, 9))
df_model.plot(column='resid_P', cmap='RdBu_r', ax=axes[0],
              vmin=-1, vmax=1, linewidth=0.3, edgecolor='white',
              legend=True, legend_kwds={'shrink':0.6})
axes[0].set_title('OLS 잔차 — log P_obs\n>0 = 모델 과소평가'); axes[0].set_axis_off()

df_model.plot(column='resid_A', cmap='RdBu_r', ax=axes[1],
              vmin=-1, vmax=1, linewidth=0.3, edgecolor='white',
              legend=True, legend_kwds={'shrink':0.6})
axes[1].set_title('OLS 잔차 — log A_obs'); axes[1].set_axis_off()
plt.show()

sgg_resid = df_model.groupby('sggnm')[['resid_P','resid_A']].mean().round(3)
print('자치구별 잔차 평균 (절대값 큰 = FE 후보):')
print(sgg_resid.reindex(sgg_resid['resid_P'].abs().sort_values(ascending=False).index).head(10))
```

## 11. pi_aj_v1.parquet 산출 — Lecture 4 입력

```python
df_model['P_pred_gbm'] = np.expm1(gbm_P.predict(X_gbm))
df_model['A_pred_gbm'] = np.expm1(gbm_A.predict(X_gbm))

out_cols = ['adm_cd_haengan','P_obs','A_obs','P_pred_gbm','A_pred_gbm','resid_P','resid_A']
proxy_cols = ['outflow_A','outflow_B','outflow_C','inflow_A','inflow_B','inflow_C',
              'out_A_signed','out_B_signed','out_C_signed']

out = adm_g[['adm_cd_haengan'] + proxy_cols].merge(df_model[out_cols], on='adm_cd_haengan', how='right')
out_path = os.path.join(OUT_DIR, 'pi_aj_v1.parquet')
out.to_parquet(out_path)
print(f'saved : {out_path}  ({os.path.getsize(out_path)/1024:.1f} KB)')
print(f'shape : {out.shape}')
print(out.head(3))
```

## 12. 정리

- 분석 단위 = admdong (관측 OD 의 자연 단위)
- 두 코드 체계 (행안부 vs SGIS) — `admdong_boundary.geojson` 이 매개
- 관측 P_obs / A_obs = admdong_od 의 row/col sum
- LP-proxy 비교 — 단순 차이 약함, signed 가 강한 음의 상관 (workplace 신호)
- 회귀 (OLS + LGBM) + spatial CV — 옆 admdong 누수 정직히 측정
- `pi_aj_v1.parquet` 산출 → Lecture 4 gravity model 입력

→ **다음 Lecture 4** — Poisson gravity GLM + IPF + 정량 검증.
