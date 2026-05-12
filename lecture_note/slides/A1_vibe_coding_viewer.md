# A1 (부록) — Vibe-coding 으로 인터랙티브 지도 만들기

```
A1 의 위치 — 강좌 외 부록
─────────────────────────────────────────────────────────────
Lec1 ── Lec2 ── Lec3 ── Lec4   (메인: 통행 수요)
            │     │
            └─────┴──→ A1  (산출물 시각화 도구 만드는 법)

목표: 코드를 외우지 말고, AI 에게 "무엇을 어떻게 요청할지" 배우기.
도구: Claude Code / Codex / Cursor 같은 AI 코딩 에이전트
참조: data/viewer/  ← 본 강의 동봉 reference. 우리가 만들 목표.
```

본 부록이 가르치는 것:
- "지도 만들어줘" 한 줄로는 왜 실패하는가
- 4단계로 쪼개서 AI 에게 던지는 프롬프트 패턴 (학생 복붙 가능)
- AI 가 "동작합니다" 한 후 학생이 직접 검증하는 법
- 막혔을 때 다음 한마디 — "안 돼"로 그치지 않는 법

## 0. 먼저 reference 뷰어를 손가락으로 만져보기

```bash
cd F:\research\TAZ
python -m RangeHTTPServer 8765
# 브라우저: http://localhost:8765/data/viewer/
```

줌, 팬, 호버, 탭 전환 — 이게 우리가 AI 와 함께 만들 목표. 어떤 동작이 매끄럽고 어떤 게 어색한지 손으로 느낀 후에 다음 슬라이드로.

## 1. 왜 "지도 만들어줘" 한 줄은 실패하나

```
학생: "서울 인터랙티브 지도 만들어줘. 빠르게."
  ↓
AI: 코드 작성 완료. 89.9만 필지 GeoJsonLayer 로 그렸음
  ↓
학생: (띄움) → 브라우저 멈춤 → 30초 후 탭 강제 종료
  ↓
학생: "동작 안 해"
  ↓
AI: 다시 시작 (원인 모름, 같은 실수 반복)
```

문제는 AI 가 아니라 **명세 없는 요청**. 본 강의 데이터는 무거워서 "잘 그려줘" 만으론 안 됨. AI 는 학생 화면을 못 보고, 데이터가 얼마나 큰지도 모르고, 본 강의 디렉터리 구조도 모름.

## 2. 좋은 프롬프팅 — 작게 시작 + 한 번에 하나만 + 매 단계 검증

```
─────────────────────────────────────────────────
Step 1: Baseline   가장 작은 데이터 + 가장 단순한 레이어 하나
Step 2: Expand     두 번째 레이어 추가
Step 3: Optimize   무거운 데이터 추가 (한 번에 한 트릭만)
Step 4: Interact   패널, 토글, 호버, 통계
─────────────────────────────────────────────────
```

규칙 3개:
- 매 단계 끝나면 **브라우저에서 직접 띄워본다** — AI 의 "동작합니다" 만 믿지 않기
- 다음 단계 가기 전 `git commit` (혹은 폴더 복사) — 망가지면 되돌리기 위해
- 막히면 step 단위로 되돌리고, 그 step 만 다시 요청

## 3. AI 에게 매번 던질 컨텍스트 블록

매 단계 첫 프롬프트에 이 블록을 그대로 첨부하세요 (본인 경로로 수정):

```
프로젝트 컨텍스트:
- 작업 디렉터리: F:\research\TAZ
- 데이터 명세는 data/README.md 참조
- 본 강의 산출물 위치:
    data/derived/lecture_outputs/pi_aj_v1.parquet   (Lecture 3)
    data/derived/lecture_outputs/od_matrix_v1.parquet (Lecture 4)
- 행정동 경계: data/raw/admdong_boundary/admdong_2023.geojson
- 참조 뷰어 (스타일·구조 참고): data/viewer/index.html
- 실행: python -m RangeHTTPServer 8765, http://localhost:8765/<path>/

제약:
- 백엔드 만들지 마. 정적 HTML + Python 변환 스크립트 + fgb 파일만.
- 외부 라이브러리는 CDN 으로 (npm/build 도구 X).
- 모든 산출물은 my_viewer/ 폴더 안에.
- 코드 짜기 전에 어떤 라이브러리/접근법 쓸지 먼저 알려주고 확인 받기.
```

