# TAZ 데이터 명세

서울 토지이용 · 도로 · 교통존 데이터를 raw / derived / viewer 세 계층으로 정리.

```
data/
├─ raw/        # 외부에서 받은 원본. 수정 금지.
│  ├─ lsmd_zoning/        국토부 LSMD 용도지역지구도 필지
│  ├─ ktdb_taz/           KTDB 2010 교통주제도
│  ├─ roads/              국토지리정보원 도로중심선 + 도로명주소 도로구간
│  ├─ sgis_oa/            통계청 SGIS 집계구 경계 2025-2Q (인구센서스 단위, 권위)
│  ├─ sgis_oa_2016/       통계청 SGIS 집계구 경계 2016년 기준 (서울 생활인구의 매핑 기반)
│  ├─ sgis_census/        통계청 SGIS 집계구별 인구·가구·주택 통계 (2024)
│  ├─ seoul_living_pop/   서울 열린데이터 광장 집계구별 시간대별 생활인구 (내국인)
│  ├─ seoul_living_movement/  서울 열린데이터 광장 행정동·자치구 단위 OD (생활이동, KT)
│  └─ admdong_boundary/   행정동 경계 폴리곤 (전국 3,516)
├─ derived/    # 우리가 가공해 분석에 직접 쓰는 산출물
└─ viewer/     # deck.gl 웹 뷰어용 슬림 사본 (WGS84)
```

CRS 표기 — EPSG:5179 (Korea 2000 / Unified CS), EPSG:5186 (Korea 2000 / Central Belt 2010), EPSG:4326 (WGS84).

---

## raw/

### `raw/lsmd_zoning/AL_D154_11_20260412/`

| 항목 | 값 |
|---|---|
| 출처 | 국토교통부 공간정보 (LSMD 용도지역지구도) |
| 기준일 | 2026-04-12 |
| 다운로드 ID | `AL_D154_11_20260412` |
| 형식 | ESRI Shapefile (`.shp/.dbf/.shx/.prj/.fix`) |
| CRS | EPSG:5186 |
| 행 수 | 899,432 필지 |
| 사이즈 | 약 1.5 GB |

**컬럼 (필지 다중 코드)**
| 컬럼 | 의미 |
|---|---|
| `A2` | 행정 위치 ("서울특별시 ~~구 ~~동") |
| `A4` | 토지대장 / 임야대장 구분 |
| `A5` | 지번 |
| `A7` | 용도지역·지구·구역 코드 (콤마 결합 다중 값, 예 `UQA01X,UQA122,UQQ300,...`) |
| `A8` | A7에 대응하는 한글 명칭 (콤마 결합) |

**용도지역 코드 분류 11클래스** — `seoul_zoning_viz/export_zoning.py`의 `ZONE_CLASS_MAP`이 단일 진실. 동일 매핑이 `export_parcels.py`에 복제돼 있음.

압축본 `AL_D154_11_20260412.zip` (151 MB)도 동봉.

`_inspect.json` — 데이터 검사용 결과(코드 분포, 시군구 분포, sample 5건). 필요 시 참고.

### `raw/ktdb_taz/`

| 항목 | 값 |
|---|---|
| 출처 | 국가교통DB (KTDB) — 2010 교통주제도 |
| 기준 시점 | 2009년 통행 OD |
| 형식 | (zip 안의 SHP) `[01]교통분석 존/T1110G.shp` |
| CRS | EPSG:5174 |
| 인코딩 | cp949 |

**현재 zip 파일 부재** — 산출물 `data/derived/seoul_taz.geojson`만 보존돼 있음. 재생성 시 KTDB에서 `2010-TM-GR-MR-CET 교통존(2009년 기준).ZIP`을 다시 받아 `data/raw/ktdb_taz/` 에 풀어넣어야 함.

T1110G.shp의 주요 컬럼:
| 컬럼 | 의미 |
|---|---|
| `TAZ_ID` | TAZ 정수 ID |
| `TAZ_NAME` | 한글 명칭 (자치구) |
| `UPTAZ_ID` | 상위 존 (서울 = `1`) |
| `TAZ_TYPE` | 존 타입 (자치구 = `2`) |

### `raw/roads/centerline/N3L_A0020000_11.shp`

| 항목 | 값 |
|---|---|
| 출처 | 국토지리정보원 — 연속수치지형도 (도로중심선) |
| 기준일 | 2025-08 |
| CRS | EPSG:5179 (PROJCS: KGD2002_Unified_Coordinate_System) |
| 행 수 | 414,791 LineString |
| 사이즈 | 217 MB (사이드카 포함) |

**컬럼**
| 컬럼 | 의미 |
|---|---|
| `UFID` | 도형 고유 ID |
| `RDDV` | 도로분류 — `RDD001` 고속, `RDD002` 국도, `RDD003` 지방도, `RDD004` 특별시도, `RDD005` 시도, `RDD006` 군도, `RDD007` 구도, `RDD008` 시군구도로, `RDD009` 기타도로, `RDD000` 미분류 |
| `RDLN` | 차선 수 |
| `RVWD` | 도로폭 (m) |
| `PVQT` | 포장 질 (`RDQ005` 아스팔트, `RDQ006` 콘크리트, `RDQ000` 미분류) |
| `DVYN` | 중앙분리대 (`CSU001` 유, `CSU002` 무) |
| `ONSD` | 일방통행 (`ITH001` 일방, `ITH002` 양방) |
| `SCLS` | 표준노드링크 등급 코드. `A0021` 고속, `A0022` 일반국도, `A00231` 시도, 그 외 시군구도로 |
| `NAME` | 도로명 (대부분 빈값) |
| `RDNU` | 도로번호 |
| `FMTA` | 작도 메타 |

`SCLS`와 `RDDV`의 등급이 일치하지 않는 경우가 많음 — 본 프로젝트는 `RDDV`보다 **도로구간 SHP의 `ROA_CLS_SE`**를 권위 등급으로 사용.

### `raw/sgis_oa/bnd_oa_11_2025_2Q.shp`

| 항목 | 값 |
|---|---|
| 출처 | 통계청 SGIS — 집계구 경계 (Output Area boundary) |
| 기준일 | 2025-06-30 (2025년 2분기) |
| CRS | EPSG:5179 (KGD2002 Unified, PROJCS deprecated 표기지만 좌표는 5179) |
| 인코딩 | UTF-8 (`.cpg` 동봉) |
| 행 수 | **19,097 폴리곤** (서울 전역) |
| 면적 | median 11,608 m² · p10 6,003 / p90 36,903 / max 9.66 km² (남산·관악산 산지) |
| 총 면적 | 605.3 km² (zoning 합과 일치) |

