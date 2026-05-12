"""A1_vibe_coding_viewer.pptx — Appendix deck (16:9, Uber design + Pretendard).

Topic: how to vibe-code a data viewer with an AI coding agent
       (Claude Code / Codex / Cursor). The content is process-heavy
       rather than code-heavy — prompts, vocabulary, checklists.
"""
from __future__ import annotations

import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

from slide_theme_uber import (
    C, SLIDE_W, SLIDE_H, MARGIN_X, MARGIN_Y, CONTENT_W, CONTENT_H, TYPE,
    add_text, add_rounded, add_card_content, add_card_soft, add_card_dark,
    add_pill, add_chip, add_code_cell, add_hairline, add_vline, add_arrow,
    add_page_chrome, new_blank_slide, new_dark_slide, setup_169, radius_for,
)


DECK_LABEL = "TAZ · A1 부록 · Vibe-coding 뷰어"


# ============================================================================
# slide 01 — title
# ============================================================================

def slide_title(prs, idx, total):
    s = new_blank_slide(prs)

    add_text(s, MARGIN_X, Inches(1.2), Inches(7), Inches(0.4),
             [("APPENDIX 01  ·  AI 협업 뷰어",
               {"style": "eyebrow", "color": C.ink})])

    add_text(s, MARGIN_X, Inches(1.7), Inches(7.4), Inches(2.7),
             [("Vibe-coding 으로\n인터랙티브 지도 만들기",
               {"style": "display_xxl", "color": C.ink,
                "line_spacing": 1.08})])

    add_text(s, MARGIN_X, Inches(4.3), Inches(7.4), Inches(1.1),
             [("코드를 외우지 말고, AI 에게 ‘무엇을 어떻게 요청할지’ 배우기.\n"
               "Claude Code / Codex / Cursor — 도구는 바뀌어도 패턴은 같다.",
               {"style": "lead", "color": C.body})])

    add_pill(s, MARGIN_X,            Inches(5.6), Inches(1.85), Inches(0.5),
             "Reference viewer",  variant="primary")
    add_pill(s, MARGIN_X + Inches(2.00), Inches(5.6), Inches(1.85), Inches(0.5),
             "Open prompts",       variant="secondary")

    # right column: overview card
    card_x = Inches(8.5)
    card_y = Inches(1.2)
    card_w = SLIDE_W - card_x - MARGIN_X
    card_h = Inches(5.0)
    add_card_content(s, card_x, card_y, card_w, card_h, radius_in=0.21)

    pad = Inches(0.42)
    add_text(s, card_x + pad, card_y + pad, card_w - pad * 2, Inches(0.32),
             [("OVERVIEW", {"style": "eyebrow", "color": C.body})])

    row_y = card_y + pad + Inches(0.55)
    rows = [
        ("왜",        "‘지도 만들어줘’ 한 줄로는 실패.\n명세 + 분할 + 검증 필요"),
        ("도구",       "AI 코딩 에이전트\n(Claude Code / Codex / Cursor)"),
        ("참조",       "data/viewer/index.html\n본 강의 동봉 reference"),
        ("이번 시간",   "4 step pattern + vocabulary\n학생이 복붙할 프롬프트 set"),
    ]
    rh = Inches(0.95)
    for i, (k, v) in enumerate(rows):
        ry = row_y + rh * i
        if i > 0:
            add_hairline(s, card_x + pad, ry - Inches(0.05),
                         card_w - pad * 2, color=C.hairline_soft)
        add_text(s, card_x + pad, ry, Inches(1.3), Inches(0.4),
                 [(k, {"style": "body_md_b", "color": C.ink})])
        add_text(s, card_x + pad + Inches(1.30), ry,
                 card_w - pad * 2 - Inches(1.30), Inches(0.8),
                 [(v, {"style": "body_sm", "color": C.body})])

    # footer
    add_hairline(s, MARGIN_X, SLIDE_H - Inches(0.85),
                 SLIDE_W - MARGIN_X * 2, color=C.hairline_soft)
    add_text(s, MARGIN_X, SLIDE_H - Inches(0.72), Inches(8), Inches(0.3),
             [("TAZ STUDIO  ·  강좌 외 부록",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, SLIDE_W - MARGIN_X - Inches(3), SLIDE_H - Inches(0.72),
             Inches(3), Inches(0.3),
             [(f"01 / {total:02d}", {"style": "eyebrow", "color": C.body,
                                     "letter_spacing_pt": 1.6})],
             align=PP_ALIGN.RIGHT)


# ============================================================================
# slide 02 — 먼저 reference 뷰어를 만져보기
# ============================================================================

def slide_touch_reference(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="STEP 0  ·  TOUCH REFERENCE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("먼저 손가락으로 만져본다",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("줌·팬·호버·탭 전환 — 어떤 동작이 매끄럽고 어색한지 ‘느낀’ 후 다음 슬라이드",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "cd F:\\research\\TAZ",
        "python -m RangeHTTPServer 8765",
        "# 브라우저: http://localhost:8765/data/viewer/",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.6), Inches(1.55),
                  code_lines, label="shell · serve reference",
                  font_pt=12, line_spacing=1.22)

    # checklist card
    add_card_content(s, MARGIN_X, Inches(4.35), Inches(8.6), Inches(2.85),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, MARGIN_X + pad, Inches(4.35) + pad,
             Inches(8.0), Inches(0.32),
             [("FEEL FIRST  ·  CHECKLIST",
               {"style": "eyebrow", "color": C.body})])

    checks = [
        "줌·팬 — 화면이 끊기지 않게 따라오나",
        "호버 — 폴리곤 위 마우스 → 툴팁 즉시 뜨나",
        "패널 — 탭 전환 시 레이어가 자연스럽게 바뀌나",
        "정합성 — 강남·종로 hotspot 이 ‘직관’ 과 맞는가",
    ]
    cy = Inches(4.35) + pad + Inches(0.40)
    for c in checks:
        add_text(s, MARGIN_X + pad, cy, Inches(8.0), Inches(0.32),
                 [("·  " + c, {"style": "body_md", "color": C.body})])
        cy += Inches(0.42)

    # right: WHY card (emphasis)
    nx = MARGIN_X + Inches(9.0)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_dark(s, nx, Inches(2.55), nw, Inches(4.65), radius_in=0.21)
    pad2 = Inches(0.30)
    add_text(s, nx + pad2, Inches(2.55) + pad2,
             nw - pad2 * 2, Inches(0.32),
             [("WHY  ·  TOUCH FIRST",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, nx + pad2, Inches(2.55) + pad2 + Inches(0.36),
             nw - pad2 * 2, Inches(0.7),
             [("Target 을\n알지 못하면",
               {"style": "display_sm", "color": C.on_dark,
                "line_spacing": 1.25})])
    add_text(s, nx + pad2, Inches(2.55) + pad2 + Inches(1.45),
             nw - pad2 * 2, Inches(2.5),
             [("AI 에게 줄 ‘좋다’ 의 기준이\n없으면 평가도 못 한다.\n\n"
               "참조 뷰어 = 학생의 정답지.\n"
               "동일 동작을 만들 필요는\n없고, 무엇이 ‘인터랙티브’\n인지 손가락으로 안다.",
               {"style": "body_sm", "color": C.mute,
                "line_spacing": 1.35})])


# ============================================================================
# slide 03 — 왜 한 줄 요청은 실패하나
# ============================================================================

def slide_why_one_liner_fails(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="ANTI-PATTERN  ·  ONE LINER",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("‘지도 만들어줘’ 한 줄은 왜 실패하나",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("AI 가 아니라 명세 없는 요청이 문제 — AI 는 화면도 데이터 크기도 못 봄",
               {"style": "lead", "color": C.body})])

    # 4-step failure flow
    fx = MARGIN_X
    fy = Inches(2.7)
    fw = Inches(7.6)
    fh = Inches(0.95)
    fgap = Inches(0.12)
    steps = [
        ("학생",  "‘서울 인터랙티브 지도 만들어줘. 빠르게.’"),
        ("AI",    "코드 작성 완료. 89.9만 필지 GeoJsonLayer 로 그렸음."),
        ("학생",  "(띄움) → 브라우저 멈춤 → 30초 후 탭 강제 종료"),
        ("학생",  "‘동작 안 해’"),
        ("AI",    "다시 시작 — 원인 모름, 같은 실수 반복"),
    ]
    for i, (who, msg) in enumerate(steps):
        y = fy + (fh + fgap) * i
        is_ai = (who == "AI")
        if is_ai:
            add_rounded(s, fx, y, fw, fh, fill=C.canvas_soft, line=None,
                        radius_ratio=radius_for(fw, fh, 0.21))
            wc, mc = C.body, C.ink
        else:
            add_rounded(s, fx, y, fw, fh, fill=C.canvas, line=C.hairline,
                        line_w_pt=0.75,
                        radius_ratio=radius_for(fw, fh, 0.21))
            wc, mc = C.body, C.ink
        pad = Inches(0.26)
        add_text(s, fx + pad, y + pad, Inches(0.9), Inches(0.35),
                 [(who, {"style": "eyebrow", "color": wc,
                         "letter_spacing_pt": 1.0})])
        add_text(s, fx + Inches(1.2), y + pad - Inches(0.04),
                 fw - Inches(1.2) - pad, fh - pad * 2,
                 [(msg, {"style": "body_md", "color": mc})])

    # right: 3 root-cause cards
    rx = fx + fw + Inches(0.30)
    rw = SLIDE_W - MARGIN_X - rx
    add_card_dark(s, rx, fy, rw, (fh + fgap) * 5 - fgap, radius_in=0.21)
    pad2 = Inches(0.28)
    add_text(s, rx + pad2, fy + pad2, rw - pad2 * 2, Inches(0.32),
             [("ROOT CAUSES", {"style": "eyebrow", "color": C.mute})])

    causes = [
        ("AI 는 화면을 못 본다",
         "본인이 띄워보지 않으면\n‘잘 그렸음’ 만 받음"),
        ("데이터 크기를 모른다",
         "89만 필지 = 검정 화면\nAI 는 그 사실을 통보받지\n못함"),
        ("디렉터리 구조를 모른다",
         "raw / derived / lecture_outputs\n경로를 매번 넣어줘야 함"),
    ]
    cy = fy + pad2 + Inches(0.40)
    for k, v in causes:
        add_text(s, rx + pad2, cy, rw - pad2 * 2, Inches(0.32),
                 [(k, {"style": "body_md_b", "color": C.on_dark})])
        add_text(s, rx + pad2, cy + Inches(0.30),
                 rw - pad2 * 2, Inches(0.85),
                 [(v, {"style": "body_sm", "color": C.mute})])
        cy += Inches(1.35)


# ============================================================================
# slide 04 — 4 step pattern (Baseline → Expand → Optimize → Interact)
# ============================================================================

def slide_four_steps(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="PATTERN  ·  4 STEPS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("작게 시작 + 한 번에 하나만 + 매 단계 검증",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("Baseline → Expand → Optimize → Interact — 한 step 끝나면 반드시 브라우저로 확인",
               {"style": "lead", "color": C.body})])

    # 4 step cards
    row_y = Inches(2.7)
    card_h = Inches(3.0)
    gap = Inches(0.18)
    card_w = (CONTENT_W - gap * 3) // 4

    steps = [
        ("1", "BASELINE",  "가장 작은 데이터\n+ 가장 단순한\n레이어 하나",
         "admdong choropleth",  "emphasis"),
        ("2", "EXPAND",    "두 번째 레이어\n추가",
         "OD flow lines",       "outline"),
        ("3", "OPTIMIZE",  "무거운 데이터 +\n한 번에 한 트릭만",
         "bbox stream · LOD",   "outline"),
        ("4", "INTERACT",  "패널 · 토글 · 호버\n· 통계 패널",
         "tabs · tooltip · stats", "outline"),
    ]
    for i, (num, head, body, eg, tone) in enumerate(steps):
        x = MARGIN_X + (card_w + gap) * i
        if tone == "emphasis":
            add_rounded(s, x, row_y, card_w, card_h, fill=C.primary, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            n_c, h_c, b_c, eg_c = C.mute, C.on_dark, C.mute, C.on_dark
        else:
            add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas_soft, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            n_c, h_c, b_c, eg_c = C.mute, C.ink, C.body, C.ink
        pad = Inches(0.26)
        add_text(s, x + pad, row_y + pad, card_w - pad * 2, Inches(0.5),
                 [(num, {"style": "display_lg", "color": n_c})])
        add_text(s, x + pad, row_y + pad + Inches(0.55),
                 card_w - pad * 2, Inches(0.4),
                 [(head, {"style": "display_sm", "color": h_c,
                          "letter_spacing_pt": 0.6})])
        add_text(s, x + pad, row_y + pad + Inches(1.05),
                 card_w - pad * 2, Inches(1.3),
                 [(body, {"style": "body_sm", "color": b_c,
                          "line_spacing": 1.35})])
        # example pill at bottom
        eg_w = card_w - pad * 2
        eg_h = Inches(0.40)
        eg_y = row_y + card_h - pad - eg_h
        bg = C.canvas if tone == "emphasis" else C.canvas
        add_rounded(s, x + pad, eg_y, eg_w, eg_h,
                    fill=bg, line=None, radius_ratio=0.5)
        add_text(s, x + pad, eg_y, eg_w, eg_h,
                 [(eg, {"style": "caption_b", "color": C.ink, "code": True,
                        "letter_spacing_pt": 0.6})],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # arrow to next
        if i < 3:
            ax1 = x + card_w + Inches(0.02)
            ax2 = x + card_w + gap - Inches(0.02)
            ay = row_y + card_h // 2
            add_arrow(s, ax1, ay, ax2, ay,
                      color=C.hairline_mid, weight_pt=1.0)

    # rules
    rl_y = row_y + card_h + Inches(0.30)
    add_rounded(s, MARGIN_X, rl_y, CONTENT_W, Inches(0.9), fill=C.primary,
                line=None, radius_ratio=radius_for(CONTENT_W, Inches(0.9), 0.21))
    add_text(s, MARGIN_X + Inches(0.36), rl_y + Inches(0.17),
             Inches(8), Inches(0.32),
             [("RULES", {"style": "eyebrow", "color": C.mute})])
    add_text(s, MARGIN_X + Inches(0.36), rl_y + Inches(0.42),
             CONTENT_W - Inches(0.72), Inches(0.5),
             [("브라우저 확인  ·  step 단위 git commit  ·  막히면 step 되돌리고 그것만 다시",
               {"style": "body_md_b", "color": C.on_dark})])


# ============================================================================
# slide 05 — 컨텍스트 블록 (학생 복붙)
# ============================================================================

def slide_context_block(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="PROMPTING  ·  CONTEXT",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("매번 던질 컨텍스트 블록",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("매 단계 첫 프롬프트에 이대로 첨부.  마지막 한 줄이 핵심 — AI 가 멋대로 달리지 못하게",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "프로젝트 컨텍스트:",
        "- 작업 디렉터리: F:\\research\\TAZ",
        "- 데이터 명세는 data/README.md 참조",
        "- 본 강의 산출물 위치:",
        "    data/derived/lecture_outputs/pi_aj_v1.parquet   (Lec3)",
        "    data/derived/lecture_outputs/od_matrix_v1.parquet (Lec4)",
        "- 행정동 경계: data/raw/admdong_boundary/admdong_2023.geojson",
        "- 참조 뷰어: data/viewer/index.html",
        "- 실행: python -m RangeHTTPServer 8765,",
        "         http://localhost:8765/<path>/",
        "",
        "제약:",
        "- 백엔드 만들지 마. 정적 HTML + Python 변환 스크립트 + fgb 파일만.",
        "- 외부 라이브러리는 CDN 으로 (npm / build 도구 X).",
        "- 모든 산출물은 my_viewer/ 폴더 안에.",
        "- 코드 짜기 전에 어떤 라이브러리 · 접근법 쓸지 먼저 알려주고 확인 받기.",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(9.6), Inches(4.7),
                  code_lines, label="copy-paste · context block",
                  font_pt=10, line_spacing=1.18)

    # right: emphasis pill on the last constraint
    nx = MARGIN_X + Inches(9.9)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_dark(s, nx, Inches(2.55), nw, Inches(4.7), radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad, nw - pad * 2, Inches(0.32),
             [("KEY LINE", {"style": "eyebrow", "color": C.mute})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.36),
             nw - pad * 2, Inches(1.5),
             [("‘코드 짜기 전\n어떤 라이브러리·\n접근법 쓸지\n먼저 알려주고\n확인 받기’",
               {"style": "display_sm", "color": C.on_dark,
                "line_spacing": 1.25})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(2.40),
             nw - pad * 2, Inches(2.0),
             [("이 한 줄로\nAI 가 헛 코드\n양산 못함.\n\n"
               "‘구현 전 brake’\n— vibe-coding 의\n가장 강력한 패턴",
               {"style": "body_sm", "color": C.mute,
                "line_spacing": 1.35})])


# ============================================================================
# slide 06 — Vocabulary 10
# ============================================================================

def slide_vocab(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="VOCABULARY  ·  10 TERMS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("학생이 알아야 할 단어 10개",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("코드는 AI 가 씀.  학생은 이 단어들을 알고 ‘무엇을 요청할지’ 정하면 됨",
               {"style": "lead", "color": C.body})])

    # table
    tab_x = MARGIN_X
    tab_y = Inches(2.55)
    tab_w = CONTENT_W
    tab_h = Inches(4.7)
    add_card_content(s, tab_x, tab_y, tab_w, tab_h, radius_in=0.21)

    pad = Inches(0.35)
    head_y = tab_y + pad + Inches(0.10)

    cols = [
        ("TERM",      Inches(0.0),  Inches(2.6)),
        ("ONE-LINE",  Inches(2.7),  Inches(5.0)),
        ("WHEN",      Inches(7.8),  tab_w - pad * 2 - Inches(7.8)),
    ]
    for h, x_off, w in cols:
        add_text(s, tab_x + pad + x_off, head_y, w, Inches(0.3),
                 [(h, {"style": "eyebrow", "color": C.body})])

    rows = [
        ("FlatGeobuf (fgb)",   "bbox 부분 로드 바이너리 지오포맷",     "1만+ feature 시각화"),
        ("bbox streaming",     "보이는 부분만 다운로드",                "줌인 시 빠른 응답"),
        ("deck.gl",            "GPU 가속 지도 레이어 라이브러리",       "다중 레이어 인터랙티브"),
        ("GeoJsonLayer",       "폴리곤·선·점 (CPU 삼각분할)",          "5천 feature 이하 폴리곤"),
        ("ScatterplotLayer",   "점 전용 GPU 레이어",                    "폴리곤 → centroid 단순화 후"),
        ("LOD (min/maxZoom)",  "줌별 다른 데이터",                       "줌 12 에 필지 안 보여도 됨"),
        ("centroid 단순화",     "폴리곤 → 점 변환",                       "90만 필지 같은 거대 폴리곤"),
        ("set_precision(1e-6)","좌표 정밀도 ≈ 10cm",                     "fgb 크기 30% ↓"),
        ("MapLibre + CARTO",   "무료 베이스맵 (Mapbox 토큰 X)",          "매번"),
        ("RangeHTTPServer",    "HTTP Range 지원 Python 서버",            "bbox streaming 필요 시"),
    ]
    rh = Inches(0.35)
    ry = head_y + Inches(0.40)
    for ri, (term, oneliner, when) in enumerate(rows):
        if ri > 0:
            add_hairline(s, tab_x + pad, ry - Inches(0.05),
                         tab_w - pad * 2, color=C.hairline_soft)
        add_text(s, tab_x + pad, ry, Inches(2.6), Inches(0.3),
                 [(term, {"style": "body_sm_b", "color": C.ink, "code": True})])
        add_text(s, tab_x + pad + Inches(2.7), ry,
                 Inches(5.0), Inches(0.3),
                 [(oneliner, {"style": "body_sm", "color": C.body})])
        add_text(s, tab_x + pad + Inches(7.8), ry,
                 tab_w - pad * 2 - Inches(7.8), Inches(0.3),
                 [(when, {"style": "body_sm", "color": C.body, "code": True})])
        ry += rh


# ============================================================================
# slide 07 — Step 1 baseline prompt (code)
# ============================================================================

def slide_step1_prompt(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="STEP 1  ·  BASELINE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("Step 1 — admdong + P_obs 색칠",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("가장 작은 데이터로 ‘fgb + GeoJsonLayer + 색칠 + 호버’ 만 — 그게 baseline",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "[위 컨텍스트 블록]",
        "",
        "가장 단순한 뷰어를 만들어줘.",
        "",
        "산출:",
        "1. my_viewer/prepare.py",
        "   - pi_aj_v1.parquet + admdong_2023.geojson join",
        "   - 서울만 (sidonm 컬럼에 '서울' 포함)",
        "   - my_viewer/adm.fgb 로 저장 (FlatGeobuf)",
        "   - EPSG:4326, set_precision(geom, 1e-6)",
        "",
        "2. my_viewer/index.html",
        "   - deck.gl + maplibre-gl + flatgeobuf-geojson (CDN)",
        "   - CARTO dark 베이스맵 (토큰 X)",
        "   - adm.fgb 를 GeoJsonLayer 로",
        "   - P_obs 값에 따라 색칠 (viridis, log scale)",
        "   - 호버 시 admdong 이름 + P_obs 툴팁",
        "",
        "3. my_viewer/README.md — 실행 방법 한 단락",
        "",
        "코드 짜기 전에 어떤 CDN 버전을 쓸지 알려주고 확인 받아.",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.6), Inches(4.7),
                  code_lines, label="prompt · step 1",
                  font_pt=10, line_spacing=1.18)

    # right: verify checklist
    nx = MARGIN_X + Inches(8.9)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("STUDENT VERIFY", {"style": "eyebrow", "color": C.body})])

    checks = [
        ("prepare.py 실행", "fgb 생성  ·  크기 < 1 MB"),
        ("브라우저 띄움",    "폴리곤이 보이나"),
        ("face validity",   "강남·종로 더 진한가"),
        ("호버 동작",       "마우스 → 툴팁 즉시"),
    ]
    sy = Inches(2.55) + pad + Inches(0.40)
    for k, v in checks:
        add_text(s, nx + pad, sy, nw - pad * 2, Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.ink})])
        add_text(s, nx + pad, sy + Inches(0.28),
                 nw - pad * 2, Inches(0.55),
                 [(v, {"style": "body_sm", "color": C.body})])
        sy += Inches(0.95)


