"""05_superblock_landuse.ipynb — Superblock + 토지이용 (도시 형태 부록 트랙)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbgen import MD, CODE, write_both

cells = [
MD("""# Lecture 5 — Superblock + 토지이용 (부록)

> 도로 자연 경계로 907 개 superblock 을 만들어
> 토지이용 다양성을 Shannon entropy 로 측정한다.

**왜** : admdong 보다 "도시 조직" 단위에 가까운 분석 단위.
통행 수요 외 도시 형태 진단 (mixed-use, 직주근접) 에 활용.

**4단계 모형 위치** : 메인 트랙 외 부록 — 통행 수요와 별개의
도시 형태 (urban form) 트랙

**사전지식** : `oa_master.parquet` (Lecture 2)

**이번 시간 산출** : `block_master.parquet` — superblock × LU·entropy

```
Lecture 5 의 위치 — 통행 수요 메인과 분리된 별도 부록
─────────────────────────────────────────────────────
Lec1, Lec2 ─→ oa_master ──┬─→ Lec3, Lec4 통행 수요 (admdong) — 메인
                          │
                          └─→ Lec5: superblock + LU ← 본 모듈
                                  (도시 조직 분석, 부록 트랙)
```

→ 메인 트랙 (Lecture 3·4) 와 무관하게 단독 수강 가능
→ Lecture 4 의 `od_matrix_v1` 와 직접 입출력 X

다룰 항목:
- 907 도시 superblock (도로 자연 경계)
- 토지이용 11 zone class 의 superblock 단위 share
- Shannon entropy 로 mixed-use 도시 조직 측정
- `block_master.parquet` — 도시 형태 진단 + 뷰어 자산"""),

MD("""## 1. Superblock 이란

```
Superblock 정의
──────────────────────────────────────────────────
간선 도로 (ROA_CLS_SE 1-3) 가 그어둔 자연 cell 안에
같은 cell 의 도시 OA 들을 묶어 만든 단위

  ┌─── 간선 도로 ───┐
  │ OA OA OA OA OA │  ← cell 안의 OA 들 dissolve
  │ OA OA OA OA OA │     → 1개 superblock
  └─── 간선 도로 ───┘

생성 알고리즘 (build_blocks_oa.py)
──────────────────────────────────────────────────
1. arterial polygonize  → 1,647 cell  (≥1000 m² 필터)
2. OA × parcels overlay → jimok_kind 비율
   - 임야 ≥ 50% → 산지 (326 OA)
   - 하천 ≥ 50% → 수계 (140 OA)
   - 그 외      → 도시 (18,631)
3. 도시 OA → cell 매칭 (max-overlap)
4. 같은 cell OA dissolve → 907 superblock
```

| 단위 | 개수 | median 면적 |
|---|---:|---:|
| OA | 19,097 | 12k m² |
| **superblock** | **907** | **264k m²** ≈ 510×510m |"""),

MD("""## 0. Imports & paths"""),

CODE("""import os, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
%matplotlib inline
plt.rcParams['figure.figsize'] = (10, 7)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

ROOT = r'F:\\research\\TAZ'
DRV  = os.path.join(ROOT, 'data', 'derived')
OUT_DIR = os.path.join(DRV, 'lecture_outputs')
os.makedirs(OUT_DIR, exist_ok=True)
print('OK')"""),

MD("""## 2. 907 superblock 로드 + 기본 통계"""),

CODE("""# seoul_blocks.fgb = superblock 폴리곤 + LU 컬럼
blk = gpd.read_file(os.path.join(DRV, 'seoul_blocks.fgb'))

# oa_count + dominant adm_cd 는 oa_to_block 에서 계산 머지
o2b = pd.read_parquet(os.path.join(DRV, 'oa_to_block.parquet'))
o2b_city = o2b[o2b['block_id'] >= 0]
oa_count = o2b_city.groupby('block_id').size().rename('oa_count')
adm_dom  = (o2b_city.groupby('block_id')['adm_cd']
                    .agg(lambda s: s.value_counts().idxmax())
                    .rename('adm_n'))
blk = blk.merge(oa_count, on='block_id', how='left')
blk = blk.merge(adm_dom,  on='block_id', how='left')

print(f'superblock : {len(blk)}')
print(f'컬럼      : {list(blk.columns)}')"""),

