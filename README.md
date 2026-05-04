# TAZ — 서울 토지이용 · 도로 · 교통존 워크스페이스

서울특별시 토지이용·용도지역·도로·교통존 데이터를 정제하고, **superblock 단위**로 토지이용을 집계해 통행 발생 모델 학습에 사용하기 위한 작업 공간.

## 빠른 시작

```bash
# 1) 코드 클론
git clone https://github.com/jihoyeo/seoul-travel-demand-2024.git
cd seoul-travel-demand-2024

# 2) raw 데이터 받기 (Hugging Face, 1.4 GB 7z)
pip install huggingface_hub
huggingface-cli download CAMUS-LAB/seoul-travel-demand-2024 \
    seoul_taz_raw.7z --repo-type dataset --local-dir .
7z x seoul_taz_raw.7z      # → data/raw/ 생성

# 3) 파이프라인 (소요 ≈ 8분, 메모리 8GB+ 권장)
python blocks/oa2016_to_oa2025.py
python blocks/build_oa_master.py        # ~6분 (LP 31일 스트리밍)
python blocks/build_blocks_oa.py        # ~60s (parcels overlay)
python blocks/aggregate_landuse.py      # ~30s
```

데이터 분리:
- **코드 (본 repo)** : `blocks/`, `seoul_zoning_viz/`, `seoul_taz_viz/`, `data/README.md`, `data/viewer/index.html`
- **raw 데이터** : Hugging Face `CAMUS-LAB/seoul-travel-demand-2024` (1.4 GB 7z)
- **derived 산출물** : 위 스크립트로 재생성 (`.gitignore` 처리)

## Layout

```
F:\research\TAZ\
├─ data/                                # 모든 데이터 (자세한 명세는 data/README.md)
│  ├─ raw/         외부 원본 (lsmd_zoning, ktdb_taz, roads/{centerline,segment,_reference})
│  ├─ derived/     분석 산출물 (필지·블록·매핑·집계)
│  ├─ viewer/      deck.gl 뷰어용 슬림 사본 + index.html
│  └─ README.md    데이터 명세서
├─ seoul_zoning_viz/   용도지역 export + 두 가지 웹 뷰어
├─ seoul_taz_viz/      KTDB 자치구 TAZ export + 뷰어
├─ blocks/             블록 폴리곤화 + 링크 매핑 + 토지이용 집계 + 뷰어 데이터
├─ README.md           ← 본 문서
└─ CLAUDE.md           Claude Code 세션 운영 가이드
```

코드와 데이터 분리: 코드 폴더(`seoul_zoning_viz/`, `seoul_taz_viz/`, `blocks/`)에는 `.py`만, 모든 raw·산출 데이터는 `data/`.

## 분석 단위

**Superblock = 도로(`ROA_CLS_SE ≤ 3`)로 둘러싸인 cell 안의 도시 OA 들의 합집합.** 907개 폴리곤. 중앙값 264,000 m² (~510×510m), `data/derived/seoul_blocks.fgb`.

생성 절차 (`blocks/build_blocks_oa.py`):
1. arterial polygonize → 3,077 cell → ≥1000 m² 필터 → 1,647 cell
2. 통계청 집계구(OA, 19,097) × parcels overlay → OA별 jimok_kind 비율 → 라벨링
   - 임야 ≥ 50% → 산지 (326개) · 하천 ≥ 50% → 수계 (140개) · 그 외 → 도시 (18,631개)
3. **도시 OA 만** cell 에 max-overlap 매칭 (실패 시 sjoin_nearest fallback) → 같은 cell 의 OA 들 dissolve → superblock
4. 산·강 OA 는 `block_id = -1` 로 표시, 별도 `data/derived/seoul_oa_excluded.fgb` 로 보존

특징:
- atom 이 OA 라 분할 없음 → `oa_to_block.parquet` 의 weight 항상 1.0
- superblock 경계 = OA 경계의 union (간선 + 통계청이 채택한 행정동·하천·단지 경계)
- 산/강이 빠져 있어 분석 입력 (P_i / A_j) 에 통행 발생 없는 면적이 섞이지 않음

도로 링크는 superblock 내부(`inside`) 또는 경계(`boundary` = 양옆 두 블록에 50/50 분배)로 귀속.

## 파이프라인

```
seoul_zoning_viz/export_zoning.py    LSMD raw → derived/seoul_zoning.geojson + zoning_stats.json
seoul_zoning_viz/export_parcels.py   LSMD raw → derived/seoul_parcels.fgb + sample
seoul_taz_viz/export_seoul.py        KTDB raw → derived/seoul_taz.geojson
blocks/build_blocks_oa.py            sgis_oa + segment + parcels
                                       → derived/seoul_blocks.fgb (907 도시 superblock, geom only)
                                       → derived/oa_to_block.parquet (kind, block_id, weight=1.0)
                                       → derived/seoul_oa.fgb / seoul_oa_excluded.fgb
                                       → viewer/oa.fgb + manifest oa_count/oa_kinds
blocks/link_to_block.py              roads/centerline + blocks → derived/link_to_block.parquet
blocks/aggregate_landuse.py          parcels + blocks → derived/block_landuse.parquet
                                                        + blocks.fgb 재저장 (LU 컬럼)
                                                        + viewer/blocks.fgb + manifest patch
blocks/export_viewer_data.py         centerline + mapping → viewer/{arterial,aux,blocks}.fgb
                                                            + manifest update
blocks/build_oa_master.py            sgis_oa + sgis_census + LOCAL_PEOPLE + oa2016_to_oa2025
                                       → derived/oa_master.parquet (19,097 × 150 cols)
```

