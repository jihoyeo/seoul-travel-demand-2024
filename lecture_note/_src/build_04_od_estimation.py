"""04_od_estimation.ipynb — Poisson gravity + IPF + 정량 검증 (통행 수요 메인 마지막)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbgen import MD, CODE, write_both

cells = [
MD("""# Lecture 4 — OD 추정 (Trip Distribution)

> Poisson gravity GLM 으로 admdong i → j 통행량 T_ij 를 추정하고
> 관측 OD 와 정량 비교한다. 본 강좌 메인 트랙의 도착점.

**왜** : 4단계 모형 2단계. "어디서 어디로 사람이 움직이는가" 의
공간적 패턴을 첫 원리에서 만들어보는 단계.

**4단계 모형 위치** : 2단계 — Trip Distribution

**사전지식** : `pi_aj_v1.parquet` (Lecture 3), GLM · IPF 개념

**이번 시간 산출** : `od_matrix_v1.parquet` — admdong × admdong T_ij

```
Lecture 4 의 위치 — 통행 수요 메인 마지막
─────────────────────────────────────────────────────────────
Lec3 (pi_aj_v1) ─→ Lec4 ─→ od_matrix_v1.parquet (T_ij)
                            + 정량 검증 (RMSE, MAPE, R²)

→ 본 모듈로 통행 수요 메인 트랙 종료
→ Lec5 superblock 은 별도 부록 트랙
```

목표 : admdong i → j 통행량 T_ij 추정
방법 : Poisson gravity GLM + IPF/Furness + 정량 검증

다룰 항목:
- admdong 426×426 관측 OD 행렬 T_obs
- Poisson GLM 으로 α (P elasticity), β (A elasticity), β_d (distance deterrence)
- IPF/Furness 로 row/col marginal 보존
- 정량 검증 (RMSE, MAPE, R²) + 정성 (TLD, flow lines, intrazonal)
- 시간대별 β_d 변화 (출근 vs 야간)"""),

MD("""## 1. Gravity model — 직관

```
중력 모형 (Gravity Model)
──────────────────────────────────────────────
T_ij = K · P_i^α · A_j^β · f(c_ij)

T_ij     : i → j 통행량
K        : 정규화 상수
P_i      : i 의 발생량 (production)
A_j      : j 의 유인량 (attraction)
α, β     : elasticity (보통 ≈ 1)
f(c_ij)  : 거리 임피던스 (deterrence)
```

거리 함수 3가지:

| 형태 | 식 | 특징 |
|---|---|---|
| Power | $c^{-\\beta}$ | 단거리 dominate |
| **Exponential** | $e^{-\\beta_d c}$ | 본 강좌 채택 |
| Tanner | $c^a \\cdot e^{-bc}$ | hybrid |

- 직관: "사람 많은 곳 → 사람 많은 곳" 으로 가깝게 흐른다
- Newton 중력 (질량/거리²) 의 통행 모델 버전"""),

MD("""## 2. 왜 Poisson GLM?

```
log E[T_ij] = log K + α log P_i + β log A_j − β_d · c_ij
                ↑           ↑              ↑
              상수      elasticity    deterrence
```

- count 데이터 → Poisson 자연 적합
- log-OLS 는 `log(T_ij + ε)` hack 필요 + 작은 flow bias
- Flowerdew & Aitkin (1982): Poisson MLE = entropy maximization 유도
- `statsmodels.GLM(family=Poisson())` 한 줄"""),

MD("""## 0. Imports & paths"""),

CODE("""import os, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import statsmodels.api as sm

warnings.filterwarnings('ignore')
%matplotlib inline
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

ROOT = r'F:\\research\\TAZ'
RAW  = os.path.join(ROOT, 'data', 'raw')
DRV  = os.path.join(ROOT, 'data', 'derived')
OUT_DIR = os.path.join(DRV, 'lecture_outputs')
print('OK')"""),

MD("""## 3. Lecture 3 산출 P_i, A_j 로드 + admdong 경계"""),