**컬럼**
| 컬럼 | 의미 |
|---|---|
| `BASE_DATE` | 기준일 (YYYYMMDD) |
| `ADM_CD` | 행정동 코드 8자리. 앞 5자리는 시군구 (`11010` = 종로구) |
| `TOT_OA_CD` | 집계구 코드 14자리. `ADM_CD(8)` + 일련번호(6) — 행정동 ⊃ 집계구 계층 |

집계구는 **인구센서스 단위 (약 500세대 기준)** 로 통계청이 그어둔 가장 작은 공식 격자. 본 프로젝트의 superblock(1,647개, 도로망 기반)보다 약 12배 잘게 나뉘며, 도로 폭까지 포함해 서울을 **빠짐없이** 덮음. SGIS 인구·가구·주택유형 통계를 `TOT_OA_CD`로 join 받을 수 있고, `derived/oa_to_block.parquet` 면적가중 매핑을 통해 superblock의 P_i / A_j 입력 변수로 disaggregate 됨.

압축본 `bnd_oa_11_2025_2Q.zip` (17 MB)도 동봉.

### `raw/sgis_oa_2016/` (서울 생활인구의 매핑 기반 — 2016 SGIS 집계구)

| 항목 | 값 |
|---|---|
| 출처 | 통계청 SGIS — 통계지역경계 2016년 기준 (`통계지역경계(2016년+기준).zip` 풀어서 보존) |
| 기준일 | 2016년 |
| CRS | **EPSG:5179** (readme: UTM-K GRS80. 파일에 .prj 없으니 코드에서 명시 부여 필요) |
| 인코딩 | cp949 (.dbf) |
| 파일 | `집계구.shp`(19,153 폴리곤) · `행정구역.shp`(424 행정동 폴리곤) · zip 내부 zip 부속파일들 (.sbn/.sbx 등) |

**`집계구.shp` 컬럼**

| 컬럼 | 자릿수 | 의미 |
|---|---:|---|
| `TOT_REG_CD` | 13 | **2016 SGIS 집계구 코드 = LOCAL_PEOPLE `집계구코드` 와 완전 일치** |
| `ADM_CD` | 7 | 2016 SGIS 행정동 코드 (424개) |
| `ADM_NM` | — | 행정동 한글명 (`사직동`, `삼청동`, …) |

**왜 중요한가** — 서울 열린데이터 광장의 LOCAL_PEOPLE 생활인구 데이터는 **이 2016 경계로 발급된 13자리 집계구 코드를 그대로 유지** 한다. 검증: LOCAL_PEOPLE 2024-12 샘플의 13자리 `집계구코드` 19,149개가 이 SHP의 `TOT_REG_CD` 와 100% 일치. 따라서 LOCAL_PEOPLE 의 공간 경계는 2016 SGIS 집계구로 보면 됨.

**2016 ↔ 2025 SGIS 관계**

| 항목 | 2016 → 2025 |
|---|---|
| `ADM_CD` | 7자리 → 8자리. **단순 `× 10` (zero-pad)** 변환. 419/426 일치. 7개만 분동·통합으로 별도 처리 (예: `1123051` → 2개 ADM 으로 split) |
| `TOT_REG_CD`(13) ↔ `TOT_OA_CD`(14) | 단순 변환 불가. 약 50개 OA 재구획 (19,153 → 19,097). **공간 교차로 면적가중 매핑 산출 필요** |

원본 zip `통계지역경계(2016년+기준).zip` 도 같은 폴더에 보존. 추출본은 git 추적 제외 권장.

### `raw/sgis_census/` (2024년 인구·가구·주택 통계, 10개 CSV)

| 항목 | 값 |
|---|---|
| 출처 | 통계청 SGIS — 집계구 단위 통계 다운로드 (`raw/sgis_census/_census_reqdoc_1777742403012.zip` 풀어서 보존, 50 MB) |
| 기준 시점 | 2024년 (인구주택총조사 등록센서스) |
| 인코딩 | **cp949** (모든 CSV) |
| 헤더 | **없음** (첫 줄부터 데이터) |
| 공통 스키마 | `year(int)`, `TOT_OA_CD(str14)`, `var_code(str)`, `value(str)` — long format. `value`는 통계 보호로 `N/A`인 셀이 있음. |
| Join 키 | `TOT_OA_CD` ↔ `raw/sgis_oa/.../TOT_OA_CD` (14자리, **완전 일치**) |
| 행정 위계 | OA 14자리 = ADM_CD(8) + 일련번호(6). 행정동 단위 집계는 앞 8자리로 group by. |

**파일별 변수 코드 분포** (변수 코드 의미는 SGIS 변수사전 기준)

| 파일 | 변수 코드 | OA 행 수 | 의미 (대표) |
|---|---|---:|---|
| `11_2024년_인구총괄(총인구).csv` | `to_in_001`/`007`/`008` | 3 × 19,097 | 총인구 / 남자 / 여자 |
| `11_2024년_인구총괄(인구밀도).csv` | `to_in_003` | 19,097 | 인구밀도 (인/km²) |
| `11_2024년_인구총괄(노령화지수).csv` | `to_in_004` | 19,097 | 노령화지수 (65+ / 0-14 × 100) |
| `11_2024년_성연령별인구.csv` | `in_age_001`–`in_age_081` | ≈ 1,047,777 | 성×5세 단위 인구 (전체 코드 분포는 SGIS 변수사전 참조) |
| `11_2024년_가구총괄.csv` | `to_ga_001`/`002` | 2 × 19,097 | 가구 수 / 평균가구원수 |
| `11_2024년_세대구성별가구.csv` | `ga_sd_001`–`ga_sd_006` | 92,433 | 세대구성별 (1세대·2세대·3세대·4세대 이상·1인·비친족) 가구 수 |
| `11_2024년_주택총괄_총주택(거처)수.csv` | `to_ho_001` | 19,097 | 총 주택(거처) 수 |
| `11_2024년_주택유형별주택.csv` | `ho_gb_001`–`ho_gb_006` | 50,614 | 단독·아파트·연립·다세대·비거주용·기타 |
| `11_2024년_연건평별주택.csv` | `ho_ar_001`–`ho_ar_009` | 93,740 | 9개 연면적 구간별 주택 수 |
| `11_2024년_건축년도별주택.csv` | `ho_yr_001`–`ho_yr_020` | 88,709 | 20개 건축년도 구간별 주택 수 |