각 코드는 같은 폴더에서 `python <스크립트>` 형태로 실행. 경로는 `data/` 아래로 상대 참조.

## 시각화

FGB bbox 스트리밍은 HTTP Range가 필요하므로 `python -m http.server`는 안 됨. `RangeHTTPServer` 사용.

```bash
pip install rangehttpserver
cd F:\research\TAZ
python -m RangeHTTPServer 8765
```

통합 뷰어 한 화면에서 탭으로 전환:

| URL | 내용 |
|---|---|
| `http://localhost:8765/data/viewer/` | **Blocks** · **Zoning** · **Parcels** · **Points** · **OA** 5탭. 좌측 zone 토글은 모든 탭 공유. OA 탭에서 OA 클릭 시 같은 superblock에 속한 OA들이 강조됨 |

## 용도지역 11클래스

LSMD 코드(A7) 매핑은 `seoul_zoning_viz/export_zoning.py`의 `ZONE_CLASS_MAP`이 단일 진실. 변경 시 `export_parcels.py`·`blocks/aggregate_landuse.py`(LU_COLOR 팔레트)도 동기화할 것.

| 클래스 | LSMD 코드 | 면적 | 필지 |
|---|---|---:|---:|
| 전용주거 | UQA111, UQA112 | 7.76 km² | 10,144 |
| 일반주거_저밀(1종) | UQA121 | 100.01 km² | 92,284 |
| 일반주거_중밀(2종) | UQA122 | 146.74 km² | 471,004 |
| 일반주거_고밀(3종) | UQA123 | 89.31 km² | 141,597 |
| 준주거 | UQA130 | 13.17 km² | 41,528 |
| 중심·일반상업 | UQA210, UQA220 | 21.31 km² | 55,282 |
| 근린·유통상업 | UQA230, UQA240 | 2.29 km² | 3,708 |
| 전용공업 | UQA310 | 0 | 0 |
| 일반·준공업 | UQA320, UQA330 | 19.07 km² | 24,712 |
| 보전·자연녹지 | UQA410, UQA430 | 203.70 km² | 57,943 |
| 생산녹지 | UQA420 | 2.22 km² | 513 |

서울 합계 ≈ 605 km². 수치 출처: `data/derived/zoning_stats.json` (export_zoning.py가 매 실행마다 갱신).

## Roadmap (분석 단계)

블록 폴리곤·링크 매핑·토지이용 집계·집계구 매핑은 완료. 다음:

- [x] **SGIS 통계 join** — 2024 인구·가구·주택 10종 통계 + 2024-12 LOCAL_PEOPLE 생활인구를 2025 `TOT_OA_CD` 한 키로 통합. 2016 SGIS 경계(`TOT_REG_CD` 13자리)를 매개로 LOCAL_PEOPLE 을 area-weighted disaggregate. 결과: `data/derived/oa_master.parquet` (19,097 OA × 150 cols).
- [ ] **건축물대장 결합** — 연면적·층수·용도 합산 (PNU join). superblock 단위 floor area density 산출.
- [ ] **블록 그래프 정의** — 블록 인접·간선 공유 기반 edge index. PyG `HeteroData` (블록 + 링크).
- [ ] **Trip Generation 모델** — 블록 토지이용·인구·연면적 → 발생/유인량 (P_i, A_j). 시간대별 조건 변수 포함.
- [ ] **Trip Distribution 모델** — 학습형 gravity로 블록 i↔j OD. row-marginal 보존 빌드인.

## Known issues

- **shapely 2.0.4 ↔ numpy 2.4.x 비호환**: `shapely.union_all`이 `ufunc 'create_collection' not supported` 에러. `pip install "shapely>=2.0.6"` (현재 2.1.2).
- **콘솔 한글 mojibake**: Windows cp949 콘솔에서 `print(한글)` 출력이 깨져 보이지만 파일·데이터는 정상.
- **shapefile 인코딩**: 한글 속성은 `encoding='cp949'`. `utf-8`/`euc-kr`는 raw bytes로 깨짐.
- **KTDB raw zip 부재**: `data/raw/ktdb_taz/` 폴더는 비어 있음. 산출물 `data/derived/seoul_taz.geojson`은 보존돼 있어 분석엔 영향 없음. 재생성 필요 시 KTDB에서 재다운로드.