마지막 한 줄이 핵심 — **AI 가 멋대로 달려서 헛 코드 양산하지 못하게.**

## 4. 학생이 알아야 할 vocabulary (10개)

코드 작성 능력보다 이 단어들을 알고 AI 에게 던질 수 있는 게 중요:

| 단어 | 한 줄 설명 | 언제 AI 에게 요청하나 |
|---|---|---|
| **FlatGeobuf (fgb)** | bbox 부분 로드 되는 바이너리 지오 포맷 | 1만+ feature 시각화 |
| **bbox streaming** | 화면에 보이는 부분만 다운로드 | 줌인 시 빠른 응답 |
| **deck.gl** | GPU 가속 지도 레이어 라이브러리 | 다중 레이어 인터랙티브 지도 |
| **GeoJsonLayer** | 폴리곤·선·점 렌더 (CPU 삼각분할) | 5천 feature 이하 폴리곤 |
| **ScatterplotLayer** | 점 전용 GPU 레이어 | 폴리곤 → centroid 점 단순화 후 |
| **LOD (minZoom/maxZoom)** | 줌 레벨별 다른 데이터 | 줌 12 에선 필지 안 보여도 됨 |
| **centroid 단순화** | 폴리곤 → 점 변환 | 90만 필지 같은 거대 폴리곤 |
| **set_precision(geom, 1e-6)** | 좌표 정밀도 줄임 (≈ 10cm) | fgb 파일 크기 30% ↓ |
| **MapLibre + CARTO** | 무료 베이스맵 (Mapbox 토큰 X) | 매번 |
| **RangeHTTPServer** | HTTP Range 지원하는 Python 정적 서버 | bbox streaming 필요 시 |

→ "ScatterplotLayer 로 바꿔줘" 한 마디로 충분. 코드는 AI 가 씀.

## 5. Step 1 — Baseline: admdong + P_obs 색칠

학생이 AI 에게:

```
[위 컨텍스트 블록]

가장 단순한 뷰어를 만들어줘.

산출:
1. my_viewer/prepare.py
   - pi_aj_v1.parquet 와 admdong_2023.geojson 을 join
   - 서울만 (sidonm 컬럼에 '서울' 포함된 행)
   - 결과를 my_viewer/adm.fgb 로 저장 (FlatGeobuf 포맷)
   - 좌표는 EPSG:4326, set_precision(geom, 1e-6)

2. my_viewer/index.html
   - deck.gl + maplibre-gl + flatgeobuf-geojson 을 CDN 으로
   - CARTO dark 베이스맵 (토큰 불필요)
   - adm.fgb 를 GeoJsonLayer 로
   - P_obs 값에 따라 색칠 (viridis 컬러맵, log scale)
   - 호버 시 admdong 이름 + P_obs 값 툴팁

3. my_viewer/README.md — 실행 방법 한 단락

코드 짜기 전에 어떤 CDN 버전을 쓸지 알려주고 확인 받아.
```

학생이 한 후 직접 확인:
- `python my_viewer/prepare.py` → fgb 파일 생성됐나? (파일 크기 ≈ 1MB 미만)
- 브라우저로 띄우기 → 폴리곤이 보이나?
- 강남·종로 쪽이 더 진한가? (face validity — P_obs 큰 곳)
- 호버 동작?

→ 안 되면 § 9 의 "막혔을 때 한마디" 표 참조.

## 6. Step 2 — Expand: OD flow lines 추가