코드의 정확한 카테고리 매핑은 SGIS 변수사전(통계청 SGIS 사이트 → 통계주제도 → 통계자료 → 변수사전)에서 받아야 함 — 압축 zip의 별첨 명세 파일은 zip 내부에 포함돼 있지 않음. 필요 시 `derived/sgis_var_dict.csv`로 별도 정리할 것.

원본 zip은 같은 폴더에 보존. CSV는 zip을 풀어 둔 결과물이지만 git 추적에서는 zip만 추가하고 풀어진 CSV는 `.gitignore` 권장 (재생성 가능).

### `raw/seoul_living_pop/` (서울 생활인구 — 집계구 단위, 시간대별 내국인)

| 항목 | 값 |
|---|---|
| 출처 | 서울 열린데이터 광장 — 서울 생활인구 (집계구 단위, 내국인) — `data.seoul.go.kr/dataList/OA-14979/F/1/datasetView.do` |
| 현재 보유 | `raw/seoul_living_pop/LOCAL_PEOPLE_202412.zip` (3.7 GB 압축, 2024-12 한 달치 31일) — **zip 그대로 보존**. 압축 해제 시 ≈ 3.9 GB. |
| 일별 파일 | zip 내부 `LOCAL_PEOPLE_YYYYMMDD.csv`, **각 ≈ 126 MB · 459,648 행** (24시간 × 19,152 OA) |
| 권장 사용 | `zipfile` 모듈로 in-place 스트리밍 (예: `with zipfile.ZipFile(...).open(name) as fh:`). 디스크에 풀지 않음. |
| 인코딩 | **cp949** · 헤더 첫 행에 BOM(`\xef\xbb\xbf`)이 들어가 있어 첫 컬럼명이 `?"기준일ID"` 처럼 보일 수 있음 |
| 형식 | CSV (모든 셀이 큰따옴표로 감싸짐), 시간대별 wide format |

**컬럼 (33개)**

| 컬럼 | 의미 |
|---|---|
| `기준일ID` | 날짜 `YYYYMMDD` |
| `시간대구분` | 시간 `00`–`23` (2자리 zero-pad) |
| `행정동코드` | **8자리** — 행정안전부 행정동 코드 (예: 종로구 청운효자동 = `11110515`). ⚠️ SGIS `ADM_CD`(8자리)와 **자릿수만 같고 체계는 다름** (행안부 종로구=`11110` vs 통계청 SGIS 종로구=`11010`). |
| `집계구코드` | **13자리** = 시도(2) + 시군구(3) + 동(3) + 일련번호(5). 통계청 옛 집계구 코드 (예: `11_010_720_10001`). ⚠️ SGIS `TOT_OA_CD`(14자리)와 **자릿수도 코드 체계도 다름** — 행정 단위 prefix가 다른 데다 일련번호 자릿수까지 달라 직접 매칭 불가. |
| `총생활인구수` | 그 시간대 OA의 총 추정 인구 (실수, KT LTE 시그널링 기반) |
| `남자0세부터9세생활인구수` … `남자70세이상생활인구수` | 14개 남자 연령대 |
| `여자0세부터9세생활인구수` … `여자70세이상생활인구수` | 14개 여자 연령대 |

남·여 각 14개 연령대 = 0–9 / 10–14 / 15–19 / 20–24 / 25–29 / 30–34 / 35–39 / 40–44 / 45–49 / 50–54 / 55–59 / 60–64 / 65–69 / 70+. **남자 0–9, 여자 0–9는 10년 단위지만 그 외는 모두 5년 단위** (서울 생활인구 표준).

**해결책 — 2016 SGIS 경계가 매개**: LOCAL_PEOPLE 의 13자리 `집계구코드` 는 **2016 SGIS `TOT_REG_CD`(13) 와 완전히 같은 코드**다 (검증: 2024-12 LOCAL_PEOPLE OA 19,149개 모두 `raw/sgis_oa_2016/집계구.shp` 와 매칭). 즉,

```
LOCAL_PEOPLE.집계구코드(13) ───직접 join─→ raw/sgis_oa_2016/집계구.shp.TOT_REG_CD(13)
                                                         (2016 폴리곤, EPSG:5179)
                                                                ↓ 공간 교차 (area-weighted)
                                          raw/sgis_oa/bnd_oa_11_2025_2Q.shp (TOT_OA_CD 14)
                                                                ↓
                                            derived/oa_to_block.parquet (기존)
                                                                ↓
                                                          superblock (block_id)
```

→ 산출 예정 매핑: `derived/oa2016_to_oa2025.parquet` (`TOT_REG_CD × TOT_OA_CD × weight`, weight 합 = 1 per `TOT_REG_CD`). 이걸 `oa_to_block.parquet` 와 합성하면 LOCAL_PEOPLE 시간대별 인구를 곧장 superblock 으로 disaggregate 가능. 두 시계열(2024 SGIS 통계 + 2024 LOCAL_PEOPLE) 이 superblock 단위에서 동일 좌표계로 결합됨.

**행정동 단위 매핑** — 2016 SGIS `ADM_CD`(7) → 2025 SGIS `ADM_CD`(8) 는 **단순 `× 10` (zero-pad)** 로 변환 가능. 419/426 직접 매칭. 7개 분동·통합 케이스만 별도 mapping table.

**LOCAL_PEOPLE의 `행정동코드` 컬럼(8자리, 행안부)** 는 사실상 무시해도 됨 — `집계구코드(13)` 만으로 위 chain 으로 결합되기 때문. 행안부 ↔ SGIS 행정동 매핑이 별도로 필요한 분석이 있을 때만 명칭 매칭으로 따로 만들 것.

### `raw/seoul_living_movement/` (생활이동 — KT 기반 관측 OD)

서울 열린데이터 광장의 **KT 생활이동 데이터**. 휴대전화 시그널링으로 추정한 관측 OD. 두 가지 입도 보유:

#### 1. `admdong_od_20240327.parquet` — 단일 일자, 행정동 ×목적 OD