CODE("""# 면적·형상 분포
print('면적 m²')
print(f'  median {blk["area_m2"].median():>10,.0f}')
print(f'  p10    {blk["area_m2"].quantile(0.1):>10,.0f}')
print(f'  p90    {blk["area_m2"].quantile(0.9):>10,.0f}')
print(f'  max    {blk["area_m2"].max():>10,.0f}')

print(f'\\nshape_idx (1=원, 1.5=정사각, 큼=길쭉)')
print(f'  median {blk["shape_idx"].median():.2f}')
print(f'  p90    {blk["shape_idx"].quantile(0.9):.2f}')

print(f'\\noa_count (block 당 OA 개수)')
print(f'  median {blk["oa_count"].median():.0f}')
print(f'  max    {blk["oa_count"].max():.0f}')

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].hist(np.log10(blk['area_m2']), bins=50, color='steelblue', edgecolor='white')
axes[0].set_xlabel('log10(area m²)'); axes[0].set_ylabel('블록 수')
axes[0].set_title('면적 분포'); axes[0].grid(alpha=0.3, axis='y')

axes[1].hist(blk['shape_idx'].clip(upper=4), bins=40, color='steelblue', edgecolor='white')
axes[1].set_xlabel('shape_idx'); axes[1].set_ylabel('블록 수')
axes[1].set_title('형상 지수 분포'); axes[1].grid(alpha=0.3, axis='y')
plt.show()"""),

MD("""## 3. 토지이용 (LU) — 11 zone class

```
LSMD 용도지역 11 클래스
──────────────────────────────────────────
주거    : 전용주거, 일반주거_저밀(1종), 중밀(2종), 고밀(3종), 준주거
상업    : 중심·일반상업, 근린·유통상업
공업    : 전용공업, 일반·준공업
녹지    : 보전·자연녹지, 생산녹지

infra (block 의 비건축 면적):
──────────────────────────────────────────
road_share, rail_share, water_share, transit_share, public_share
```

각 superblock = 11 클래스의 면적 share 분포 + infra 5종 share."""),

CODE("""# block_landuse.parquet = long format (block_id × zone_class × area_share)
blu = pd.read_parquet(os.path.join(DRV, 'block_landuse.parquet'))
print(f'block_landuse shape : {blu.shape}')
print(f'컬럼 : {list(blu.columns)}')
print(blu.head(6))

# long → wide pivot (한 block 의 11 클래스 share)
wide_lu = blu.pivot_table(index='block_id', columns='zone_class',
                          values='area_share', aggfunc='sum', fill_value=0)
print(f'\\nwide shape : {wide_lu.shape}  (block × zone_class)')
print(wide_lu.head(3).round(2))"""),

MD("""## 4. dominant LU + buildable_share

각 superblock 의:
- `major_lu` = 가장 큰 zone class
- `major_share` = 그 비중
- `buildable_share` = 건축 가능 토지 비율 (도로·철도·하천·교통·공공 제외)"""),

CODE("""# major_lu 분포
print('major_lu 분포 (superblock 카운트):')
print(blk['major_lu'].value_counts())

# buildable_share 분포
print(f'\\nbuildable_share')
print(f'  median {blk["buildable_share"].median():.2f}')
print(f'  p10    {blk["buildable_share"].quantile(0.1):.2f}')
print(f'  p90    {blk["buildable_share"].quantile(0.9):.2f}')"""),