# ============================================================================
# slide 08 — Step 3 optimize: "코드 짜지 마, 먼저 의견"
# ============================================================================

def slide_step3_optimize(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="STEP 3  ·  OPTIMIZE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("Step 3 — ‘코드 짜지 마, 먼저 의견 줘’",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("19,097 OA 추가 — 무거운 데이터 들어가기 전, 트레이드오프 표를 먼저 받는다",
               {"style": "lead", "color": C.body})])

    # left: 두-단계 프롬프트 시퀀스
    code_lines_1 = [
        "[컨텍스트]",
        "",
        "이제 OA 19,097 폴리곤 (~19MB) 을 추가하려고 해.",
        "",
        "코드 작성 전에 분석부터 해줘:",
        "",
        "1. bbox streaming 이 필요한가, 한 번 fetch 면 충분?",
        "2. 폴리곤 그대로 GeoJsonLayer 인가, centroid 점으로?",
        "3. 줌 11(전체) 에서도 보여야 하나, LOD 로 줌12+ 만?",
        "4. 어떤 컬럼을 색칠 변수로 노출할까?",
        "",
        "각 선택지의 트레이드오프 설명 후, data/viewer/oa.fgb",
        "처리 방식과 비교해서 추천해줘.",
        "동의하면 그때 구현 요청할게.",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(6.4), Inches(3.0),
                  code_lines_1, label="prompt · ask first",
                  font_pt=10, line_spacing=1.18)

    code_lines_2 = [
        "좋아. bbox streaming + GeoJsonLayer + 줌 11+ 부터,",
        "색칠 변수는 pop_total / lp_pool_24h / lp_pool_morning",
        "세 가지 드롭다운으로 가자.",
        "구현해줘.",
    ]
    add_code_cell(s, MARGIN_X, Inches(5.75),
                  Inches(6.4), Inches(1.50),
                  code_lines_2, label="prompt · approve + build",
                  font_pt=11, line_spacing=1.20)

    # arrow between
    add_arrow(s, MARGIN_X + Inches(3.2), Inches(5.60),
              MARGIN_X + Inches(3.2), Inches(5.72),
              color=C.hairline_mid, weight_pt=1.25)

    # right: pattern card (emphasis)
    nx = MARGIN_X + Inches(6.7)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_dark(s, nx, Inches(2.55), nw, Inches(4.7), radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("WHY  ·  TWO-STAGE PROMPT",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.36),
             nw - pad * 2, Inches(1.0),
             [("AI 가 헛 코드\n양산 못 함",
               {"style": "display_sm", "color": C.on_dark,
                "line_spacing": 1.25})])

    points = [
        ("ASK first",   "트레이드오프 표를 받음.\n학생이 ‘무엇을’ 정한다."),
        ("THEN build",  "동의한 결정만 코드로.\nrework 비용 ↓"),
        ("compare ref", "data/viewer/ 와 비교하라\n는 한 마디가 품질 잡음"),
    ]
    py = Inches(2.55) + pad + Inches(1.65)
    for k, v in points:
        add_text(s, nx + pad, py, nw - pad * 2, Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.on_dark,
                       "code": True})])
        add_text(s, nx + pad, py + Inches(0.30),
                 nw - pad * 2, Inches(0.75),
                 [(v, {"style": "body_sm", "color": C.mute})])
        py += Inches(1.10)