| 항목 | 값 |
|---|---|
| 출처 | 서울 열린데이터 광장 — 동별 목적OD (`data.seoul.go.kr/dataList/OA-21285`) |
| 기준일 | 2024-03-27 (수요일) |
| 입도 | 전국 행정동 × 행정동 (출/도착 시간대, 내·외국인, 목적별) |
| 행 수 | 6,741,497 (서울 O×D 만 필터 시 2,202,055) |
| 사이즈 | 102 MB parquet (snappy, 원본 CSV 380 MB cp949) |
| 원본 보존 | 원본 CSV(`input_data.csv`) 는 보존하지 않음. 재다운로드 가능. |

**컬럼**
| 컬럼 | 타입 | 의미 |
|---|---|---|
| `ETL_YMD` | int32 | 수집일 `YYYYMMDD` (현재 `20240327` 단일) |
| `O_ADMDONG_CD` | int32 | 출발 행정동 8자리 (행안부 체계). 서울 = `11`로 시작 |
| `D_ADMDONG_CD` | int32 | 도착 행정동 8자리 |
| `ST_TIME_CD` | int8 | 출발 시간대 `0`–`23` |
| `FNS_TIME_CD` | int8 | 도착 시간대 `0`–`23` (`FNS_TIME_CD ≥ ST_TIME_CD`, day-crossing 미반영) |
| `IN_FORN_DIV_NM` | int8 | 내·외국인 — `1` 내국인 (≈95%) · `2` 외국인 |
| `MOVE_PURPOSE` | int8 | 통행 목적 `1`–`7` ❓ 공식 명세 미동봉 — 추정 [`1` 출근, `2` 등교, `3` 쇼핑/외식, `4` 여가, `5` 업무, `6` 기타, `7` 귀가]. **분포 확인 후 학생이 직접 라벨링하는 연습 대상** |
| `MOVE_DIST` | float32 | 평균 이동 거리 (미터) |
| `MOVE_TIME` | float32 | 평균 이동 시간 (초) |
| `CNT` | float32 | 통행자 수 (실수 — KT 표본을 인구 비율로 보정한 추정값) |

**핵심 주의 — 행정동 코드 체계**

`O/D_ADMDONG_CD` 는 **행정안전부 8자리 코드** (예: 종로구 청운효자동 = `11110515`). 통계청 SGIS `ADM_CD`(8자리, 종로구 = `11010xxx`)와는 **시군구 segment 가 다른 별개 체계**. LOCAL_PEOPLE 의 `행정동코드` 와 동일 체계라 명칭 매칭이 필요한 join (admdong_od ↔ SGIS oa_master) 은:
- (a) `data/raw/admdong_boundary/admdong_2023.geojson` 의 `adm_cd2`(행안부 10자리, 앞 8 = ADMDONG_CD) 와 `adm_cd`(SGIS 10자리) 가 같은 행에 들어 있어 **이 geojson 이 행안부 ↔ SGIS 변환표** 역할
- (b) 또는 한글 명칭 (`adm_nm`) 매칭

**MOVE_PURPOSE 코드 분포 (2024-03-27)**
| 코드 | 행 수 |
|---:|---:|
| 1 | 1,247,370 |
| 2 | 251,033 |
| 3 | 2,398,140 |
| 4 | 32,118 |
| 5 | 4,835 |
| 6 | 21,677 |
| 7 | 2,786,324 |

#### 2. `gu_hourly_od_202310.parquet` — 한 달, 자치구 × 시간대 × 성연령 × 이동유형 OD

| 항목 | 값 |
|---|---|
| 출처 | 서울 열린데이터 광장 — 수도권 생활이동 (자치구 단위) |
| 기준 | 2023-10 한 달 |
| 입도 | 시군구 × 시군구 × 시간대 × 요일 × 성 × 연령 × 이동유형 |
| 행 수 | 31,284,404 |
| 사이즈 | 128 MB parquet |

**컬럼**
| 컬럼 | 타입 | 의미 |
|---|---|---|
| `ETL_YM` | int32 | `YYYYMM` (`202310`) |
| `DAYOFWEEK` | category | 한글 (`월`, `화`, …, `일`) |
| `ARR_TIME` | int8 | 도착 시간대 `0`–`23` |
| `O_GU_CD`, `D_GU_CD` | int32 | 출/도착 **시군구 5자리** (행안부, 서울 `11010`–`11250` 25개). 종로구=`11010` |
| `SEX` | category | `F` · `M` |
| `AGE_GROUP` | Int8 (nullable) | 5세 단위 (0, 10, 15, 20, 25, …, 80). NaN = 표본 보호 |
| `MOVE_TYPE` | category | 2-letter (`H`=Home, `W`=Work, `E`=Etc) 조합 9개 — `HH`, `HW`, `HE`, `WH`, `WW`, `WE`, `EH`, `EW`, `EE` |
| `AVG_MOVE_TIME_MIN` | Int16 (nullable) | 평균 이동 시간 (분) |
| `MOVE_POP` | float32 | 통행 인구 (4,025,240 행은 `*` 표본 보호 → NaN, ≈13%) |

**원본 결측 처리** — `MOVE_POP`, `AVG_MOVE_TIME_MIN`, `AGE_GROUP` 에 표본 보호용 `*` 가 들어가 있어 nullable dtype 으로 보존. 0 imputation 금지.

### `raw/admdong_boundary/admdong_2023.geojson`

| 항목 | 값 |
|---|---|
| 출처 | 행정안전부 (KOSIS, 통계청 행정구역 변경 이력 통합) — 비둘기맘 GitHub 등 보조 채널로도 유통 |
| 기준일 | 2023-01-01 |
| 입도 | 전국 행정동 |
| 행 수 | 3,516 (서울 426) |
| CRS | EPSG:4326 |
| 사이즈 | 34 MB |

**컬럼** (str 컬럼은 leading zero 보존 — int 변환 시 주의)
| 컬럼 | 길이 | 의미 |
|---|---|---|
| `adm_cd` | str(7) | SGIS 행정동 단축 코드. 종로구 청운효자동 = `1101053` |
| `adm_cd8` | str(8) | `adm_cd + '0'` (SGIS 표준 8자리) |
| `adm_cd2` | str(10) | **행안부 10자리 코드 — 앞 8자리 = `admdong_od.O/D_ADMDONG_CD` 매칭 키** (서울 426 100% 매칭) |
| `adm_nm` | str | 한글 명칭 (`시도 시군구 행정동`, cp949 원본 → utf-8) |
| `sgg`, `sggnm` | str | 시군구 코드/명 |
| `sido`, `sidonm` | str | 시도 코드/명 |
| `geometry` | geom | MultiPolygon, WGS84 |