CODE("""# major_lu choropleth
LU_COLOR = {
    '전용주거': '#FFE082', '일반주거_저밀(1종)': '#FFC107', '일반주거_중밀(2종)': '#FB8C00',
    '일반주거_고밀(3종)': '#E64A19', '준주거': '#B71C1C',
    '중심·일반상업': '#7B1FA2', '근린·유통상업': '#BA68C8',
    '일반·준공업': '#455A64',
    '보전·자연녹지': '#43A047', '생산녹지': '#9CCC65',
}

fig, ax = plt.subplots(figsize=(13, 11))
for cls, color in LU_COLOR.items():
    sub = blk[blk['major_lu'] == cls]
    if len(sub): sub.plot(ax=ax, color=color, edgecolor='white', linewidth=0.2,
                          label=f'{cls} ({len(sub)})')
ax.legend(loc='lower left', fontsize=8, ncol=2)
ax.set_title('서울 superblock — major LU choropleth')
ax.set_axis_off(); plt.show()"""),

MD("""## 5. Shannon entropy — mixed-use 측정

```
Shannon entropy 정의
──────────────────────────────────────
H = -Σ p_i · log(p_i)        (p_i = i 클래스의 면적 share)

해석:
  H = 0   : 한 클래스가 100% (homogeneous)
  H 클수록: 여러 클래스 골고루 (mixed-use)
  H max   : log(11) ≈ 2.40 (균등 분포)
```

전통 도시계획에서 mixed-use 가 보행성·생활편의·통행 패턴에 미치는 영향을 측정하는 표준 지표."""),

CODE("""# entropy 계산 — block 별 11 클래스 분포의 Shannon entropy
def shannon(row):
    p = row[row > 0]
    p = p / p.sum()
    return -(p * np.log(p)).sum()

wide_lu['zone_entropy'] = wide_lu.apply(shannon, axis=1)
blk = blk.merge(wide_lu[['zone_entropy']], on='block_id', how='left')

print(f'zone_entropy 분포')
print(f'  median {blk["zone_entropy"].median():.2f}')
print(f'  p90    {blk["zone_entropy"].quantile(0.9):.2f}')
print(f'  max    {blk["zone_entropy"].max():.2f}    (이론 최대: log(11) = {np.log(11):.2f})')

# entropy 상위 10개 (가장 mixed-use)
top_mix = blk.nlargest(10, 'zone_entropy')[['block_id','adm_n','area_m2','major_lu','zone_entropy']]
print(f'\\n가장 mixed-use 인 superblock top 10:')
print(top_mix.to_string(index=False))"""),

CODE("""# entropy choropleth
fig, ax = plt.subplots(figsize=(13, 11))
blk.plot(column='zone_entropy', cmap='viridis', ax=ax,
         vmin=0, vmax=blk['zone_entropy'].quantile(0.95),
         linewidth=0, legend=True,
         legend_kwds={'label': 'Shannon entropy', 'shrink': 0.6},
         missing_kwds={'color': 'lightgray'})
ax.set_title('서울 superblock — 토지이용 Shannon entropy\\n(밝을수록 mixed-use)')
ax.set_axis_off(); plt.show()"""),

MD("""## 6. OA 인구·LP → block 합산

`oa_master` 의 OA 단위 변수를 `block_id` 합산해 블록 단위로.

```
OA → block 합산 흐름
─────────────────────────────────
oa_master ─┬─ sum: pop_total, hh_count, ho_total, area_m2
           ├─ sum: lp_pool_* (시간풀별 인구)
           └─ 인구가중 mean: aging_idx, hh_avg_size
              (가중평균 = (값 × 인구).sum() / 인구.sum())
```"""),