CODE("""pa = pd.read_parquet(os.path.join(OUT_DIR, 'pi_aj_v1.parquet'))
boundary = gpd.read_file(os.path.join(RAW, 'admdong_boundary', 'admdong_2023.geojson'))
seoul = boundary[boundary['sidonm'].str.contains('서울', na=False)].copy()
seoul['adm_cd_haengan'] = seoul['adm_cd2'].astype(str).str[:8].astype(int)
seoul = seoul.to_crs(5179)

g = seoul[['adm_cd_haengan','adm_nm','sgg','sggnm','geometry']].merge(
    pa, on='adm_cd_haengan', how='left')
g = g[g['P_obs'].notna() & g['A_obs'].notna()].reset_index(drop=True)
print(f'OD 모델링 admdong : {len(g)}')
print(f'P_obs total       : {g["P_obs"].sum():,.0f}')
print(f'A_obs total       : {g["A_obs"].sum():,.0f}')"""),

MD("""## 4. 인구가중 centroid — 거리 행렬 기준점

```
centroid 계산
────────────────────────────────────────────
admdong 의 OA centroid 들을 OA 인구로 가중평균
  → 도시 활동의 무게중심
  → 단순 geometry centroid 보다 정확
```"""),

CODE("""m = gpd.read_parquet(os.path.join(DRV, 'oa_master.parquet'))
m = m[m['block_id'] != -1].copy()
m['adm_cd_sgis'] = m['TOT_OA_CD'].astype(str).str[:8].astype(int)
m['cx'] = m.geometry.centroid.x
m['cy'] = m.geometry.centroid.y
m['w'] = m['pop_total'].fillna(0)

def wmean(sub):
    if sub['w'].sum() == 0:
        return pd.Series({'cx': sub['cx'].mean(), 'cy': sub['cy'].mean()})
    return pd.Series({'cx': (sub['cx']*sub['w']).sum()/sub['w'].sum(),
                      'cy': (sub['cy']*sub['w']).sum()/sub['w'].sum()})

cent_sgis = m.groupby('adm_cd_sgis').apply(wmean).reset_index()
# SGIS → 행안부 변환
sgis_to_haengan = pd.DataFrame({
    'adm_cd_haengan': seoul['adm_cd_haengan'].values,
    'adm_cd_sgis': seoul['adm_cd8'].astype(int).values
})
cent = cent_sgis.merge(sgis_to_haengan, on='adm_cd_sgis', how='left')
g = g.merge(cent[['adm_cd_haengan','cx','cy']], on='adm_cd_haengan', how='left')
print(f'centroid 결측 : {g["cx"].isna().sum()}')"""),

MD("""## 5. 426×426 거리 행렬"""),

CODE("""coords = g[['cx','cy']].values
n = len(coords)
print(f'n = {n}, OD pairs = {n*n:,}')

# n × n × 2 행렬 차원으로 모든 쌍 거리 계산
diff = coords[:, None, :] - coords[None, :, :]
dist_km = np.sqrt((diff ** 2).sum(axis=2)) / 1000

# self-distance = 자기 admdong 반경 근사 (intrazonal)
np.fill_diagonal(dist_km, np.sqrt(g.geometry.area.values / np.pi) / 1000)

print(f'\\n거리 mean {dist_km.mean():.2f}, median {np.median(dist_km):.2f}, max {dist_km.max():.2f} km')

fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(dist_km[np.triu_indices(n, k=1)], bins=60, color='steelblue', edgecolor='white')
ax.set_xlabel('admdong-pair distance (km)'); ax.set_ylabel('pair count')
ax.set_title('admdong 쌍 Euclidean 거리 분포')
ax.grid(alpha=0.3); plt.show()"""),

MD("""## 6. 관측 OD 행렬 T_obs (426×426)

```
OD long → wide
────────────────────────────────────
admdong_od_20240327 (long, 222만 행)
   │ groupby (O, D) → CNT.sum()
   ↓
T_obs[i, j] = i → j 통행량 (426×426 행렬)
```"""),