→ 이 파일이 **행안부(생활이동) ↔ SGIS(센서스) 행정동 코드 변환표**. `admdong_od` 의 `O/D_ADMDONG_CD` (int 8자리) 와 join 하려면 `adm_cd2.str[:8].astype(int)` 로 키 생성.

### `raw/roads/segment/TL_SPRD_MANAGE_11_202601.shp`

| 항목 | 값 |
|---|---|
| 출처 | 도로명주소 전자지도 — 도로구간 |
| 기준일 | 2026-01 |
| CRS | EPSG:5179 |
| 행 수 | 66,698 LineString (도로명이 부여된 도로만) |
| 사이즈 | 75 MB |
| 인코딩 | cp949 |

**컬럼 (주요)**
| 컬럼 | 의미 |
|---|---|
| `RN` | 도로명 (한글) |
| `ENG_RN` | 영문 도로명 |
| `RN_CD` | 도로명 코드 |
| `RDS_MAN_NO` | 도로구간 관리번호 |
| `ROA_CLS_SE` | **도로 등급 (1=고속, 2=국도, 3=지방·특·광역시도, 4=시·군·구도)** ← 블록 구분의 권위 등급 |
| `ROAD_BT` | 도로 폭 |
| `ROAD_LT` | 도로 길이 |
| `SIG_CD` | 시군구 코드 |
| `RBP_CN`, `REP_CN` | 도로구간 시점/종점 명칭 |
| 외 | `ALWNC_DE`, `MVMN_DE` 허용일·이동일 등 행정 메타 |

**등급별 분포**: 1급 15 / 2급 523 / 3급 8,504 / 4급 57,656.

### `raw/roads/_reference/`

인접 프로젝트 `F:\research\생활도로_위험도_모델\` 의 알고리즘 참고 코드.

| 파일 | 내용 |
|---|---|
| `01_build_star_network.py` | 도로중심선 → degree-2 경유점 병합 후 링크-노드 그래프. degree≥3 노드를 Star로 정의. |
| `05_build_blocks.py` | grade 1-3을 장벽, grade-4 링크로 연결된 컴포넌트를 Union-Find로 묶어 블록(=Star ID 집합) 산출. TAZ 프로젝트는 폴리곤이 필요해 별도로 polygonize 방식을 채택. |

---

## 집계구(OA) 단위 데이터 종합

서울 19,097개 집계구를 키로 결합 가능한 모든 데이터셋을 한자리에서 정리. **분석 단위는 superblock**이지만 모든 외부 통계가 OA로 들어오므로 OA → superblock disaggregation(`derived/oa_to_block.parquet`)을 거쳐 P_i / A_j 입력으로 변환됨.

### 키 체계

| 키 | 자릿수 | 보유 위치 | 비고 |
|---|---:|---|---|
| `TOT_OA_CD` | 14 | `raw/sgis_oa/`, `raw/sgis_census/`, `derived/oa_to_block.parquet`, `derived/seoul_oa.fgb` | SGIS 2025-2Q. `ADM_CD(8) + seq(6)`. **권위 키.** |
| 2016 SGIS `TOT_REG_CD` | 13 | `raw/sgis_oa_2016/집계구.shp`, `raw/seoul_living_pop/.집계구코드` | **2016 SGIS 와 LOCAL_PEOPLE 이 공유하는 키.** 13(=시도2+시군구3+동3+seq5). 2025 SGIS 와는 폴리곤 50개가 재구획되어 공간 교차 매핑 필요. |
| SGIS `ADM_CD` | 8 (2025) / 7 (2016) | 각 SGIS 데이터셋 | 2025 = 2016 × 10 (zero-pad). 419/426 직접 매칭. 종로구=`11010`. |
| 행안부 행정동코드 | 8 | `raw/seoul_living_pop/.행정동코드` 만 | 행정안전부 표준. 종로구=`11110`. **SGIS와 별개 체계** — LOCAL_PEOPLE 매핑은 `집계구코드(13)` 사용이 정공이라 일반적으론 무시. |

### 데이터셋 카탈로그

| 데이터 | 위치 (raw / derived) | 키 | 단위 | 시간 해상도 | 비고 |
|---|---|---|---|---|---|
| 집계구 경계 폴리곤 (19,097) | `raw/sgis_oa/bnd_oa_11_2025_2Q.shp` | `TOT_OA_CD` | OA | 정적 (2025-06-30) | EPSG:5179. 서울 605.3 km². |
| 집계구 ↔ superblock 면적가중 매핑 | `derived/oa_to_block.parquet` | `TOT_OA_CD × block_id` | OA × superblock | — | weight 합 = 1. 도로 잔여 명시 보존. |
| 집계구 + 지배 superblock 결합 폴리곤 | `derived/seoul_oa.fgb` | `TOT_OA_CD` | OA | — | 분석·뷰어 공용 마스터. |
| **2024년 인구총괄 (총인구·남·여)** | `raw/sgis_census/11_2024년_인구총괄(총인구).csv` | `TOT_OA_CD` | OA | 2024 단년 | `to_in_001/007/008` |
| **2024년 인구밀도** | `raw/sgis_census/11_2024년_인구총괄(인구밀도).csv` | `TOT_OA_CD` | OA | 2024 | `to_in_003` (인/km²) |
| **2024년 노령화지수** | `raw/sgis_census/11_2024년_인구총괄(노령화지수).csv` | `TOT_OA_CD` | OA | 2024 | `to_in_004` |
| **2024년 성·5세별 인구** | `raw/sgis_census/11_2024년_성연령별인구.csv` | `TOT_OA_CD × in_age_*` | OA × (성 × 5세) | 2024 | 81개 코드 |
| **2024년 가구총괄 (가구수·평균가구원)** | `raw/sgis_census/11_2024년_가구총괄.csv` | `TOT_OA_CD × {to_ga_001,002}` | OA | 2024 | |
| **2024년 세대구성별 가구** | `raw/sgis_census/11_2024년_세대구성별가구.csv` | `TOT_OA_CD × ga_sd_*` | OA × 세대구성 | 2024 | 1·2·3·4세대 / 1인 / 비친족 (6코드) |
| **2024년 총주택수** | `raw/sgis_census/11_2024년_주택총괄_총주택(거처)수.csv` | `TOT_OA_CD` | OA | 2024 | `to_ho_001` |
| **2024년 주택유형별** | `raw/sgis_census/11_2024년_주택유형별주택.csv` | `TOT_OA_CD × ho_gb_*` | OA × 유형 | 2024 | 단독·아파트·연립·다세대·비거주용·기타 (6코드) |
| **2024년 연건평별 주택** | `raw/sgis_census/11_2024년_연건평별주택.csv` | `TOT_OA_CD × ho_ar_*` | OA × 면적구간 | 2024 | 9개 구간 |
| **2024년 건축년도별 주택** | `raw/sgis_census/11_2024년_건축년도별주택.csv` | `TOT_OA_CD × ho_yr_*` | OA × 건축년대 | 2024 | 20개 구간 |
| 집계구 경계 폴리곤 2016 (19,153) | `raw/sgis_oa_2016/집계구.shp` | `TOT_REG_CD` (13) | OA | 정적 (2016) | LOCAL_PEOPLE 매핑 기반. EPSG:5179 (.prj 없으니 명시 부여). |
| **서울 생활인구 (내국인)** | `raw/seoul_living_pop/LOCAL_PEOPLE_YYYYMMDD.csv` | `집계구코드`(13) ↔ 2016 SGIS `TOT_REG_CD` | OA × 시간 × 성연령 | 시간(24) × 일(현재 2024-12 31일) | 14M 행/월. 14성연령대 + 총. |

### 결합·다운스트림 파이프라인 (현재 기준)

기준 OA = **2025 SGIS `TOT_OA_CD` (14자리)**. 모든 OA-단위 통계가 이 키 한 곳으로 모이도록 산출됨.

```
raw/sgis_oa_2016/집계구.shp        raw/seoul_living_pop/LOCAL_PEOPLE_*.csv
        │                                       │
        └─────[ TOT_REG_CD 13 ]─────────────────┘
                                                ▼
                            blocks/build_oa_master.py
                                                │  (월간 시간 풀 평균
                                                │   × oa2016_to_oa2025 weight)
                                                ▼