CODE("""m = gpd.read_parquet(os.path.join(DRV, 'oa_master.parquet'))
m = m[m['block_id'] != -1].copy()   # 산/강 제외

sum_cols = ['pop_total','hh_count','ho_total','area_m2',
            'lp_pool_resident_02_05','lp_pool_morning_07_10',
            'lp_pool_midday_11_15','lp_pool_evening_18_21','lp_pool_24h']
agg = m.groupby('block_id')[sum_cols].sum().reset_index()

# 인구가중 mean
def wmean(g, val, w='pop_total'):
    ww = g[w].fillna(0); v = g[val]
    return float((v*ww).sum() / ww.sum()) if ww.sum() > 0 else v.mean()

for c in ['aging_idx','hh_avg_size']:
    s = m.groupby('block_id').apply(lambda g: wmean(g, c)).rename(f'{c}_w')
    agg = agg.merge(s.reset_index(), on='block_id')

# block_master 통합
bm = blk.merge(agg, on='block_id', how='left', suffixes=('','_oa'))
# area_m2 가 중복 (block geometry vs OA 합) — block 의 것 우선
if 'area_m2_oa' in bm.columns: bm = bm.drop(columns='area_m2_oa')

print(f'block_master shape : {bm.shape}')
print('주요 컬럼:')
print([c for c in bm.columns if c not in ['geometry']][:15])"""),

CODE("""# 저장 — 도시 조직 진단 마스터
bm_path = os.path.join(OUT_DIR, 'block_master.parquet')
bm.to_parquet(bm_path)
print(f'saved : {bm_path}  ({os.path.getsize(bm_path)/1e6:.2f} MB)')

# 검증값
print('\\n검증:')
print(f'  pop_total 합계   : {bm["pop_total"].sum()/1e6:.2f}M')
print(f'  hh_count 합계    : {bm["hh_count"].sum()/1e6:.2f}M')
print(f'  결측 (pop_total) : {bm["pop_total"].isna().sum()}')"""),

MD("""## 7. 한 자치구 zoom-in — superblock + LU 종합 view"""),

CODE("""# 강남구 SGIS code = 11230
target_sgg = '11230'
m['sgg_cd'] = m['ADM_CD'].astype(str).str[:5]
target_blocks = m[m['sgg_cd'] == target_sgg]['block_id'].dropna().unique()
print(f'강남구 superblock : {len(target_blocks)}')

fig, ax = plt.subplots(figsize=(12, 12))
target_bm = bm[bm['block_id'].isin(target_blocks)]
for cls, color in LU_COLOR.items():
    sub = target_bm[target_bm['major_lu'] == cls]
    if len(sub):
        sub.plot(ax=ax, color=color, edgecolor='white', linewidth=0.5,
                 label=f'{cls} ({len(sub)})')
target_bm.boundary.plot(ax=ax, color='black', linewidth=0.6)
ax.set_title(f'강남구 ({target_sgg}) — superblock {len(target_bm)}개')
ax.legend(loc='lower right', fontsize=8)
ax.set_axis_off(); plt.show()"""),

MD("""## 8. 정리

- **907 도시 superblock** = 간선 도로(ROA_CLS_SE 1-3) 안의 OA 들 dissolve
- **major_lu, buildable_share** = 블록의 대표 용도 + 건축 가능 비율
- **Shannon entropy** = mixed-use 측정 (0 ~ log(11)=2.40)
- **block_master.parquet** = 도시 조직 진단 + 뷰어 자산
- Lecture 3·4 통행 수요는 admdong 단위로 별도 메인 트랙

→ **강좌 종료** — 메인 트랙 (Lecture 3·4) 와 함께 학습하면 도시 형태 ↔ 통행 패턴 의 관계를 입체적으로 볼 수 있음."""),

CODE("""print('OK')
print(f'superblock          : {len(bm)}')
print(f'major_lu 종류       : {bm["major_lu"].nunique()}')
print(f'block_master 저장   : {bm_path}')"""),
]

if __name__ == '__main__':
    HERE = os.path.dirname(__file__)
    write_both(cells,
               os.path.join(HERE, '..', 'notebooks', '05_superblock_landuse.ipynb'),
               os.path.join(HERE, '..', 'slides', '05_superblock_landuse.md'))