CODE("""od = pd.read_parquet(os.path.join(RAW, 'seoul_living_movement', 'admdong_od_20240327.parquet'))
o_seoul = od['O_ADMDONG_CD'].astype(str).str.startswith('11')
d_seoul = od['D_ADMDONG_CD'].astype(str).str.startswith('11')
od = od[o_seoul & d_seoul & (od['IN_FORN_DIV_NM'] == 1)].copy()

# 전 시간대 통합
od_agg = od.groupby(['O_ADMDONG_CD','D_ADMDONG_CD'], as_index=False)['CNT'].sum()

# admdong → index 매핑
adm_idx = {c: i for i, c in enumerate(g['adm_cd_haengan'])}
od_agg['i'] = od_agg['O_ADMDONG_CD'].map(adm_idx)
od_agg['j'] = od_agg['D_ADMDONG_CD'].map(adm_idx)
od_agg = od_agg.dropna(subset=['i','j'])
od_agg['i'] = od_agg['i'].astype(int); od_agg['j'] = od_agg['j'].astype(int)

T_obs = np.zeros((n, n), dtype=float)
T_obs[od_agg['i'].values, od_agg['j'].values] = od_agg['CNT'].values
print(f'T_obs shape : {T_obs.shape}')
print(f'T_obs sum   : {T_obs.sum():,.0f}')
print(f'0 인 cell   : {(T_obs == 0).mean()*100:.1f}%   (sparsity)')

# 검증 — row sum vs P_obs, col sum vs A_obs
P_arr = g['P_obs'].values; A_arr = g['A_obs'].values
print(f'\\nrow_sum vs P_obs max diff : {np.abs(T_obs.sum(axis=1) - P_arr).max():.4f}')
print(f'col_sum vs A_obs max diff : {np.abs(T_obs.sum(axis=0) - A_arr).max():.4f}')"""),

MD("""## 7. Poisson GLM fit

```
fit 데이터 (long format)
─────────────────────────────
i, j      : admdong index (i ≠ j)
T_ij      : 관측 통행량
log P_i   : log(P_obs + 1)
log A_j   : log(A_obs + 1)
c_ij      : 거리 km
→ 181,050 행 (425×426 - 대각선)
```"""),

CODE("""i_idx, j_idx = np.indices((n, n))
mask = i_idx != j_idx   # 대각선 제외 (intrazonal 별도)

flat = pd.DataFrame({
    'T':     T_obs[mask],
    'log_P': np.log(P_arr[i_idx[mask]] + 1),
    'log_A': np.log(A_arr[j_idx[mask]] + 1),
    'd':     dist_km[mask],
})
print(f'fit rows : {len(flat):,}')
print(f'T == 0 비율 : {(flat["T"] == 0).mean()*100:.1f}%')

X_glm = sm.add_constant(flat[['log_P','log_A','d']])
glm = sm.GLM(flat['T'], X_glm, family=sm.families.Poisson()).fit()

print(f'\\n--- 추정 결과 ---')
print(f'log K   = {glm.params["const"]:>7.3f}')
print(f'α (P)   = {glm.params["log_P"]:>7.3f}')
print(f'β (A)   = {glm.params["log_A"]:>7.3f}')
print(f'β_d     = {glm.params["d"]:>7.3f}  → 1km 늘면 ×{np.exp(glm.params["d"]):.3f}')"""),

CODE("""# deterrence function 시각화
beta_d = glm.params['d']
d_grid = np.linspace(0.1, 30, 200)
deterrence = np.exp(beta_d * d_grid)

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(d_grid, deterrence, color='steelblue', linewidth=2)
ax.set_xlabel('distance (km)'); ax.set_ylabel('deterrence factor exp(β_d · d)')
ax.set_title(f'Deterrence function — β_d = {beta_d:.3f} km⁻¹')
ax.set_yscale('log'); ax.grid(alpha=0.3); plt.show()"""),

MD("""## 8. IPF/Furness — marginal 보정

```
IPF (Iterative Proportional Fitting)
────────────────────────────────────────────
GLM 만으론 row/col marginal 정확 보존 X
→ 반복 row 정규화 + col 정규화

반복 (n iter):
  T = T × (P_i / Σ_j T_ij)   ← row 보정
  T = T × (A_j / Σ_i T_ij)   ← col 보정
  if max err < tol: break

수렴 : 보통 6-10 iter 으로 1% 이내
```"""),