```
[컨텍스트]

기존 뷰어에 두 번째 레이어를 추가해줘.

1. prepare.py 에 함수 추가:
   - od_matrix_v1.parquet 에서 T_obs 상위 200 OD 쌍만
   - 각 O 와 D 의 admdong centroid 좌표 join
   - LineString geometry 로 my_viewer/od.fgb 저장
   - 속성: T_obs, distance_km

2. index.html 에 LineLayer 추가:
   - 선 굵기는 log(T_obs) 비례
   - 색은 흰색 → 빨강 그라데이션
   - 기존 admdong choropleth 는 그대로 유지

3. 좌상단에 패널 한 개 — "OD flows" 토글 (켜기/끄기)

검증할 것:
- top OD 가 강남·종로·여의도 쪽에 몰리나? (face validity)
- 토글로 깔끔히 사라지나?
```

→ AI 가 흑백으로 만들거나 굵기가 안 변하면, 학생이 그대로 말함: **"굵기가 안 변해. log(T_obs) 가 LineLayer 의 getWidth 에 제대로 들어갔는지 확인."**

## 7. Step 3 — Optimize: 무거운 데이터 + perf 트릭

여기서 핵심 패턴 — **"코드 짜지 마, 먼저 의견 줘"**:

```
[컨텍스트]

이제 OA 19,097개 폴리곤 (data/derived/seoul_oa.fgb, ≈ 19MB) 을 추가하려고 해.

코드 작성 전에 분석부터 해줘:

1. 이 사이즈는 bbox streaming 이 필요한가, 한 번 fetch 면 충분한가?
2. 폴리곤 그대로 GeoJsonLayer 인가, centroid 점으로 단순화하나?
3. 줌 11 (서울 전체) 에서도 보여야 하나, LOD 로 줌 12+ 부터만 활성화하나?
4. OA 마다 어떤 컬럼을 색칠 변수로 노출할까? (oa_master.parquet 컬럼 중)

각 선택지의 트레이드오프를 설명한 다음, 본 강의 reference (data/viewer/oa.fgb 의
처리 방식) 와 비교해서 추천해줘. 동의하면 그때 구현 요청할게.
```

AI 가 트레이드오프 표를 주면 학생이 골라서:

```
좋아. bbox streaming + GeoJsonLayer + 줌 11+ 부터, 색칠 변수는
pop_total / lp_pool_24h / lp_pool_morning 세 가지 드롭다운으로 가자.
구현해줘.
```

이 두 단계 패턴이 본 슬라이드의 핵심 — **AI 가 헛 코드 양산 못하게 한 번 brake**.

## 8. Step 4 — Interact: 패널, 호버, 통계

```
[컨텍스트]

data/viewer/index.html 의 좌상단 패널 스타일을 참고해서 본 뷰어 패널을 다듬어줘.

요구:
- 세 탭: "Admdong" / "Flows" / "OA"
- 각 탭마다: 레이어 토글, 색상 범례, mini 통계 (mean / median / max / NaN 수)
- 호버 시 fixed 위치 툴팁 (마우스 따라다니지 말고 우상단 고정)
- ESC 키로 패널 접기, ` 키로 다시 펴기

스타일:
- 반투명 검정 배경 + 살짝 blur
- 데이터 텍스트는 monospace
- 시스템 기본 폰트