# ============================================================================
# slide 09 — F12 가 학생의 눈 (검증 표)
# ============================================================================

def slide_f12_verify(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="VERIFY  ·  F12",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("F12 가 학생의 눈",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("‘동작한다고 했다’ ≠ ‘동작한다’.  AI 는 화면을 못 봄 — 직접 띄워서 확인",
               {"style": "lead", "color": C.body})])

    # verify table
    tab_x = MARGIN_X
    tab_y = Inches(2.55)
    tab_w = CONTENT_W
    tab_h = Inches(4.7)
    add_card_content(s, tab_x, tab_y, tab_w, tab_h, radius_in=0.21)

    pad = Inches(0.35)
    cols = [
        ("ITEM",   Inches(0.0),   Inches(1.8)),
        ("WHERE",  Inches(1.9),   Inches(2.6)),
        ("WHAT",   Inches(4.6),   Inches(4.6)),
        ("TARGET", Inches(9.3),   tab_w - pad * 2 - Inches(9.3)),
    ]
    head_y = tab_y + pad + Inches(0.10)
    for h, x_off, w in cols:
        add_text(s, tab_x + pad + x_off, head_y, w, Inches(0.3),
                 [(h, {"style": "eyebrow", "color": C.body})])

    rows = [
        ("첫 frame",       "그냥 띄움",                    "5초 이내에 뭐가 보이나",          "5초+"),
        ("콘솔 에러",      "F12 → Console",               "빨간 에러 없나",                   "0개"),
        ("데이터 일치",     "패널 통계 vs 노트북",          "mean / median 일치?",              "일치"),
        ("FPS",            "Performance 녹화 → 줌·팬",     "FPS 메터 30+",                     "30+"),
        ("Network",        "Network → 줌인",              "새 fgb 청크 요청 가나",            "가야 함"),
        ("Face validity",  "시각으로",                    "강남 hotspot? 외곽 producer?",     "직관 일치"),
    ]
    rh = Inches(0.62)
    ry = head_y + Inches(0.40)
    for ri, (item, where, what, target) in enumerate(rows):
        if ri > 0:
            add_hairline(s, tab_x + pad, ry - Inches(0.06),
                         tab_w - pad * 2, color=C.hairline_soft)
        add_text(s, tab_x + pad, ry, Inches(1.8), Inches(0.5),
                 [(item, {"style": "body_md_b", "color": C.ink})])
        add_text(s, tab_x + pad + Inches(1.9), ry, Inches(2.6), Inches(0.5),
                 [(where, {"style": "body_sm", "color": C.body, "code": True})])
        add_text(s, tab_x + pad + Inches(4.6), ry, Inches(4.6), Inches(0.5),
                 [(what, {"style": "body_sm", "color": C.body})])
        # target pill
        tp_w = Inches(1.3); tp_h = Inches(0.34)
        tp_x = tab_x + tab_w - pad - tp_w
        tp_y = ry + Inches(0.08)
        add_rounded(s, tp_x, tp_y, tp_w, tp_h, fill=C.primary, line=None,
                    radius_ratio=0.5)
        add_text(s, tp_x, tp_y, tp_w, tp_h,
                 [(target, {"style": "caption_b", "color": C.on_dark,
                            "letter_spacing_pt": 0.6})],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        ry += rh


# ============================================================================
# slide 10 — 막혔을 때 다음 한마디
# ============================================================================

def slide_stuck_phrases(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="STUCK  ·  NEXT LINE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("막혔을 때 다음 한마디",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("‘안 돼’ 만으론 AI 가 진단 불가 — 무엇이 / 어디서 / 어떻게 한 줄 더",
               {"style": "lead", "color": C.body})])

    # table
    tab_x = MARGIN_X
    tab_y = Inches(2.55)
    tab_w = CONTENT_W
    tab_h = Inches(4.7)
    add_card_content(s, tab_x, tab_y, tab_w, tab_h, radius_in=0.21)

    pad = Inches(0.35)
    head_y = tab_y + pad + Inches(0.10)

    add_text(s, tab_x + pad, head_y, Inches(3.8), Inches(0.3),
             [("SYMPTOM", {"style": "eyebrow", "color": C.body})])
    add_text(s, tab_x + pad + Inches(3.9), head_y,
             tab_w - pad * 2 - Inches(3.9), Inches(0.3),
             [("NEXT LINE  ·  WHAT TO SAY",
               {"style": "eyebrow", "color": C.body})])

    rows = [
        ("폴리곤 안 보임",
         "‘콘솔 에러는 [붙여넣기].  ogrinfo adm.fgb 결과는 X feat’"),
        ("보이지만 색이 단색",
         "‘P_obs 분포가 [min~max], 색 매핑 도메인이 그 범위 맞나’"),
        ("회색 화면",
         "‘베이스맵 fetch 안 됨.  Network 탭에 cartocdn 401/403’"),
        ("너무 느림",
         "‘FPS 12 @ 줌13.  Performance 녹화에 GeoJsonLayer main-thread 점유’"),
        ("줌인 데이터 안 늘어남",
         "‘Network 에서 fgb 청크 새로 안 받음.  bbox streaming 코드 확인’"),
        ("호버 안 됨",
         "‘pickable: true 빠진 거 아닌가’"),
        ("fgb 파일 너무 큼",
         "‘출력 fgb 가 30MB.  set_precision / drop / dtype 어느 거 빠짐’"),
    ]
    rh = Inches(0.55)
    ry = head_y + Inches(0.40)
    for ri, (sym, msg) in enumerate(rows):
        if ri > 0:
            add_hairline(s, tab_x + pad, ry - Inches(0.04),
                         tab_w - pad * 2, color=C.hairline_soft)
        add_text(s, tab_x + pad, ry, Inches(3.8), Inches(0.5),
                 [(sym, {"style": "body_md_b", "color": C.ink})])
        add_text(s, tab_x + pad + Inches(3.9), ry,
                 tab_w - pad * 2 - Inches(3.9), Inches(0.5),
                 [(msg, {"style": "body_sm", "color": C.body, "code": True})])
        ry += rh