CODE("""# GLM 예측치를 seed 로
K_const = np.exp(glm.params['const'])
T_seed = K_const * (P_arr[:, None] + 1) ** glm.params['log_P'] \\
                 * (A_arr[None, :] + 1) ** glm.params['log_A'] \\
                 * np.exp(beta_d * dist_km)
print(f'seed sum     : {T_seed.sum():,.0f}')
print(f'observed sum : {T_obs.sum():,.0f}')

def ipf(T, P, A, max_iter=50, tol=1e-3):
    T = T.copy(); history = []
    for it in range(max_iter):
        rs = T.sum(axis=1); T = T * np.where(rs > 0, P/rs, 1)[:, None]
        cs = T.sum(axis=0); T = T * np.where(cs > 0, A/cs, 1)[None, :]
        err = max(np.abs(T.sum(axis=1)-P).max()/max(P.max(),1),
                  np.abs(T.sum(axis=0)-A).max()/max(A.max(),1))
        history.append(err)
        if err < tol: break
    return T, history

T_pred, hist = ipf(T_seed, P_arr, A_arr)
print(f'\\nIPF iter : {len(hist)}, final max err : {hist[-1]:.5f}')

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(range(1, len(hist)+1), hist, marker='o', color='steelblue')
ax.set_yscale('log'); ax.set_xlabel('iteration'); ax.set_ylabel('max marginal error')
ax.set_title('IPF / Furness 수렴 곡선'); ax.grid(alpha=0.3); plt.show()"""),

MD("""## 9. 검증 1 — 정량 (RMSE, MAPE, R²)

관측 OD 가 있어 정량 검증 가능. Lecture 3 의 회귀 검증과 동일하게 R² 측정."""),

CODE("""flat_obs  = T_obs[mask]
flat_pred = T_pred[mask]

rmse = np.sqrt(((flat_obs - flat_pred)**2).mean())
mape = (np.abs(flat_obs - flat_pred) / (flat_obs + 1)).mean()
ss_res = ((flat_obs - flat_pred)**2).sum()
ss_tot = ((flat_obs - flat_obs.mean())**2).sum()
r2 = 1 - ss_res / ss_tot

print(f'RMSE : {rmse:.2f}')
print(f'MAPE : {mape*100:.1f}%')
print(f'R²   : {r2:.3f}')

# log-log scatter (작은 flow 까지)
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
axes[0].scatter(flat_obs, flat_pred, s=3, alpha=0.2, color='steelblue')
axes[0].plot([0, flat_obs.max()], [0, flat_obs.max()], 'r--', alpha=0.6)
axes[0].set_xlabel('Observed T_ij'); axes[0].set_ylabel('Predicted T_ij')
axes[0].set_title('linear scale'); axes[0].grid(alpha=0.3)

axes[1].scatter(flat_obs+1, flat_pred+1, s=3, alpha=0.2, color='steelblue')
axes[1].plot([1, flat_obs.max()+1], [1, flat_obs.max()+1], 'r--', alpha=0.6)
axes[1].set_xscale('log'); axes[1].set_yscale('log')
axes[1].set_xlabel('Observed T_ij + 1'); axes[1].set_ylabel('Predicted T_ij + 1')
axes[1].set_title('log-log (small flows)'); axes[1].grid(alpha=0.3)
plt.show()"""),

MD("""## 10. 검증 2 — Trip Length Distribution

관측 vs 예측 TLD 가 일치하면 거리 모델링이 맞다는 신호."""),

CODE("""flat_d = dist_km[mask]
bins = np.arange(0, 31, 1)
tld_obs, _  = np.histogram(flat_d, bins=bins, weights=flat_obs)
tld_pred, _ = np.histogram(flat_d, bins=bins, weights=flat_pred)
centers = (bins[:-1] + bins[1:]) / 2

fig, ax = plt.subplots(figsize=(11, 5))
w = 0.4
ax.bar(centers - w/2, tld_obs/tld_obs.sum(),   width=w, label='Observed',  color='steelblue', alpha=0.8)
ax.bar(centers + w/2, tld_pred/tld_pred.sum(), width=w, label='Predicted', color='indianred', alpha=0.8)
ax.set_xlabel('distance (km)'); ax.set_ylabel('통행 비율')
ax.set_title('Trip Length Distribution — 관측 vs 예측')
ax.legend(); ax.grid(alpha=0.3, axis='y'); plt.show()

print(f'평균 통행거리 — 관측  : {(flat_d * flat_obs).sum() / flat_obs.sum():.2f} km')
print(f'평균 통행거리 — 예측  : {(flat_d * flat_pred).sum() / flat_pred.sum():.2f} km')"""),