기존 레이어 동작은 그대로.
```

## 9. AI 가 "동작합니다" 한 후 학생이 확인 — F12 가 학생의 눈

| 항목 | 어디서 | 무엇을 보나 | 목표 |
|---|---|---|---|
| 첫 frame | 그냥 띄움 | 5초 이내에 뭐가 보이나 | 5초+ |
| 콘솔 에러 | F12 → Console | 빨간 에러 없나 | 0개 |
| 데이터 일치 | 패널 통계 vs M3/M4 노트북 | 같은 mean / median? | 일치 |
| FPS | F12 → Performance 녹화 → 줌·팬 | FPS 메터 30+? | 30+ |
| Network | F12 → Network → 줌인 | 새 fgb 청크 요청 가나? | 가야 함 (streaming) |
| Face validity | 시각으로 | 강남 hotspot? 외곽 producer? | 직관과 맞음 |

→ **"AI 가 동작한다고 했다" ≠ "동작한다"**. AI 는 그럴듯한 코드를 짤 뿐, 학생 화면을 못 봄. 직접 띄워서 확인.

## 10. 막혔을 때 다음 한마디

"안 돼" 만으로는 AI 가 진단 불가. **무엇이 / 어디서 / 어떻게** 안 되는지 한 줄 더:

| 증상 | 학생이 던질 한마디 |
|---|---|
| 폴리곤 안 보임 | "콘솔 에러는 [붙여넣기]. `ogrinfo my_viewer/adm.fgb` 결과는 X feat" |
| 보이지만 색이 단색 | "P_obs 분포가 [min~max], 색 매핑 도메인이 그 범위 맞나" |
| 회색 화면 | "베이스맵 fetch 가 안 되는 듯. Network 탭에 cartocdn 401/403 보임" |
| 너무 느림 | "FPS 12, 줌 13 에서. Performance 녹화 보니 GeoJsonLayer 가 메인 스레드 점유" |
| 줌인 시 데이터 안 늘어남 | "Network 탭에서 fgb 청크 새로 안 받음. bbox streaming 코드 확인" |
| 호버 안 됨 | "pickable: true 빠진 거 아닌가" |
| fgb 파일 너무 큼 | "출력 fgb 가 30MB. set_precision / 컬럼 drop / dtype 변경 어느 거 빠졌나" |

→ 화면 캡처를 같이 보내면 더 빠름 (Claude Code 는 이미지 첨부 가능).

## 11. 과제

본인의 mini viewer 만들기:

**최소 요구**:
- Lecture 3 의 `pi_aj_v1.parquet` 시각화 — admdong P_obs choropleth
- Lecture 4 의 `od_matrix_v1.parquet` 시각화 — top OD flow lines
- 위 5~8 의 단계별 프롬프트 그대로 복붙해도 OK, 변형해도 OK
- README 에 본인이 변경한 부분 한 단락

**도전 (선택)**:
- OA 단위 레이어 추가 (`oa_master.parquet` 컬럼 한 개 색칠)
- 필지 점도 추가 (`seoul_parcels_pts.fgb` → ScatterplotLayer)
- LOD 동작 (줌에 따라 레이어 자동 토글)
- 시간대별 OD 토글 (`MOVE_PURPOSE` 별)

**제출**:
- GitHub repo (private OK) 링크
- README 에 스크린샷 3장 (줌 11 / 13 / 15)
- `prompts.md` — AI 와의 대화 기록 (그대로 복붙)

**평가**:
- 검증 체크리스트 (§ 9) 6개 중 5개 통과
- 데이터 정확성 — 패널 통계가 노트북 출력과 일치
- AI 와의 대화가 **"작게 시작 + 단계별 검증"** 패턴 따랐나
- 프롬프트가 명세적인가 (모호한 "잘 만들어줘" 류 없나)

**비교 reference**: `data/viewer/`. 그보다 단순해도 OK. 핵심은 **AI 와 협업하는 방식** 자체.

## 12. 정리

- "지도 만들어줘" 한 줄 → 실패. **명세 + 단계 분할 + 검증** 이 필요.
- 4단계 패턴: **Baseline → Expand → Optimize → Interact**, 매 단계 학생이 직접 검증.
- 코드 외우지 말 것. **vocabulary 10개** (§ 4) 만 알면 AI 에게 던질 수 있음.
- AI 가 "동작합니다" 라고 하면 학생이 띄워서 직접. **F12 가 학생의 눈.**
- 막히면 **무엇이 / 어디서 / 어떻게** — "안 돼" 한 줄로는 AI 진단 불가.
- AI 가 멋대로 달리지 못하게 **"코드 짜기 전 의견 먼저"** 한 줄을 컨텍스트에.

→ Lecture 4 메인 트랙으로 회귀. A1 은 시간 여유 / 학생 흥미가 있을 때.