# ============================================================================
# slide 11 — 과제 + 평가
# ============================================================================

def slide_assignment(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="ASSIGNMENT  ·  RUBRIC",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("과제 — 본인의 mini viewer",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("핵심은 ‘작게 시작 + 단계별 검증’ 패턴.  결과물보다 AI 와의 대화 방식이 평가 대상",
               {"style": "lead", "color": C.body})])

    # 3 columns: 최소 / 도전 / 평가
    col_y = Inches(2.55)
    col_h = Inches(4.7)
    col_w = (CONTENT_W - Inches(0.30) * 2) // 3

    # 최소 (outline)
    cx = MARGIN_X
    add_rounded(s, cx, col_y, col_w, col_h, fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(col_w, col_h, 0.21))
    pad = Inches(0.30)
    add_text(s, cx + pad, col_y + pad, col_w - pad * 2, Inches(0.32),
             [("최소 요구", {"style": "eyebrow", "color": C.body})])
    add_text(s, cx + pad, col_y + pad + Inches(0.36),
             col_w - pad * 2, Inches(0.55),
             [("MUST", {"style": "display_md", "color": C.ink})])
    must = [
        "pi_aj_v1.parquet 시각화\n(admdong P_obs choropleth)",
        "od_matrix_v1.parquet 시각화\n(top OD flow lines)",
        "5~8 단계별 프롬프트 복붙 OK\n변형도 OK",
        "README — 변경한 부분\n한 단락",
    ]
    my = col_y + pad + Inches(1.10)
    for m in must:
        add_text(s, cx + pad, my, col_w - pad * 2, Inches(0.7),
                 [("·  " + m, {"style": "body_sm", "color": C.body})])
        my += Inches(0.78)

    # 도전 (emphasis)
    cx2 = cx + col_w + Inches(0.30)
    add_rounded(s, cx2, col_y, col_w, col_h, fill=C.primary, line=None,
                radius_ratio=radius_for(col_w, col_h, 0.21))
    add_text(s, cx2 + pad, col_y + pad, col_w - pad * 2, Inches(0.32),
             [("도전 (선택)", {"style": "eyebrow", "color": C.mute})])
    add_text(s, cx2 + pad, col_y + pad + Inches(0.36),
             col_w - pad * 2, Inches(0.55),
             [("BONUS", {"style": "display_md", "color": C.on_dark})])
    bonus = [
        "OA 단위 레이어 추가\n(oa_master 컬럼 색칠)",
        "필지 점 추가\n(seoul_parcels_pts.fgb)",
        "LOD 동작\n(줌별 자동 토글)",
        "시간대별 OD 토글\n(MOVE_PURPOSE)",
    ]
    by = col_y + pad + Inches(1.10)
    for b in bonus:
        add_text(s, cx2 + pad, by, col_w - pad * 2, Inches(0.7),
                 [("·  " + b, {"style": "body_sm", "color": C.mute})])
        by += Inches(0.78)

    # 평가 (outline)
    cx3 = cx2 + col_w + Inches(0.30)
    add_rounded(s, cx3, col_y, col_w, col_h, fill=C.canvas, line=C.hairline,
                line_w_pt=0.75,
                radius_ratio=radius_for(col_w, col_h, 0.21))
    add_text(s, cx3 + pad, col_y + pad, col_w - pad * 2, Inches(0.32),
             [("평가  ·  RUBRIC", {"style": "eyebrow", "color": C.body})])
    add_text(s, cx3 + pad, col_y + pad + Inches(0.36),
             col_w - pad * 2, Inches(0.55),
             [("GRADED", {"style": "display_md", "color": C.ink})])
    rubric = [
        "검증 체크리스트 (§ 9)\n6개 중 5개 통과",
        "데이터 정확성 —\n패널 통계 vs 노트북",
        "AI 대화가 ‘작게 시작 +\n단계별 검증’ 따랐나",
        "프롬프트가 명세적인가\n(‘잘 만들어줘’ 류 없나)",
    ]
    ry = col_y + pad + Inches(1.10)
    for r in rubric:
        add_text(s, cx3 + pad, ry, col_w - pad * 2, Inches(0.7),
                 [("·  " + r, {"style": "body_sm", "color": C.body})])
        ry += Inches(0.78)