MD("""## 11. 검증 3 — Top-100 flow lines"""),

CODE("""T_pred_nd = T_pred.copy(); np.fill_diagonal(T_pred_nd, 0)
top = np.argsort(T_pred_nd.flatten())[::-1][:100]
i_top, j_top = np.unravel_index(top, T_pred_nd.shape)

lines = [{'src': i, 'dst': j, 'flow': T_pred_nd.flatten()[k],
          'geometry': LineString([Point(coords[i]), Point(coords[j])])}
         for k, (i, j) in enumerate(zip(i_top, j_top))]
flows = gpd.GeoDataFrame(lines, crs=5179)

fig, ax = plt.subplots(figsize=(13, 11))
g.boundary.plot(ax=ax, color='lightgray', linewidth=0.3)
g.plot(column='A_obs', cmap='Reds', ax=ax, linewidth=0,
       vmax=g['A_obs'].quantile(0.95), alpha=0.6)

maxf = flows['flow'].max()
for _, row in flows.iterrows():
    lw = 0.3 + 3 * (row['flow'] / maxf)
    p1, p2 = row.geometry.coords
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', alpha=0.3, linewidth=lw)

ax.set_title('Top-100 예측 OD flow lines\\n(배경 = A_obs 도착량)')
ax.set_axis_off(); plt.show()
print(f'top-100 flow 합 : {flows["flow"].sum():,.0f}')"""),

MD("""**face validity** — 강남·종로·여의도가 attractor 로 보이는가?
외곽 베드타운이 producer 로 보이는가?"""),

MD("""## 12. 검증 4 — Intrazonal share"""),

CODE("""intra_obs  = np.diag(T_obs);  intra_pred = np.diag(T_pred)
share_obs  = np.where(T_obs.sum(axis=1)  > 0, intra_obs  / T_obs.sum(axis=1),  0)
share_pred = np.where(T_pred.sum(axis=1) > 0, intra_pred / T_pred.sum(axis=1), 0)

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(g.geometry.area/1e6, share_obs,  s=12, alpha=0.6, label='Observed',  color='steelblue')
ax.scatter(g.geometry.area/1e6, share_pred, s=12, alpha=0.6, label='Predicted', color='indianred')
ax.set_xlabel('admdong area (km²)'); ax.set_ylabel('intrazonal share T_ii / Σ T_ij')
ax.set_xscale('log'); ax.set_title('Intrazonal share — admdong 면적과 관계')
ax.legend(); ax.grid(alpha=0.3); plt.show()"""),

MD("""## 13. 시간대별 β_d 변화 — 출근 vs 야간

```
시간대 분해 의미
─────────────────────────────────
출근시간 (7-9시)   장거리 통근 ↑ → β_d 절대값 ↓ (덜 가파름)
주간   (10-16시)   일반 이동
퇴근시간 (17-19시)
야간   (22-5시)    단거리 ↑     → β_d 절대값 ↑ (가파름)
```"""),