raw/sgis_oa/bnd_oa_11_2025_2Q.shp ────┐    LOCAL_PEOPLE @ 2025 OA
raw/sgis_census/*.csv (long) ─────────┤              │
derived/oa_to_block.parquet (block) ──┴──── join ────┤
                                                     ▼
                       derived/oa_master.parquet / .fgb
                       (19,097 OA × 150 cols, geometry 포함)
                                                     │
                                                     ▼  × oa_to_block.weight
                                              superblock 단위 합산
                                                     ▼
                                         derived/seoul_blocks.fgb 의 P_i / A_j
```

- 마스터 데이터셋 (`oa_master`) 한 장으로 시각화·모델링 둘 다 충당. SGIS 인구·가구·주택 + LOCAL_PEOPLE 시간 풀이 같은 OA 키에서 정렬됨.
- superblock 합산: 마스터의 OA 컬럼을 `oa_to_block.parquet` (weight=1 per OA, 즉 OA가 superblock의 atom) join 해서 `groupby('block_id').sum()` 이면 끝.
- LOCAL_PEOPLE 디테일이 더 필요하면 (평일/주말 분리, 일별 시계열) `build_oa_master.py` 의 시간 풀 정의를 확장 후 재실행. 현재는 31일 통합 평균.
- SGIS `value=='N/A'` 통계 보호 셀과 LOCAL_PEOPLE 미수집 OA 모두 `NaN` 보존 — 0 imputation 금지.

---

## derived/

본 프로젝트의 분석 단위 데이터. 각 파일의 생성 스크립트와 컬럼 명세.

### `derived/seoul_zoning.geojson`
- 생성: `seoul_zoning_viz/export_zoning.py`
- 입력: `raw/lsmd_zoning/.../AL_D154_11_20260412.shp`
- 내용: 11개 용도지역 클래스로 dissolve된 폴리곤. 시각화·요약 통계용.
- CRS: EPSG:4326. 사이즈 약 19 MB.

### `derived/seoul_parcels.fgb`
- 생성: `seoul_zoning_viz/export_parcels.py`
- 내용: 필지 단위 폴리곤 (89.9만건). dissolve 안 함.
- CRS: EPSG:4326. 사이즈 약 322 MB.
- 컬럼: `pnu` (19자리 필지 고유번호), `zone_class` (11클래스 한글), `zone_code` (LSMD 코드), `area_m2`, `sgg` (시군구 5자리).
- 페어 산출물: `seoul_parcels_sample.geojson` (앞 1,000개 미리보기).

### `derived/zoning_stats.json`
- `export_zoning.py`가 갱신. 클래스별 면적·필지 수.

### `derived/seoul_taz.geojson`
- 생성: `seoul_taz_viz/export_seoul.py`
- 내용: 서울 25개 자치구 TAZ 폴리곤 (KTDB 2010, EPSG:5174→4326).
- 컬럼: `TAZ_ID`, `TAZ_NAME`, geometry.

### `derived/seoul_blocks.fgb`
- 생성: `blocks/build_blocks_oa.py` → `blocks/aggregate_landuse.py`로 토지이용 컬럼 보강
- 내용: **분석의 공간 단위 = 도시 superblock**. arterial polygonize cell (ROA_CLS_SE ≤ 3, ≥1000 m² 필터된 1,647 cell) 안에 max-overlap 매칭된 도시 OA 들의 합집합. **907개 도시 superblock**. 산(임야 ≥ 50% OA 326개) · 강(하천 ≥ 50% OA 140개) 은 superblock 에서 제외하고 `derived/seoul_oa_excluded.fgb` 로 별도 보존.
- CRS: EPSG:5179. 면적 중앙값 264,000 m² (~510×510m), 총 406.5 km² (도시만, 산/강 제외 198.8 km² 빠짐).
- 핵심 설계: atom 이 OA 라 분할 없음 → `oa_to_block.parquet` weight 항상 1.0. jimok_kind ∈ {도로, 철도, 하천, 교통, 공공·공원·공장}은 *비건축 인프라*로 분리. zone_class mix는 건축 가능 필지만으로 산출.
- 컬럼:
  | 컬럼 | 의미 |
  |---|---|
  | `block_id` | 0~906 정수 PK |
  | `area_m2` | 블록 총 면적 (m²). 중앙값 ≈ 264,000 |
  | `oa_count` | 블록을 구성하는 OA 개수 (median 12, max 545) |
  | `adm_n` | 블록이 걸친 행정동 수 (대부분 1, cross-adm 303개) |
  | `perimeter_m` · `shape_idx` | 둘레, 형상 지수 (1=원, 클수록 길쭉) |
  | `major_lu` | 주력 용도지역 (**건축 가능 필지** 면적 합 최대 클래스) |
  | `major_share` | major_lu가 buildable 면적에서 차지하는 비율 (0~1) |
  | `buildable_area_m2` | 건축 가능 필지 면적 합 (도로·하천·철도·교통·공공 제외) |
  | `buildable_share` | buildable_area_m2 / area_m2 |
  | `buildable_parcel_count` | 건축 가능 필지 수 |
  | `road_share` · `road_area_m2` | 도로 필지 비율·면적 |
  | `rail_share` · `rail_area_m2` | 철도 필지 |
  | `water_share` · `water_area_m2` | 하천 필지 |
  | `transit_share` · `transit_area_m2` | 교통(주차장 등) |
  | `public_share` · `public_area_m2` | 공공(학교·종교·공원·공장 등) |
- 페어: `seoul_blocks_preview.geojson` (랜덤 샘플 미리보기, EPSG:4326).
- 4단계 모델 입력: zone_class mix(11차원) + 5종 인프라 share(road/rail/water/transit/public) + buildable_share + 형상(area, perimeter, shape_idx) → 발생량 P_i, 유인량 A_j.

### `derived/link_to_block.parquet`
- 생성: `blocks/link_to_block.py`
- 내용: 도로중심선 414,791 링크 ↔ 블록 귀속 매핑. **링크 중점에서 양쪽 1.5 m 오프셋 점이 각각 어느 블록에 들어가는지로 판정**.
- 컬럼: `link_id` (centerline 행 인덱스, int64) · `block_id` (Int64, nullable) · `weight` (float32, 0.5 또는 1.0) · `side` (`inside` / `left` / `right` / `outside`).
- 분류 분포 (현 superblock 기준):
  | side | 의미 | 행 수 |
  |---|---|---:|
  | inside | 양쪽 같은 블록 → 100% 그 블록 | 332,974 |
  | left/right | 양쪽 다른 블록 → 50/50 분배 (간선 위 링크) | 26,023 × 2 |
  | edge | 한쪽만 블록, 외곽 | 3,346 |
  | outside | 둘 다 블록 외부 (한강·외곽) | 52,448 |
- 사용: 블록 단위 통행 발생량 / O-D 마진 계산 시 link 통행을 weight로 분배.

### `derived/seoul_parcels_pts.fgb`
- 생성: `blocks/export_parcel_points.py` (입력: `seoul_parcels.fgb`)
- 내용: 89.9만 필지의 centroid Point + 슬림 속성. 시각화 가속 전용.
- CRS: EPSG:4326. 사이즈 196 MB. 컬럼: `pnu`, `zone_class`, `zone_code`, `jimok`, `jimok_kind`, `area_m2`, `sgg`.
- centroid 계산은 EPSG:5179에서 수행 후 4326으로 reproject (geographic centroid 회피).
- viewer의 Points 탭이 ScatterplotLayer로 GPU 가속 렌더링.

### `derived/oa_to_block.parquet`
- 생성: `blocks/build_blocks_oa.py`
- 내용: 19,097 OA → 도시 superblock 매핑. **OA atom 이라 분할 없음 → weight 항상 1.0**.
- 컬럼: `oa_cd` (str14), `adm_cd` (str8), `kind` ({도시·산지·수계}), `block_id` (Int64; 산/강은 -1), `oa_area_m2`, `inter_area_m2`, `weight` (=1.0).
- 행 수 = 19,097 (1 row per OA). 산/강 OA 466개는 `block_id=-1` 로 표시.

### `derived/seoul_oa.fgb`
- 생성: `blocks/build_blocks_oa.py`
- 내용: 집계구 폴리곤 + 도시/산/강 라벨 + 매칭 superblock (분석·뷰어 공용 마스터).
- CRS: EPSG:5179. 컬럼: `oa_cd`, `adm_cd`, `kind`, `major_block` (Int64; 산/강은 -1), `oa_area_m2`.

### `derived/seoul_oa_excluded.fgb`
- 생성: `blocks/build_blocks_oa.py`
- 내용: 분석에서 제외된 산/강 OA 466개 (산지 326 + 수계 140). 시각화에서 회색 톤으로 표시.
- CRS: EPSG:5179. 컬럼: `oa_cd`, `adm_cd`, `kind`, `oa_area_m2`.

### `derived/oa2016_to_oa2025.parquet`
- 생성: `blocks/oa2016_to_oa2025.py`
- 입력: `raw/sgis_oa_2016/집계구.shp` + `raw/sgis_oa/bnd_oa_11_2025_2Q.shp`
- 내용: 2016 SGIS OA(13자리, LOCAL_PEOPLE 좌표계) → 2025 SGIS OA(14자리, 통계 좌표계) 면적가중 매핑.
- 컬럼: `TOT_REG_CD(str13)`, `TOT_OA_CD(str14)`, `weight(float32, 합=1 per TOT_REG_CD)`, `inter_area_m2`, `oa2016_area_m2`.
- 행 수: 40,322 (2016 OA 19,153개 × 평균 2.1 split, 50m² sliver 제거 후).
- 분포: 1:1 매칭 6,732 / 90%+ dominant 7,694 / 진짜 split (<50% dominant) 2,068.
- 면적가중 가정: 2016 OA 내부 균일분포 (population-density 가중으로 정교화하려면 SGIS 인구 미리 join 후 재계산).

### `derived/oa_master.parquet` · `derived/oa_master.fgb`
- 생성: `blocks/build_oa_master.py`
- **본 프로젝트의 OA 단위 통합 마스터.** 모든 2024 SGIS 통계 + 2024-12 LOCAL_PEOPLE 시간대 풀을 2025 SGIS `TOT_OA_CD` 한 키로 결합.
- 행: 19,097 (2025 OA 전수). 열: 150. CRS: EPSG:5179. 사이즈 약 16 MB (parquet) / 35 MB (fgb).
- **컬럼 그룹**:
  | 그룹 | 컬럼 |
  |---|---|
  | 공간·식별 | `TOT_OA_CD`, `ADM_CD`, `block_id`, `area_m2`, `geometry` |
  | 인구총괄 (alias) | `pop_total`, `pop_male`, `pop_female`, `pop_density`, `aging_idx` |
  | 가구·주택 (alias) | `hh_count`, `hh_avg_size`, `ho_total` |
  | 세대구성별 | `ga_sd_001`–`006` (1세대·2세대·3세대·4세대·1인·비친족) |
  | 주택유형 | `ho_gb_001`–`006` (단독·아파트·연립·다세대·비거주용·기타) |
  | 연건평별 | `ho_ar_001`–`009` (9 면적구간) |
  | 건축년도별 | `ho_yr_001`–`020` (20 년대구간) |
  | 성연령 (SGIS) | `in_age_001`–`in_age_081` (81 코드, 변수사전 참조) |
  | LOCAL_PEOPLE 시간 풀 | `lp_pool_resident_02_05`, `lp_pool_morning_07_10`, `lp_pool_midday_11_15`, `lp_pool_evening_18_21`, `lp_pool_late_22_01`, `lp_pool_24h` (각 풀 평균 총생활인구) |
  | LOCAL_PEOPLE 24h 성연령 | `lp_demo_total_24h`, `lp_demo_m_{0_9..70p}` (14), `lp_demo_f_{0_9..70p}` (14) |
- LOCAL_PEOPLE 처리: `LOCAL_PEOPLE_202412.zip` 31일 × 24시간 → 시간 풀별 OA 평균 → `oa2016_to_oa2025` weight 로 2025 OA disaggregate.
- 결측 처리: SGIS `value=='N/A'` 통계 보호 셀과 LOCAL_PEOPLE 미수집 OA 모두 `NaN` 보존 (0 imputation 금지).
- 검증값 (현재 산출):
  - `pop_total`: mean 489, median 482, max 6,644 (대형 아파트 단지 OA)
  - `hh_count`: mean 218, median 206
  - `lp_pool_24h`: mean 535, median 338, max 39,788 (강남·명동급 hotspot)
- 사용:
  ```python
  import geopandas as gpd
  m = gpd.read_parquet('data/derived/oa_master.parquet')   # 모델링용 (geometry 포함)
  # 시각화는 m.to_file 또는 oa_master.fgb 직접 로드
  ```

### `derived/block_landuse.parquet`
- 생성: `blocks/aggregate_landuse.py`
- 내용: 블록당 용도지역 클래스별 long-format (**buildable 필지만**, 도로·철도·하천·교통·공공 제외). 4단계 모델의 토지이용 mix 입력.
- 컬럼: `block_id`, `zone_class`, `area_m2`, `area_share`. 약 3,400행.
- `area_share`의 분모는 `buildable_area_m2`. 한 블록의 share 합 = 1.
- 비건축 인프라 share는 `seoul_blocks.fgb`의 `road_share` 등 wide 컬럼에 별도 보존.

---

## viewer/

deck.gl 웹 뷰어용 슬림 사본 (모두 EPSG:4326, 좌표 정밀도 6자리). RangeHTTPServer로 서빙해 FlatGeobuf bbox 스트리밍 사용.

| 파일 | 의미 | 사이즈 |
|---|---|---:|
| `viewer/blocks.fgb` | 블록 폴리곤 + major_lu 등 viewer 컬럼 | 2.2 MB |
| `viewer/arterial.fgb` | `boundary` 분류 도로 (간선 = 블록 경계) | 5.7 MB |
| `viewer/aux.fgb` | `edge`+`outside` 도로 (외곽 / 한강 등) | 14 MB |
| `viewer/oa.fgb` | 통계청 집계구 + major_block (oa_cd/adm_cd) | 19 MB |
| `viewer/manifest.json` | 색상 팔레트, 중심 좌표, LOD 임계값, oa_count |
| `viewer/index.html` | 뷰어 HTML 본체 (deck.gl + flatgeobuf JS) |

`inside` 분류 도로(블록 내부 골목, 약 33만 링크)는 viewer에 포함하지 않음 — 분석용 `link_to_block.parquet`에는 보존.

생성: `blocks/export_viewer_data.py` + `blocks/aggregate_landuse.py`(블록의 토지이용 컬럼).

### 실행
```
cd F:\research\TAZ
python -m RangeHTTPServer 8765
```
- 통합 뷰어 (Blocks · Zoning · Parcels · Points · OA 탭): <http://localhost:8765/data/viewer/>
  - **Blocks** — superblock 폴리곤 + 간선/aux 도로. 색은 블록 major 토지이용
  - **Zoning** — 11클래스 dissolved (한 장 19MB 즉시 로드)
  - **Parcels** — 89.9만 필지 bbox 스트리밍 (줌 13+에서만 표시)
  - **Points** — 89.9만 필지 centroid (ScatterplotLayer 가속)
  - **OA** — 통계청 집계구 19,097. 시군구 / 행정동 / major_block 색상 모드. OA 클릭 시 같은 superblock에 속한 OA들 강조
  - 좌측 패널의 zone 토글은 모든 탭이 공유

---

## 파이프라인 요약

```
raw/lsmd_zoning/AL_D154...shp
        │
        ├─ seoul_zoning_viz/export_zoning.py  → derived/seoul_zoning.geojson
        └─ seoul_zoning_viz/export_parcels.py → derived/seoul_parcels.fgb

raw/ktdb_taz/...T1110G.shp
        └─ seoul_taz_viz/export_seoul.py      → derived/seoul_taz.geojson

raw/sgis_oa/...shp + raw/roads/segment/...shp + derived/seoul_parcels.fgb
        └─ blocks/build_blocks_oa.py          → derived/seoul_blocks.fgb (907 도시 superblock)
                                              → derived/oa_to_block.parquet (kind, block_id)
                                              → derived/seoul_oa.fgb / seoul_oa_excluded.fgb
                                              → viewer/oa.fgb + manifest oa_count/oa_kinds

raw/roads/centerline/...shp + derived/seoul_blocks.fgb
        └─ blocks/link_to_block.py            → derived/link_to_block.parquet

derived/seoul_parcels.fgb + derived/seoul_blocks.fgb
        └─ blocks/aggregate_landuse.py        → derived/block_landuse.parquet
                                              → derived/seoul_blocks.fgb (재저장 + LU 컬럼)
                                              → viewer/blocks.fgb + manifest.json (LU 팔레트)

raw/roads/centerline/...shp + derived/link_to_block.parquet
        └─ blocks/export_viewer_data.py       → viewer/{arterial,aux}.fgb

```