# ============================================================================
# slide 12 — summary
# ============================================================================

def slide_summary(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SUMMARY  ·  RECAP",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("정리 — A1 에서 챙길 6가지",
               {"style": "display_xl", "color": C.ink})])

    row_y = Inches(2.2)
    card_w = (CONTENT_W - Inches(0.2) * 5) // 6
    card_h = Inches(2.7)
    cards = [
        ("1", "명세",        "‘잘 만들어줘’ X\n명세 + 분할 + 검증"),
        ("2", "4 step",      "Baseline → Expand\n→ Optimize → Interact"),
        ("3", "컨텍스트",     "매번 컨텍스트 블록.\n경로 · 제약 · 참조"),
        ("4", "Vocabulary",  "단어 10개 — fgb,\nbbox, deck.gl, ..."),
        ("5", "F12",         "AI 는 화면 못 봄.\n학생이 직접 띄움"),
        ("6", "막힐 때",     "무엇이 / 어디서 /\n어떻게 — 한 줄 더"),
    ]
    for i, (num, head, body) in enumerate(cards):
        x = MARGIN_X + (card_w + Inches(0.2)) * i
        add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(card_w, card_h, 0.21))
        pad = Inches(0.20)
        add_text(s, x + pad, row_y + pad, card_w - pad * 2, Inches(0.5),
                 [(num, {"style": "display_lg", "color": C.mute})])
        add_text(s, x + pad, row_y + pad + Inches(0.55),
                 card_w - pad * 2, Inches(0.5),
                 [(head, {"style": "display_sm", "color": C.ink})])
        add_text(s, x + pad, row_y + pad + Inches(1.10),
                 card_w - pad * 2, Inches(1.5),
                 [(body, {"style": "body_sm", "color": C.body,
                          "line_spacing": 1.35})])

    # bottom: closing dark card
    pr_y = Inches(5.20)
    pr_h = Inches(1.7)
    add_card_dark(s, MARGIN_X, pr_y, CONTENT_W, pr_h, radius_in=0.21)
    pad = Inches(0.5)
    add_text(s, MARGIN_X + pad, pr_y + pad, Inches(4), Inches(0.32),
             [("CLOSING  ·  WHAT TO REMEMBER",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, MARGIN_X + pad, pr_y + pad + Inches(0.3),
             Inches(9), Inches(0.7),
             [("코드를 외우지 말 것.  AI 에게 ‘무엇을 어떻게 요청할지’ 만 알면 충분",
               {"style": "display_md", "color": C.on_dark})])
    btn_w = Inches(2.4); btn_h = Inches(0.55)
    btn_x = MARGIN_X + CONTENT_W - pad - btn_w
    btn_y = pr_y + (pr_h - btn_h) // 2
    add_rounded(s, btn_x, btn_y, btn_w, btn_h, fill=C.canvas, line=None,
                radius_ratio=0.5)
    add_text(s, btn_x, btn_y, btn_w, btn_h,
             [("Lec4 메인으로 ←", {"style": "button", "color": C.ink})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# main
# ============================================================================

def build():
    prs = Presentation()
    setup_169(prs)

    slides = [
        slide_title,
        slide_touch_reference,
        slide_why_one_liner_fails,
        slide_four_steps,
        slide_context_block,
        slide_vocab,
        slide_step1_prompt,
        slide_step3_optimize,
        slide_f12_verify,
        slide_stuck_phrases,
        slide_assignment,
        slide_summary,
    ]
    total = len(slides)

    for i, fn in enumerate(slides, start=1):
        fn(prs, i, total)

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "slides", "A1_vibe_coding_viewer.pptx",
    )
    prs.save(out)
    print(f"OK · {total} slides · {out}")
    return out


if __name__ == "__main__":
    build()