CODE("""def fit_band(od_sub):
    od_a = od_sub.groupby(['O_ADMDONG_CD','D_ADMDONG_CD'], as_index=False)['CNT'].sum()
    od_a['i'] = od_a['O_ADMDONG_CD'].map(adm_idx); od_a['j'] = od_a['D_ADMDONG_CD'].map(adm_idx)
    od_a = od_a.dropna(subset=['i','j'])
    od_a['i'] = od_a['i'].astype(int); od_a['j'] = od_a['j'].astype(int)
    T = np.zeros((n, n)); T[od_a['i'].values, od_a['j'].values] = od_a['CNT'].values
    P_t = T.sum(axis=1); A_t = T.sum(axis=0)
    fl = pd.DataFrame({
        'T': T[mask],
        'log_P': np.log(P_t[i_idx[mask]] + 1),
        'log_A': np.log(A_t[j_idx[mask]] + 1),
        'd':     dist_km[mask],
    })
    glm_t = sm.GLM(fl['T'], sm.add_constant(fl[['log_P','log_A','d']]),
                   family=sm.families.Poisson()).fit()
    return glm_t.params['log_P'], glm_t.params['log_A'], glm_t.params['d'], T.sum()

bands = [
    ('전체',          od),
    ('출근 (7-9)',    od[od['ST_TIME_CD'].between(7, 9)]),
    ('주간 (10-16)',  od[od['ST_TIME_CD'].between(10, 16)]),
    ('퇴근 (17-19)',  od[od['ST_TIME_CD'].between(17, 19)]),
    ('야간 (22-5)',   od[od['ST_TIME_CD'].isin(list(range(22,24)) + list(range(0,6)))]),
]
results = [(lbl,) + fit_band(sub) for lbl, sub in bands]
res_df = pd.DataFrame(results, columns=['시간대','α','β','β_d','T_sum']).round(3)
print(res_df.to_string(index=False))

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(res_df['시간대'], res_df['β_d'], color='steelblue', edgecolor='white')
ax.set_ylabel('β_d (km⁻¹)')
ax.set_title('시간대별 거리 deterrence — 음수, 절대값 클수록 단거리 dominate')
ax.grid(alpha=0.3, axis='y'); plt.xticks(rotation=15); plt.tight_layout(); plt.show()"""),

MD("""## 14. od_matrix_v1.parquet 저장"""),

CODE("""ii, jj = np.indices((n, n))
flat_out = pd.DataFrame({
    'adm_O_haengan': g['adm_cd_haengan'].values[ii.flatten()],
    'adm_D_haengan': g['adm_cd_haengan'].values[jj.flatten()],
    'adm_O_nm':      g['adm_nm'].values[ii.flatten()],
    'adm_D_nm':      g['adm_nm'].values[jj.flatten()],
    'T_obs':         T_obs.flatten(),
    'T_pred':        T_pred.flatten(),
    'distance_km':   dist_km.flatten(),
})
flat_out['residual'] = flat_out['T_obs'] - flat_out['T_pred']
flat_out = flat_out[(flat_out['T_obs'] > 0) | (flat_out['T_pred'] > 0.5)].reset_index(drop=True)
print(f'OD pairs : {len(flat_out):,}')

od_path = os.path.join(OUT_DIR, 'od_matrix_v1.parquet')
flat_out.to_parquet(od_path)
print(f'saved : {od_path}  ({os.path.getsize(od_path)/1e6:.2f} MB)')"""),

MD("""## 15. 정리 — 강좌 마무리

학습한 것:
- **Gravity model** = "사람 많은 곳 → 사람 많은 곳" 의 행동 유도
- **Poisson GLM** = count 데이터의 right likelihood, log-OLS 보다 정직
- **IPF/Furness** ~ 10 iter 으로 marginal 보존
- 검증 4종 — **정량 (RMSE/MAPE/R²)** + **정성 (TLD, flow, intrazonal)**
- 시간대별 β_d 변화 — 출근시간 (덜 가파름) vs 야간 (가파름)

본 강좌가 보인 것:

> **stock 데이터 + 도로·토지이용 + 관측 OD** 로 4단계 모형 1·2단계의 baseline 을 실데이터로 fit 하고 검증.

후속 (강좌 외):
- KHTS 매칭 → β recalibration
- Network distance (한강·고속도로 효과)
- Mode choice / Network assignment (3·4단계)"""),

CODE("""print('OK')
print(f'OD pairs        : {len(flat_out):,}')
print(f'IPF iter        : {len(hist)}')
print(f'final max err   : {hist[-1]:.5f}')
print(f'R² (i!=j)       : {r2:.3f}')
print(f'RMSE            : {rmse:.2f}')
print(f'산출            : {od_path}')"""),
]

if __name__ == '__main__':
    HERE = os.path.dirname(__file__)
    write_both(cells,
               os.path.join(HERE, '..', 'notebooks', '04_od_estimation.ipynb'),
               os.path.join(HERE, '..', 'slides', '04_od_estimation.md'))
