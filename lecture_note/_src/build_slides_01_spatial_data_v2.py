"""01_spatial_data.pptx — Lecture 1 deck (16:9, Uber design system + Pretendard).

Pillars:
  - black-and-white duet, pill 999 px on every interactive shape
  - editorial illustrations absent; visual rhythm carried by polarity flips
  - Pretendard ExtraBold / Bold / Medium / ExtraLight only
  - code rendered as light code cells (canvas-softer + Cascadia Code), tight line-spacing
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


DECK_LABEL = "TAZ · Lecture 1 · 서울 공간 데이터"


# ============================================================================
# helpers — local diagram primitives
# ============================================================================

def step_card(slide, x, y, w, h, *, head, body, tone="light"):
    """Numbered/labelled step card used inside flow diagrams.

    tone='light'      → canvas-soft fill, ink text (default step)
    tone='emphasis'   → black fill, white text (scope highlight)
    tone='outline'    → white fill, hairline border (out-of-scope step)
    """
    if tone == "light":
        add_rounded(slide, x, y, w, h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(w, h, 0.18))
        head_color, body_color = C.ink, C.body
    elif tone == "emphasis":
        add_rounded(slide, x, y, w, h, fill=C.primary, line=None,
                    radius_ratio=radius_for(w, h, 0.18))
        head_color, body_color = C.on_dark, C.on_dark
    elif tone == "outline":
        add_rounded(slide, x, y, w, h, fill=C.canvas, line=C.hairline,
                    line_w_pt=0.75,
                    radius_ratio=radius_for(w, h, 0.18))
        head_color, body_color = C.ink, C.body
    else:
        raise ValueError(tone)

    pad = Inches(0.20)
    add_text(slide, x + pad, y + pad, w - pad * 2, h - pad * 2,
             [(head, {"style": "display_sm", "color": head_color}),
              (body, {"style": "body_sm", "color": body_color,
                      "space_before": 3})])


def caption_arrow(slide, x1, y1, x2, y2, label=None):
    add_arrow(slide, x1, y1, x2, y2, color=C.hairline_mid, weight_pt=1.25)
    if label:
        mx = (x1 + x2) // 2
        my = (y1 + y2) // 2
        add_text(slide, mx - Inches(0.7), my - Inches(0.18),
                 Inches(1.4), Inches(0.3),
                 [(label, {"style": "caption", "color": C.body})],
                 align=PP_ALIGN.CENTER)


# ============================================================================
# slide 01 — title
# ============================================================================

def slide_title(prs, idx, total):
    s = new_blank_slide(prs)

    # left column: eyebrow → hero → subtitle → CTA pill row
    eyebrow_y = Inches(1.2)
    title_y   = Inches(1.7)
    sub_y     = Inches(4.3)
    cta_y     = Inches(5.6)

    add_text(s, MARGIN_X, eyebrow_y, Inches(7), Inches(0.4),
             [("LECTURE 01  ·  4 OF 30",
               {"style": "eyebrow", "color": C.ink})])

    add_text(s, MARGIN_X, title_y, Inches(7.2), Inches(2.5),
             [("강좌 개요\n+ 서울 공간 데이터",
               {"style": "display_xxl", "color": C.ink,
                "line_spacing": 1.08})])

    add_text(s, MARGIN_X, sub_y, Inches(7.2), Inches(1.1),
             [("서울의 공간 단위(필지 · OA · admdong · 자치구)와 좌표계 3종을 익혀\n"
               "이후 모든 모듈의 raw 데이터를 읽을 수 있게 한다.",
               {"style": "lead", "color": C.body})])

    add_pill(s, MARGIN_X,            cta_y, Inches(1.85), Inches(0.5),
             "Open notebook",  variant="primary")
    add_pill(s, MARGIN_X + Inches(2.00), cta_y, Inches(1.65), Inches(0.5),
             "View raw data",  variant="secondary")

    # right column: a single 'overview card' — content card chrome
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
        ("왜",            "통행수요 분석은\n‘어떤 공간 단위에서 하는가’ 로 시작·끝남"),
        ("4단계 모형 위치","강좌 도입 — 1·2단계\n(Generation · Distribution) 의 단위 결정"),
        ("사전지식",      "없음 (강좌 시작)"),
        ("이번 시간 산출", "개념 정리만 (파일 산출 X)"),
    ]
    rh = Inches(0.95)
    for i, (k, v) in enumerate(rows):
        ry = row_y + rh * i
        if i > 0:
            add_hairline(s, card_x + pad, ry - Inches(0.05),
                         card_w - pad * 2, color=C.hairline_soft)
        add_text(s, card_x + pad, ry, Inches(1.2), Inches(0.4),
                 [(k, {"style": "body_md_b", "color": C.ink})])
        add_text(s, card_x + pad + Inches(1.25), ry,
                 card_w - pad * 2 - Inches(1.25), Inches(0.8),
                 [(v, {"style": "body_sm", "color": C.body})])

    # footer block
    add_hairline(s, MARGIN_X, SLIDE_H - Inches(0.85),
                 SLIDE_W - MARGIN_X * 2, color=C.hairline_soft)
    add_text(s, MARGIN_X, SLIDE_H - Inches(0.72), Inches(8), Inches(0.3),
             [("TAZ STUDIO  ·  서울 통행수요 강좌",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, SLIDE_W - MARGIN_X - Inches(3), SLIDE_H - Inches(0.72),
             Inches(3), Inches(0.3),
             [(f"01 / {total:02d}", {"style": "eyebrow", "color": C.body,
                                     "letter_spacing_pt": 1.6})],
             align=PP_ALIGN.RIGHT)


# ============================================================================
# slide 02 — 강좌 전체 흐름 (5 cards horizontal)
# ============================================================================

def slide_course_flow(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="STRUCTURE  ·  COURSE FLOW",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(10), Inches(0.7),
             [("강좌 전체 흐름",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("Lec1·2 = 공통 데이터 단계 ·  Lec3·4 = 통행 수요 메인 ·  Lec5 = 도시 형태 부록",
               {"style": "lead", "color": C.body})])

    # main row: 4 cards Lec1→2→3→4
    row_y = Inches(2.8)
    card_w = Inches(2.6)
    card_h = Inches(2.2)
    gap = Inches(0.30)
    total_w = card_w * 4 + gap * 3
    start_x = (SLIDE_W - total_w) // 2

    main_titles = [
        ("Lec 1", "공간 데이터",      "오늘 — 단위·좌표계"),
        ("Lec 2", "OA 마스터",        "SGIS + LOCAL_PEOPLE"),
        ("Lec 3", "P / A 발생",       "admdong 통행 발생"),
        ("Lec 4", "OD 추정",          "admdong OD 행렬"),
    ]
    for i, (eb, name, sub) in enumerate(main_titles):
        x = start_x + (card_w + gap) * i
        # all main cards: emphasis if scope (i=0), light for rest
        tone = "emphasis" if i == 0 else "light"
        if tone == "emphasis":
            add_rounded(s, x, row_y, card_w, card_h, fill=C.primary, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            head, body, eb_color = C.on_dark, C.on_dark, C.mute
        else:
            add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas_soft, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            head, body, eb_color = C.ink, C.body, C.body

        pad = Inches(0.30)
        add_text(s, x + pad, row_y + pad, card_w - pad * 2, Inches(0.3),
                 [(eb, {"style": "eyebrow", "color": eb_color})])
        add_text(s, x + pad, row_y + pad + Inches(0.45),
                 card_w - pad * 2, Inches(0.7),
                 [(name, {"style": "display_lg", "color": head,
                          "line_spacing": 1.15})])
        add_text(s, x + pad, row_y + card_h - pad - Inches(0.7),
                 card_w - pad * 2, Inches(0.7),
                 [(sub, {"style": "body_sm", "color": body})])

    # arrows between main cards
    arrow_y = row_y + card_h // 2
    for i in range(3):
        x1 = start_x + (card_w + gap) * i + card_w + Inches(0.04)
        x2 = start_x + (card_w + gap) * (i + 1) - Inches(0.04)
        add_arrow(s, x1, arrow_y, x2, arrow_y,
                  color=C.hairline_mid, weight_pt=1.25)

    # Lec5 branch — appears as a separate card below Lec3/4 region with branch line
    branch_y = row_y + card_h + Inches(0.55)
    branch_w = Inches(5.4)
    branch_h = Inches(1.05)
    branch_x = (SLIDE_W - branch_w) // 2 + Inches(0.6)

    add_rounded(s, branch_x, branch_y, branch_w, branch_h,
                fill=C.canvas, line=C.hairline, line_w_pt=0.75,
                radius_ratio=radius_for(branch_w, branch_h, 0.21))
    pad = Inches(0.30)
    add_text(s, branch_x + pad, branch_y + pad,
             Inches(1.2), Inches(0.35),
             [("LEC 5  ·  부록", {"style": "eyebrow", "color": C.body})])
    add_text(s, branch_x + pad, branch_y + pad + Inches(0.30),
             branch_w - pad * 2, Inches(0.55),
             [("도시 형태 — superblock + 토지이용 (block_master)",
               {"style": "display_sm", "color": C.ink})])

    # branch line from Lec2 bottom down to Lec5 top-left
    lec2_x = start_x + (card_w + gap) * 1
    lec2_bottom_x = lec2_x + card_w // 2
    lec2_bottom_y = row_y + card_h
    add_arrow(s, lec2_bottom_x, lec2_bottom_y,
              branch_x + Inches(0.6), branch_y,
              color=C.hairline_mid, weight_pt=1.0)


# ============================================================================
# slide 03 — 4단계 통행수요모형
# ============================================================================

def slide_4step_model(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="CONCEPT  ·  4-STEP MODEL",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("4단계 통행수요모형 — 무엇을 만드나",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("본 강좌 = 1·2단계.  이론은 교재 참조 → 강좌는 ‘실데이터 적용의 어려움’에 집중",
               {"style": "lead", "color": C.body})])

    # 4 cards
    row_y = Inches(2.95)
    card_w = Inches(2.85)
    card_h = Inches(2.55)
    gap = Inches(0.22)
    total_w = card_w * 4 + gap * 3
    start_x = (SLIDE_W - total_w) // 2

    items = [
        ("1", "Trip Generation",    "발생 · 유인량",
         "Pᵢ = 지역 i 에서 출발하는 통행 수\nAⱼ = 지역 j 에 도착하는 통행 수",
         "Lecture 3",  "emphasis"),
        ("2", "Trip Distribution",  "분포",
         "Tᵢⱼ = 지역 i → j 통행 행렬",
         "Lecture 4",  "emphasis"),
        ("3", "Mode Choice",        "수단 분담",
         "차·지하철·버스 선택 모형",
         "강좌 외", "outline"),
        ("4", "Network Assignment", "배정",
         "도로 네트워크 위 통행량 배정",
         "강좌 외", "outline"),
    ]

    for i, (num, en, ko, body, scope, tone) in enumerate(items):
        x = start_x + (card_w + gap) * i
        if tone == "emphasis":
            add_rounded(s, x, row_y, card_w, card_h, fill=C.primary, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            n_color, head_color, body_color, scope_bg, scope_text = (
                C.on_dark, C.on_dark, C.mute, C.on_dark, C.ink)
        else:
            add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas, line=C.hairline,
                        line_w_pt=0.75,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            n_color, head_color, body_color, scope_bg, scope_text = (
                C.mute, C.ink, C.body, C.canvas_soft, C.body)

        pad = Inches(0.28)
        add_text(s, x + pad, row_y + pad, Inches(0.6), Inches(0.7),
                 [(num, {"style": "display_xxl", "color": n_color,
                         "size_pt": 36, "line_spacing": 1.0})])
        add_text(s, x + pad, row_y + pad + Inches(0.85),
                 card_w - pad * 2, Inches(0.4),
                 [(en, {"style": "display_sm", "color": head_color})])
        add_text(s, x + pad, row_y + pad + Inches(1.18),
                 card_w - pad * 2, Inches(0.32),
                 [(ko, {"style": "body_sm", "color": body_color})])
        add_text(s, x + pad, row_y + pad + Inches(1.55),
                 card_w - pad * 2, Inches(0.8),
                 [(body, {"style": "body_sm", "color": body_color})])

        # scope pill at bottom of card
        scope_w = Inches(1.30)
        scope_h = Inches(0.34)
        scope_x = x + (card_w - scope_w) // 2
        scope_y = row_y + card_h - pad - scope_h
        add_rounded(s, scope_x, scope_y, scope_w, scope_h,
                    fill=scope_bg, line=None, radius_ratio=0.5)
        add_text(s, scope_x, scope_y, scope_w, scope_h,
                 [(scope, {"style": "caption_b", "color": scope_text,
                           "letter_spacing_pt": 0.6})],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# slide 04 — 두 트랙 구조
# ============================================================================

def slide_two_tracks(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="STRUCTURE  ·  TWO TRACKS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("두 트랙 구조 — 같은 raw 데이터 → 두 갈래 분석",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("분석 단위는 ‘데이터의 입도’ 가 결정한다.  도로 → superblock, 관측 OD → admdong",
               {"style": "lead", "color": C.body})])

    # left column: source chips → oa_master hub → 2 branches
    diag_x = MARGIN_X
    diag_y = Inches(2.8)
    diag_w = Inches(7.2)

    # sources (3 chips stacked on the left)
    src_w = Inches(2.4)
    src_h = Inches(0.78)
    src_gap = Inches(0.10)
    src_x = diag_x
    src_y0 = diag_y

    sources = [
        ("공간 데이터",   "polygon + boundary"),
        ("SGIS 통계",    "인구·가구·주택"),
        ("LOCAL_PEOPLE","시간대 생활인구"),
    ]
    for i, (a, b) in enumerate(sources):
        y = src_y0 + (src_h + src_gap) * i
        add_rounded(s, src_x, y, src_w, src_h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(src_w, src_h, 0.18))
        add_text(s, src_x + Inches(0.22), y + Inches(0.10),
                 src_w - Inches(0.44), src_h - Inches(0.2),
                 [(a, {"style": "display_sm", "color": C.ink}),
                  (b, {"style": "body_sm", "color": C.body, "space_before": 2})])

    # hub: oa_master (centered)
    hub_w = Inches(2.0)
    hub_h = Inches(1.4)
    hub_x = src_x + src_w + Inches(0.85)
    hub_y = src_y0 + (src_h * 3 + src_gap * 2 - hub_h) // 2
    add_rounded(s, hub_x, hub_y, hub_w, hub_h, fill=C.primary, line=None,
                radius_ratio=radius_for(hub_w, hub_h, 0.21))
    add_text(s, hub_x + Inches(0.20), hub_y + Inches(0.20),
             hub_w - Inches(0.4), hub_h - Inches(0.4),
             [("OA 마스터", {"style": "display_md", "color": C.on_dark}),
              ("oa_master\n.parquet", {"style": "body_sm", "color": C.mute,
                                       "space_before": 2})])

    # arrows from sources to hub
    for i in range(3):
        y = src_y0 + (src_h + src_gap) * i + src_h // 2
        add_arrow(s, src_x + src_w + Inches(0.02), y,
                  hub_x - Inches(0.02), hub_y + hub_h // 2,
                  color=C.hairline_mid, weight_pt=1.0)

    # branches: two cards on the right
    br_x = hub_x + hub_w + Inches(0.85)
    br_w = Inches(2.55)
    br_h = Inches(1.15)
    br_gap = Inches(0.20)
    br_y0 = hub_y - (br_h + br_gap // 2 - hub_h // 2)

    branches = [
        ("Lec 3 · 4",     "admdong (426)",   "통행 수요 메인", "emphasis"),
        ("Lec 5 (부록)",   "superblock (907)","도시 형태 부록",  "outline"),
    ]
    for i, (eb, head, sub, tone) in enumerate(branches):
        y = br_y0 + (br_h + br_gap) * i
        if tone == "emphasis":
            add_rounded(s, br_x, y, br_w, br_h, fill=C.canvas, line=C.ink,
                        line_w_pt=1.25,
                        radius_ratio=radius_for(br_w, br_h, 0.18))
        else:
            add_rounded(s, br_x, y, br_w, br_h, fill=C.canvas, line=C.hairline,
                        line_w_pt=0.75,
                        radius_ratio=radius_for(br_w, br_h, 0.18))
        pad = Inches(0.22)
        add_text(s, br_x + pad, y + pad, br_w - pad * 2, Inches(0.3),
                 [(eb, {"style": "eyebrow", "color": C.body})])
        add_text(s, br_x + pad, y + pad + Inches(0.32),
                 br_w - pad * 2, Inches(0.4),
                 [(head, {"style": "display_sm", "color": C.ink})])
        add_text(s, br_x + pad, y + pad + Inches(0.68),
                 br_w - pad * 2, Inches(0.3),
                 [(sub, {"style": "body_sm", "color": C.body})])
        # arrow from hub
        add_arrow(s, hub_x + hub_w + Inches(0.02), hub_y + hub_h // 2,
                  br_x - Inches(0.02), y + br_h // 2,
                  color=C.hairline_mid, weight_pt=1.0)

    # right column: comparison row (table-like)
    tab_x = Inches(8.6)
    tab_y = Inches(2.8)
    tab_w = SLIDE_W - MARGIN_X - tab_x
    tab_h = Inches(3.6)
    add_card_content(s, tab_x, tab_y, tab_w, tab_h, radius_in=0.21)

    pad = Inches(0.35)
    add_text(s, tab_x + pad, tab_y + pad, tab_w - pad * 2, Inches(0.32),
             [("TRACK COMPARISON",
               {"style": "eyebrow", "color": C.body})])

    rows = [
        ("트랙",       "분석 단위",         "왜",              "산출"),
        ("통행 수요 메인","admdong  ·  426",   "관측 OD 단위",     "pi_aj_v1, od_matrix_v1"),
        ("도시 형태 부록","superblock  ·  907","도로 자연 경계",   "block_master.parquet"),
    ]
    rh = Inches(0.78)
    head_y = tab_y + pad + Inches(0.5)
    col_x = [tab_x + pad,
             tab_x + pad + Inches(0.95),
             tab_x + pad + Inches(2.40),
             tab_x + pad + Inches(3.55)]
    col_w = [Inches(0.95), Inches(1.45), Inches(1.15), tab_w - pad * 2 - Inches(3.55)]

    for ri, row in enumerate(rows):
        y = head_y + rh * ri
        if ri == 0:
            for ci, (c, x, w) in enumerate(zip(row, col_x, col_w)):
                add_text(s, x, y, w, Inches(0.3),
                         [(c, {"style": "eyebrow", "color": C.body})])
        else:
            add_hairline(s, tab_x + pad, y - Inches(0.06),
                         tab_w - pad * 2, color=C.hairline_soft)
            style_first = "display_sm" if ri > 0 else "body_md_b"
            for ci, (c, x, w) in enumerate(zip(row, col_x, col_w)):
                style = "display_sm" if ci == 0 else "body_sm"
                color = C.ink if ci == 0 else C.body
                add_text(s, x, y, w, Inches(0.5),
                         [(c, {"style": style, "color": color})])


# ============================================================================
# slide 05 — 공간 단위 위계
# ============================================================================

def slide_hierarchy(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="STRUCTURE  ·  SPATIAL HIERARCHY",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("서울 공간 단위 위계",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("작은 단위에서 큰 단위로 올라갈수록 코드 체계로 위계가 표현된다",
               {"style": "lead", "color": C.body})])

    # 5 layers stacked, smallest at top (parcel) → largest at bottom (sido)
    layers = [
        # (name_ko, name_en, count, role, agg_note)
        ("필지",        "parcel",     "89.9만",   "LSMD · 필지·용도지역",  "↑ centroid"),
        ("집계구",      "OA",         "19,097",  "SGIS · 통계 원자",      "↑ groupby ADM_CD[:8]"),
        ("행정동",      "admdong",    "426",     "통행 수요 단위",         "↑ groupby [:5]"),
        ("시군구",      "sgg",        "25",      "정책 단위 · KTDB TAZ",   "↑"),
        ("시도",        "sido",       "1",       "서울특별시",            "—"),
    ]

    col_x = MARGIN_X
    row_y0 = Inches(2.7)
    row_h = Inches(0.74)
    row_gap = Inches(0.10)
    table_w = Inches(8.4)

    # column header
    add_text(s, col_x, row_y0 - Inches(0.36),
             Inches(1.6), Inches(0.3),
             [("UNIT", {"style": "eyebrow", "color": C.body})])
    add_text(s, col_x + Inches(2.4), row_y0 - Inches(0.36),
             Inches(1.6), Inches(0.3),
             [("COUNT", {"style": "eyebrow", "color": C.body})])
    add_text(s, col_x + Inches(4.4), row_y0 - Inches(0.36),
             Inches(4.0), Inches(0.3),
             [("ROLE", {"style": "eyebrow", "color": C.body})])

    for i, (kr, en, cnt, role, agg) in enumerate(layers):
        y = row_y0 + (row_h + row_gap) * i
        # tone: highlight rows actually used in course (OA, admdong)
        used = en in ("OA", "admdong")
        if used:
            add_rounded(s, col_x, y, table_w, row_h, fill=C.primary, line=None,
                        radius_ratio=radius_for(table_w, row_h, 0.16))
            kr_color, en_color, body_color = C.on_dark, C.mute, C.mute
        else:
            add_rounded(s, col_x, y, table_w, row_h, fill=C.canvas_soft, line=None,
                        radius_ratio=radius_for(table_w, row_h, 0.16))
            kr_color, en_color, body_color = C.ink, C.body, C.body

        pad = Inches(0.30)
        # unit name + en code
        add_text(s, col_x + pad, y + Inches(0.10),
                 Inches(2.2), Inches(0.35),
                 [(kr, {"style": "display_sm", "color": kr_color})])
        add_text(s, col_x + pad, y + Inches(0.42),
                 Inches(2.2), Inches(0.3),
                 [(en, {"style": "body_sm", "color": en_color,
                        "code": True})])
        # count
        add_text(s, col_x + Inches(2.4), y + Inches(0.16),
                 Inches(1.8), Inches(0.5),
                 [(cnt, {"style": "display_md", "color": kr_color})])
        # role
        add_text(s, col_x + Inches(4.4), y + Inches(0.10),
                 Inches(4.0), Inches(0.32),
                 [(role, {"style": "body_md", "color": kr_color})])
        add_text(s, col_x + Inches(4.4), y + Inches(0.42),
                 Inches(4.0), Inches(0.3),
                 [(agg, {"style": "caption", "color": body_color,
                         "code": True})])

    # right column — key points
    right_x = col_x + table_w + Inches(0.40)
    right_w = SLIDE_W - MARGIN_X - right_x
    add_card_content(s, right_x, row_y0, right_w, Inches(4.3),
                     radius_in=0.21)
    pad = Inches(0.32)
    add_text(s, right_x + pad, row_y0 + pad,
             right_w - pad * 2, Inches(0.32),
             [("KEY POINTS", {"style": "eyebrow", "color": C.body})])
    bullets = [
        "상위 단위는 하위 단위의 묶음",
        "본 강좌 사용 단위 — OA(통계) · admdong(통행) · superblock(도로)",
        "⚠ admdong 코드 체계 두 종류 (행안부 vs SGIS)",
        "  → Lecture 3 에서 매핑 다룸",
    ]
    by = row_y0 + pad + Inches(0.55)
    for b in bullets:
        emphasis = b.strip().startswith("⚠")
        color = C.ink if emphasis else C.body
        style = "body_md_b" if emphasis else "body_md"
        add_text(s, right_x + pad, by,
                 right_w - pad * 2, Inches(0.6),
                 [(b, {"style": style, "color": color})])
        by += Inches(0.55)


# ============================================================================
# slide 06 — 환경 설정 + Imports
# ============================================================================

def slide_imports(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SETUP  ·  IMPORTS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("0. 환경 설정 + Imports",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("이후 모든 코드 셀은 ROOT / RAW / DRV 경로를 그대로 사용",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "import os, sys, warnings",
        "import numpy as np",
        "import pandas as pd",
        "import geopandas as gpd",
        "import matplotlib.pyplot as plt",
        "",
        "warnings.filterwarnings('ignore')",
        "%matplotlib inline",
        "plt.rcParams['figure.figsize']     = (10, 7)",
        "plt.rcParams['font.family']        = 'Malgun Gothic'",
        "plt.rcParams['axes.unicode_minus'] = False",
        "",
        "ROOT = r'F:\\research\\TAZ'",
        "RAW  = os.path.join(ROOT, 'data', 'raw')",
        "DRV  = os.path.join(ROOT, 'data', 'derived')",
        "print('OK')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.3),
                  code_lines,
                  label="cell · setup",
                  font_pt=12, line_spacing=1.20)

    # right side: notes card
    notes_x = MARGIN_X + Inches(9.1)
    notes_w = SLIDE_W - MARGIN_X - notes_x
    add_card_content(s, notes_x, Inches(2.55), notes_w, Inches(4.3),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, notes_x + pad, Inches(2.55) + pad,
             notes_w - pad * 2, Inches(0.32),
             [("NOTES", {"style": "eyebrow", "color": C.body})])

    notes = [
        ("geopandas",      "공간 데이터 — 본 강좌 핵심"),
        ("Malgun Gothic", "한글 폰트 — 안 깨지게 강제"),
        ("RAW",            "원본 데이터"),
        ("DRV",            "파생 데이터 (강좌용 사본)"),
    ]
    ny = Inches(2.55) + pad + Inches(0.5)
    for k, v in notes:
        add_text(s, notes_x + pad, ny,
                 Inches(1.4), Inches(0.32),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, notes_x + pad, ny + Inches(0.28),
                 notes_w - pad * 2, Inches(0.42),
                 [(v, {"style": "body_sm", "color": C.body})])
        ny += Inches(0.85)


# ============================================================================
# slide 07 — 좌표계 흐름
# ============================================================================

def slide_crs_flow(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="CRS  ·  FLOW",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("좌표계 (CRS) 3종 — 흐름",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("raw → 분석(5179) → 시각화(4326)  ·  to_crs(5179) 한 줄로 변환",
               {"style": "lead", "color": C.body})])

    # three columns: raw / analysis / viz
    col_y = Inches(2.95)
    col_w = Inches(3.8)
    col_h = Inches(3.4)
    gap_x = Inches(0.6)
    total_w = col_w * 3 + gap_x * 2
    start_x = (SLIDE_W - total_w) // 2

    # raw — light card with 3 sources
    raw_x = start_x
    add_rounded(s, raw_x, col_y, col_w, col_h, fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(col_w, col_h, 0.21))
    pad = Inches(0.32)
    add_text(s, raw_x + pad, col_y + pad, col_w - pad * 2, Inches(0.32),
             [("RAW  ·  원본 좌표계",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, raw_x + pad, col_y + pad + Inches(0.32),
             col_w - pad * 2, Inches(0.6),
             [("3개 소스, 2개 좌표계",
               {"style": "display_sm", "color": C.ink})])

    sources = [
        ("sgis_oa",  "EPSG:5179"),
        ("roads",    "EPSG:5179"),
        ("lsmd",     "EPSG:5186"),
    ]
    sy = col_y + pad + Inches(1.10)
    for name, epsg in sources:
        add_text(s, raw_x + pad, sy, Inches(1.4), Inches(0.28),
                 [(name, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, raw_x + pad + Inches(1.5), sy, Inches(2.0), Inches(0.28),
                 [(epsg, {"style": "body_md", "color": C.body, "code": True})])
        sy += Inches(0.40)

    # arrow 1
    arrow_y = col_y + col_h // 2
    add_arrow(s, raw_x + col_w + Inches(0.05), arrow_y,
              raw_x + col_w + gap_x - Inches(0.05), arrow_y,
              color=C.hairline_mid, weight_pt=1.5)
    add_text(s, raw_x + col_w, arrow_y - Inches(0.42),
             gap_x, Inches(0.3),
             [("to_crs(5179)", {"style": "caption_b", "color": C.body,
                                "code": True})],
             align=PP_ALIGN.CENTER)

    # analysis — emphasis (black) card
    ana_x = raw_x + col_w + gap_x
    add_rounded(s, ana_x, col_y, col_w, col_h, fill=C.primary, line=None,
                radius_ratio=radius_for(col_w, col_h, 0.21))
    add_text(s, ana_x + pad, col_y + pad, col_w - pad * 2, Inches(0.32),
             [("ANALYSIS  ·  분석 표준",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, ana_x + pad, col_y + pad + Inches(0.32),
             col_w - pad * 2, Inches(0.6),
             [("EPSG:5179",
               {"style": "display_md", "color": C.on_dark, "code": True})])
    add_text(s, ana_x + pad, col_y + pad + Inches(0.95),
             col_w - pad * 2, Inches(0.4),
             [("KGD2002 / Unified  ·  m 단위",
               {"style": "body_md", "color": C.mute})])

    notes_ana = [
        "면적 계산 m² 그대로",
        "거리 계산 m 단위",
        "버퍼·인접·교차 안정",
    ]
    ny = col_y + pad + Inches(1.65)
    for n in notes_ana:
        add_text(s, ana_x + pad, ny, col_w - pad * 2, Inches(0.32),
                 [("·  " + n, {"style": "body_md", "color": C.on_dark})])
        ny += Inches(0.36)

    # arrow 2
    add_arrow(s, ana_x + col_w + Inches(0.05), arrow_y,
              ana_x + col_w + gap_x - Inches(0.05), arrow_y,
              color=C.hairline_mid, weight_pt=1.5)
    add_text(s, ana_x + col_w, arrow_y - Inches(0.42),
             gap_x, Inches(0.3),
             [("to_crs(4326)", {"style": "caption_b", "color": C.body,
                                "code": True})],
             align=PP_ALIGN.CENTER)

    # viz — outline card
    viz_x = ana_x + col_w + gap_x
    add_rounded(s, viz_x, col_y, col_w, col_h, fill=C.canvas, line=C.hairline,
                line_w_pt=0.75,
                radius_ratio=radius_for(col_w, col_h, 0.21))
    add_text(s, viz_x + pad, col_y + pad, col_w - pad * 2, Inches(0.32),
             [("VIZ  ·  웹 시각화",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, viz_x + pad, col_y + pad + Inches(0.32),
             col_w - pad * 2, Inches(0.6),
             [("EPSG:4326",
               {"style": "display_md", "color": C.ink, "code": True})])
    add_text(s, viz_x + pad, col_y + pad + Inches(0.95),
             col_w - pad * 2, Inches(0.4),
             [("WGS84  ·  degree 단위",
               {"style": "body_md", "color": C.body})])
    notes_viz = [
        "deck.gl · leaflet · mapbox",
        "면적 계산 금지 (degree)",
        "본 강좌 viewer 입력",
    ]
    ny = col_y + pad + Inches(1.65)
    for n in notes_viz:
        add_text(s, viz_x + pad, ny, col_w - pad * 2, Inches(0.32),
                 [("·  " + n, {"style": "body_md", "color": C.body})])
        ny += Inches(0.36)


# ============================================================================
# slide 08 — 좌표계 표 + 주의사항
# ============================================================================

def slide_crs_table(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="CRS  ·  REFERENCE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("좌표계 3종 — 한 눈에",
               {"style": "display_xl", "color": C.ink})])

    # table card
    tab_x = MARGIN_X
    tab_y = Inches(2.0)
    tab_w = Inches(8.4)
    tab_h = Inches(3.6)
    add_card_content(s, tab_x, tab_y, tab_w, tab_h, radius_in=0.21)

    pad = Inches(0.35)
    cols = [
        ("EPSG",   Inches(0.0),  Inches(1.0)),
        ("이름",    Inches(1.2),  Inches(2.7)),
        ("단위",    Inches(4.1),  Inches(0.9)),
        ("용도",    Inches(5.2),  tab_w - pad * 2 - Inches(5.2)),
    ]
    head_y = tab_y + pad + Inches(0.10)
    for h, x_off, w in cols:
        add_text(s, tab_x + pad + x_off, head_y, w, Inches(0.3),
                 [(h, {"style": "eyebrow", "color": C.body})])

    rows = [
        ("5179", "KGD2002 / Unified",        "m",      "분석 표준",          True),
        ("5186", "KGD2002 / Central Belt",   "m",      "LSMD 필지 (변환 후 분석)", False),
        ("4326", "WGS84",                    "degree", "웹 시각화 전용",     False),
    ]
    rh = Inches(0.95)
    for ri, (epsg, name, unit, use, emp) in enumerate(rows):
        ry = head_y + Inches(0.45) + rh * ri
        if ri > 0:
            add_hairline(s, tab_x + pad, ry - Inches(0.08),
                         tab_w - pad * 2, color=C.hairline_soft)
        epsg_color = C.ink
        if emp:
            # add a small black pill on the right for "분석 표준" emphasis
            pill_w = Inches(1.10)
            pill_h = Inches(0.34)
            add_rounded(s, tab_x + tab_w - pad - pill_w, ry + Inches(0.10),
                        pill_w, pill_h, fill=C.primary, line=None,
                        radius_ratio=0.5)
            add_text(s, tab_x + tab_w - pad - pill_w, ry + Inches(0.10),
                     pill_w, pill_h,
                     [("STANDARD", {"style": "caption_b", "color": C.on_dark,
                                    "letter_spacing_pt": 1.0})],
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # cells
        add_text(s, tab_x + pad, ry, Inches(1.0), Inches(0.6),
                 [(epsg, {"style": "display_md", "color": epsg_color,
                          "code": True})])
        add_text(s, tab_x + pad + Inches(1.2), ry + Inches(0.06),
                 Inches(2.7), Inches(0.6),
                 [(name, {"style": "body_md_b", "color": C.ink})])
        add_text(s, tab_x + pad + Inches(4.1), ry + Inches(0.06),
                 Inches(0.9), Inches(0.6),
                 [(unit, {"style": "body_md", "color": C.body,
                          "code": True})])
        add_text(s, tab_x + pad + Inches(5.2), ry + Inches(0.06),
                 tab_w - pad * 2 - Inches(5.2) - Inches(1.3), Inches(0.6),
                 [(use, {"style": "body_md", "color": C.body})])

    # right: caveats card
    cav_x = tab_x + tab_w + Inches(0.30)
    cav_w = SLIDE_W - MARGIN_X - cav_x
    add_rounded(s, cav_x, tab_y, cav_w, tab_h, fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(cav_w, tab_h, 0.21))
    pad2 = Inches(0.30)
    add_text(s, cav_x + pad2, tab_y + pad2, cav_w - pad2 * 2, Inches(0.32),
             [("주의 · CAVEATS",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, cav_x + pad2, tab_y + pad2 + Inches(0.35),
             cav_w - pad2 * 2, Inches(0.8),
             [("WGS84(4326) 로\n면적 계산 금지",
               {"style": "display_sm", "color": C.ink})])
    add_text(s, cav_x + pad2, tab_y + pad2 + Inches(1.20),
             cav_w - pad2 * 2, Inches(0.8),
             [("degree 단위는 면적 의미 없음.\n면적·거리 → 반드시 5179 로 변환 후 계산.",
               {"style": "body_sm", "color": C.body})])
    # to_crs example
    add_code_cell(s, cav_x + pad2, tab_y + tab_h - pad2 - Inches(0.95),
                  cav_w - pad2 * 2, Inches(0.95),
                  ["gdf = gdf.to_crs(5179)",
                   "gdf['area_km2'] = gdf.area / 1e6"],
                  font_pt=10, line_spacing=1.18, padding_in=0.18)


# ============================================================================
# slide 09 — 자치구 폴리곤 (1/3) — 행정동 geojson 로딩
# ============================================================================

def slide_sgg_1(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="ADMDONG  ·  LOAD",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("자치구 폴리곤 — 가장 단순한 사례 (1/3)",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("행정동 경계 geojson 부터 시작.  서울 자치구는 행정동 dissolve 로 얻음",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "boundary = gpd.read_file(os.path.join(",
        "    RAW, 'admdong_boundary', 'admdong_2023.geojson'))",
        "",
        "seoul_admdong = boundary[",
        "    boundary['sidonm'].str.contains('서울', na=False)",
        "].copy()",
        "",
        "print(f'서울 행정동 : {len(seoul_admdong)}')",
        "print(f'CRS         : {seoul_admdong.crs}')",
        "print(f'컬럼        : {list(seoul_admdong.columns)}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(3.7),
                  code_lines, label="cell · load admdong",
                  font_pt=12, line_spacing=1.22)

    # right: expected output
    out_x = MARGIN_X + Inches(9.1)
    out_w = SLIDE_W - MARGIN_X - out_x
    add_rounded(s, out_x, Inches(2.55), out_w, Inches(3.7),
                fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(out_w, Inches(3.7), 0.21))
    pad = Inches(0.30)
    add_text(s, out_x + pad, Inches(2.55) + pad,
             out_w - pad * 2, Inches(0.32),
             [("EXPECTED OUTPUT", {"style": "eyebrow", "color": C.body})])
    out_lines = [
        "서울 행정동 : 426",
        "CRS         : EPSG:4326",
        "컬럼        :",
        "  ['sidonm',",
        "   'sggnm',",
        "   'admnm',",
        "   'adm_cd2',",
        "   'geometry']",
    ]
    ly = Inches(2.55) + pad + Inches(0.55)
    for line in out_lines:
        add_text(s, out_x + pad, ly,
                 out_w - pad * 2, Inches(0.28),
                 [(line, {"style": "body_sm", "color": C.ink,
                          "code": True})])
        ly += Inches(0.32)


# ============================================================================
# slide 10 — 자치구 폴리곤 (2/3) — 5179 변환 + 면적
# ============================================================================

def slide_sgg_2(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="ADMDONG  ·  AREA",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("자치구 폴리곤 (2/3) — 좌표 변환 + 면적",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("4326 → 5179 변환 후 .area / 1e6 으로 km² 계산",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "seoul_admdong = seoul_admdong.to_crs(5179)",
        "seoul_admdong['area_km2'] = seoul_admdong.geometry.area / 1e6",
        "",
        "print(f'서울 총 면적 : {seoul_admdong[\"area_km2\"].sum():.1f} km²')",
        "print('행정동 면적 통계 (km²):')",
        "print(seoul_admdong['area_km2'].describe().round(2))",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(2.6),
                  code_lines, label="cell · to_crs + area",
                  font_pt=12, line_spacing=1.22)

    # output card
    out_lines = [
        "서울 총 면적 : 605.2 km²",
        "행정동 면적 통계 (km²):",
        "count     426.00",
        "mean        1.42",
        "std         1.16",
        "min         0.13",
        "50%         1.07",
        "max         9.06",
    ]
    add_code_cell(s, MARGIN_X, Inches(5.30),
                  Inches(8.8), Inches(1.95),
                  out_lines, label="output",
                  font_pt=11, line_spacing=1.22)

    # right: explanation
    exp_x = MARGIN_X + Inches(9.1)
    exp_w = SLIDE_W - MARGIN_X - exp_x
    add_card_content(s, exp_x, Inches(2.55), exp_w, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.32)
    add_text(s, exp_x + pad, Inches(2.55) + pad,
             exp_w - pad * 2, Inches(0.32),
             [("WHY 5179", {"style": "eyebrow", "color": C.body})])
    add_text(s, exp_x + pad, Inches(2.55) + pad + Inches(0.45),
             exp_w - pad * 2, Inches(0.75),
             [("4326 단위는\ndegree — 면적 의미 없음",
               {"style": "display_sm", "color": C.ink,
                "line_spacing": 1.25})])
    add_text(s, exp_x + pad, Inches(2.55) + pad + Inches(1.45),
             exp_w - pad * 2, Inches(1.6),
             [("EPSG:5179 는 KGD2002 단일평면 좌표계로\n"
               "단위가 m. geometry.area 가 m² 로 나와,\n"
               "/ 1e6 만 하면 km² 가 됨.",
               {"style": "body_sm", "color": C.body})])
    add_text(s, exp_x + pad, Inches(2.55) + pad + Inches(3.20),
             exp_w - pad * 2, Inches(1.0),
             [("→ 서울 총 면적 605.2 km².\n"
               "  공식 자료(605.21) 와 일치.",
               {"style": "body_sm", "color": C.ink})])


# ============================================================================
# slide 11 — 자치구 폴리곤 (3/3) — dissolve + 시각화
# ============================================================================

def slide_sgg_3(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="ADMDONG  ·  DISSOLVE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("자치구 폴리곤 (3/3) — dissolve + 시각화",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("행정동 → 자치구 dissolve  ·  matplotlib choropleth 기본 패턴",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "sgg = seoul_admdong.dissolve(",
        "    by='sggnm', as_index=False,",
        "    aggfunc={'area_km2': 'sum'})",
        "print(f'서울 자치구 : {len(sgg)}')",
        "",
        "fig, ax = plt.subplots(figsize=(11, 9))",
        "sgg.plot(column='area_km2', ax=ax, cmap='YlOrRd',",
        "         edgecolor='white', linewidth=1.5, legend=True,",
        "         legend_kwds={'label': '면적 (km²)', 'shrink': 0.6})",
        "",
        "for _, row in sgg.iterrows():",
        "    pt = row.geometry.representative_point()",
        "    ax.annotate(row['sggnm'], (pt.x, pt.y), fontsize=8, ha='center')",
        "",
        "ax.set_title('서울 25개 자치구 — 면적 분포')",
        "ax.set_axis_off(); plt.show()",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · dissolve + plot",
                  font_pt=11, line_spacing=1.18)

    # right: 3 step cards
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("STEPS", {"style": "eyebrow", "color": C.body})])
    steps = [
        ("1", "dissolve(by='sggnm')",      "행정동 426 → 자치구 25 로 합침"),
        ("2", "cmap='YlOrRd'",             "면적 → 색상 매핑 (연속형)"),
        ("3", "representative_point",      "라벨 배치 — centroid 외곽 보정"),
    ]
    sy = Inches(2.55) + pad + Inches(0.5)
    for num, code, desc in steps:
        add_text(s, nx + pad, sy, Inches(0.4), Inches(0.5),
                 [(num, {"style": "display_md", "color": C.ink})])
        add_text(s, nx + pad + Inches(0.4), sy,
                 nw - pad * 2 - Inches(0.4), Inches(0.32),
                 [(code, {"style": "body_sm_b", "color": C.ink,
                          "code": True})])
        add_text(s, nx + pad + Inches(0.4), sy + Inches(0.30),
                 nw - pad * 2 - Inches(0.4), Inches(0.6),
                 [(desc, {"style": "body_sm", "color": C.body})])
        sy += Inches(1.30)


# ============================================================================
# slide 12 — 집계구 OA + 14자리 코드
# ============================================================================

def slide_oa_intro(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA  ·  INTRO",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("집계구 (OA) — 통계의 원자",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("SGIS 가 발급하는 가장 작은 인구 통계 단위 (Output Area)",
               {"style": "lead", "color": C.body})])

    # left: bullets + counts
    left_x = MARGIN_X
    left_w = Inches(5.6)
    add_card_content(s, left_x, Inches(2.55), left_w, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.42)

    add_text(s, left_x + pad, Inches(2.55) + pad,
             left_w - pad * 2, Inches(0.32),
             [("WHAT IS OA", {"style": "eyebrow", "color": C.body})])
    add_text(s, left_x + pad, Inches(2.55) + pad + Inches(0.40),
             left_w - pad * 2, Inches(1.1),
             [("Output Area",
               {"style": "display_lg", "color": C.ink, "code": True})])
    add_text(s, left_x + pad, Inches(2.55) + pad + Inches(1.50),
             left_w - pad * 2, Inches(2.5),
             [("• 통계청 SGIS 발급, 가장 작은 인구 통계 단위",
               {"style": "body_md", "color": C.body}),
              ("• 서울 = 19,097개",
               {"style": "body_md", "color": C.body, "space_before": 4}),
              ("• 모든 인구·가구·주택 통계가 OA 단위로 공개",
               {"style": "body_md", "color": C.body, "space_before": 4}),
              ("• 본 강좌 Lecture 2 ‘OA 마스터’ 의 기준 단위",
               {"style": "body_md_b", "color": C.ink, "space_before": 4})])

    # right: 14-digit code anatomy
    right_x = left_x + left_w + Inches(0.30)
    right_w = SLIDE_W - MARGIN_X - right_x
    add_rounded(s, right_x, Inches(2.55), right_w, Inches(4.7),
                fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(right_w, Inches(4.7), 0.21))
    pad = Inches(0.32)
    add_text(s, right_x + pad, Inches(2.55) + pad,
             right_w - pad * 2, Inches(0.32),
             [("CODE ANATOMY  ·  14 DIGITS",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, right_x + pad, Inches(2.55) + pad + Inches(0.30),
             right_w - pad * 2, Inches(0.5),
             [("ADM_CD = 11010530010001",
               {"style": "display_sm", "color": C.ink, "code": True})])

    # digit segments — 4 boxes
    seg_y = Inches(2.55) + pad + Inches(1.10)
    segs = [
        ("11",     "시도",     Inches(0.55)),
        ("010",    "시군구",   Inches(0.78)),
        ("530",    "동",       Inches(0.78)),
        ("010001", "일련번호", Inches(1.45)),
    ]
    seg_total_w = sum((w for _, _, w in segs), Emu(0)) + Inches(0.10) * 3
    seg_x = right_x + (right_w - seg_total_w) // 2
    for digits, label, w in segs:
        # box
        add_rounded(s, seg_x, seg_y, w, Inches(0.74),
                    fill=C.canvas, line=C.hairline, line_w_pt=0.75,
                    radius_ratio=radius_for(w, Inches(0.74), 0.15))
        add_text(s, seg_x, seg_y, w, Inches(0.74),
                 [(digits, {"style": "display_md", "color": C.ink, "code": True})],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # label below
        add_text(s, seg_x, seg_y + Inches(0.80), w, Inches(0.3),
                 [(label, {"style": "body_sm", "color": C.body})],
                 align=PP_ALIGN.CENTER)
        seg_x += w + Inches(0.10)

    # ADM_CD[:8] bracket underneath
    bracket_y = seg_y + Inches(1.30)
    seg_x = right_x + (right_w - seg_total_w) // 2
    bracket_w = segs[0][2] + segs[1][2] + segs[2][2] + Inches(0.20)
    add_rounded(s, seg_x, bracket_y, bracket_w, Inches(0.46),
                fill=C.primary, line=None,
                radius_ratio=radius_for(bracket_w, Inches(0.46), 0.21))
    add_text(s, seg_x, bracket_y, bracket_w, Inches(0.46),
             [("ADM_CD[:8]  ·  행정동 코드", {"style": "caption_b", "color": C.on_dark,
                                       "letter_spacing_pt": 0.8})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, right_x + pad, bracket_y + Inches(0.60),
             right_w - pad * 2, Inches(0.5),
             [("→ ADM_CD 앞 8자리 grouping 으로\n  OA(19,097) → admdong(426) 집계 가능",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 13 — OA 폴리곤 로딩
# ============================================================================

def slide_oa_load(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA  ·  LOAD",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("OA 폴리곤 로딩",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("19,097 폴리곤 shapefile.  CP949 인코딩 + time it",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "import time",
        "t0 = time.time()",
        "oa = gpd.read_file(",
        "    os.path.join(RAW, 'sgis_oa', 'bnd_oa_11_2025_2Q.shp'),",
        "    encoding='cp949')",
        "print(f'로딩 시간 : {time.time() - t0:.1f}s')",
        "print(f'OA 수     : {len(oa)}')",
        "print(f'컬럼      : {list(oa.columns)}')",
        "oa.head(3)",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(3.6),
                  code_lines, label="cell · load oa shapefile",
                  font_pt=12, line_spacing=1.22)

    out_lines = [
        "로딩 시간 : 5.8s   ·   OA 수 : 19,097",
        "컬럼      : ['TOT_OA_CD', 'ADM_CD', 'BASE_YEAR', 'geometry']",
    ]
    add_code_cell(s, MARGIN_X, Inches(6.30),
                  Inches(8.8), Inches(0.95),
                  out_lines,
                  label="output", font_pt=10, line_spacing=1.20)

    # right: caveats / shapefile notes
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("WHY ENCODING", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.40),
             nw - pad * 2, Inches(0.8),
             [("CP949",
               {"style": "display_md", "color": C.ink, "code": True})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(1.30),
             nw - pad * 2, Inches(2.5),
             [("SGIS 가 배포하는 shapefile 의 .dbf 는\nCP949(MS949) 인코딩.",
               {"style": "body_sm", "color": C.body}),
              ("\nUTF-8 로 열면 한글 컬럼명 깨짐.\n\n"
               "→ 한글 raw 데이터는 일단 cp949 시도, "
               "그래도 깨지면 euc-kr.",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 14 — OA 면적 분포
# ============================================================================

def slide_oa_area(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA  ·  AREA DISTRIBUTION",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("OA 면적 분포",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("인구 단위 — 도심은 작고 외곽은 큼.  log-scale 히스토그램으로 확인",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "oa['area_m2'] = oa.geometry.area",
        "print(f'면적 (m²)')",
        "print(f'  median : {oa[\"area_m2\"].median():>10,.0f}')",
        "print(f'  p10    : {oa[\"area_m2\"].quantile(0.1):>10,.0f}')",
        "print(f'  p90    : {oa[\"area_m2\"].quantile(0.9):>10,.0f}')",
        "print(f'  max    : {oa[\"area_m2\"].max():>10,.0f}')",
        "",
        "fig, ax = plt.subplots(figsize=(10, 4))",
        "ax.hist(np.log10(oa['area_m2']), bins=60,",
        "        color='steelblue', edgecolor='white')",
        "ax.set_xlabel('log10(area m²)')",
        "ax.set_ylabel('OA 개수')",
        "ax.set_title('서울 OA 면적 분포 — 도심 작고 외곽 큼')",
        "ax.grid(alpha=0.3, axis='y'); plt.show()",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · oa area distribution",
                  font_pt=11, line_spacing=1.18)

    # right: stats card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(2.0),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("EXPECTED STATS", {"style": "eyebrow", "color": C.body})])
    stats = [("median", "  13,500 m²"),
             ("p10",    "   4,200 m²"),
             ("p90",    "  60,500 m²"),
             ("max",    "1,800,000 m²")]
    sy = Inches(2.55) + pad + Inches(0.30)
    for k, v in stats:
        add_text(s, nx + pad, sy, Inches(0.9), Inches(0.28),
                 [(k, {"style": "body_sm_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad + Inches(0.95), sy,
                 nw - pad * 2 - Inches(0.95), Inches(0.28),
                 [(v, {"style": "body_sm", "color": C.body, "code": True})])
        sy += Inches(0.28)

    # right bottom: why log
    add_rounded(s, nx, Inches(4.75), nw, Inches(2.5),
                fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(nw, Inches(2.5), 0.21))
    add_text(s, nx + pad, Inches(4.75) + pad,
             nw - pad * 2, Inches(0.32),
             [("WHY log10", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(4.75) + pad + Inches(0.35),
             nw - pad * 2, Inches(1.6),
             [("OA 면적은 4자리수 차이.\n"
               "선형 히스토그램에 그리면 외곽 큰 OA 가\n"
               "오른쪽 tail 로 길게 늘어져 분포 모양이\n안 보임.\n"
               "log10 으로 정규성에 가깝게.",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 15 — 종로구 OA 시각화
# ============================================================================

def slide_oa_jongno(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA  ·  JONGNO",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("한 자치구만 — 종로구 OA",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("ADM_CD 앞 5자리(시군구) 필터로 종로구(11010) 만 추출",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "jongno_oa = oa[oa['ADM_CD'].astype(str).str[:5] == '11010']",
        "print(f'종로구 OA : {len(jongno_oa)}')",
        "",
        "fig, ax = plt.subplots(figsize=(12, 10))",
        "jongno_oa.plot(ax=ax,",
        "    color='lightblue', edgecolor='steelblue',",
        "    linewidth=0.4)",
        "ax.set_title(f'종로구 OA — {len(jongno_oa)}개')",
        "ax.set_axis_off(); plt.show()",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(3.0),
                  code_lines, label="cell · filter + plot",
                  font_pt=12, line_spacing=1.22)

    # output
    add_code_cell(s, MARGIN_X, Inches(5.70),
                  Inches(8.8), Inches(0.7),
                  ["종로구 OA : 388"],
                  label="output", font_pt=11, line_spacing=1.18)

    # right: pattern hint
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("PATTERN", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.35),
             nw - pad * 2, Inches(0.7),
             [("ADM_CD\nslicing",
               {"style": "display_md", "color": C.ink, "line_spacing": 1.15})])

    slice_tab = [
        ("[:2]", "시도",     "11"),
        ("[:5]", "시군구",   "11010"),
        ("[:8]", "행정동",   "11010530"),
        ("[:14]","OA 일련",  "11010530010001"),
    ]
    sy = Inches(2.55) + pad + Inches(1.50)
    for sl, label, ex in slice_tab:
        add_text(s, nx + pad, sy, Inches(0.85), Inches(0.28),
                 [(sl, {"style": "body_sm_b", "color": C.ink,
                        "code": True})])
        add_text(s, nx + pad + Inches(0.85), sy,
                 Inches(1.1), Inches(0.28),
                 [(label, {"style": "body_sm", "color": C.body})])
        add_text(s, nx + pad + Inches(1.95), sy,
                 nw - pad * 2 - Inches(1.95), Inches(0.28),
                 [(ex, {"style": "body_sm", "color": C.body, "code": True})])
        sy += Inches(0.42)


# ============================================================================
# slide 16 — 필지 LSMD 개요 (bbox 스트리밍 이유)
# ============================================================================

def slide_parcel_intro(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="PARCEL  ·  LSMD",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("필지 — LSMD zone_class",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("89.9만 필지를 한꺼번에 그릴 수 없다 — bbox 스트리밍이 합리적",
               {"style": "lead", "color": C.body})])

    # left: 3 stats cards stacked horizontally
    stat_y = Inches(2.6)
    stat_h = Inches(1.6)
    sw = Inches(2.85)
    sgap = Inches(0.20)
    sx0 = MARGIN_X
    stats = [
        ("원본",      "1.5 GB",         "LSMD · EPSG:5186"),
        ("강좌용 사본","322 MB",        "seoul_parcels.fgb · 4326"),
        ("필지 수",   "89.9만",         "11 종 zone_class 라벨 완료"),
    ]
    for i, (k, v, sub) in enumerate(stats):
        x = sx0 + (sw + sgap) * i
        add_rounded(s, x, stat_y, sw, stat_h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(sw, stat_h, 0.21))
        pad = Inches(0.25)
        add_text(s, x + pad, stat_y + pad, sw - pad * 2, Inches(0.3),
                 [(k, {"style": "eyebrow", "color": C.body})])
        add_text(s, x + pad, stat_y + pad + Inches(0.32),
                 sw - pad * 2, Inches(0.6),
                 [(v, {"style": "display_lg", "color": C.ink})])
        add_text(s, x + pad, stat_y + pad + Inches(0.95),
                 sw - pad * 2, Inches(0.5),
                 [(sub, {"style": "body_sm", "color": C.body})])

    # right of stats: dark promo card with 'WHY bbox streaming'
    pr_x = sx0 + (sw + sgap) * 3
    pr_w = SLIDE_W - MARGIN_X - pr_x
    add_rounded(s, pr_x, stat_y, pr_w, stat_h, fill=C.primary, line=None,
                radius_ratio=radius_for(pr_w, stat_h, 0.21))
    pad = Inches(0.32)
    add_text(s, pr_x + pad, stat_y + pad, pr_w - pad * 2, Inches(0.32),
             [("WHY BBOX STREAMING", {"style": "eyebrow", "color": C.mute})])
    add_text(s, pr_x + pad, stat_y + pad + Inches(0.40),
             pr_w - pad * 2, Inches(1.0),
             [("전체 그리면 검정 화면\n샘플은 너무 듬성",
               {"style": "display_sm", "color": C.on_dark,
                "line_spacing": 1.30})])

    # below: 3 reason cards (bbox vs full vs sample)
    rs_y = stat_y + stat_h + Inches(0.30)
    rs_h = Inches(2.1)
    rs_items = [
        ("전체 로딩", "89.9만 필지 — 화면 검어짐 + IO 4~6초",
         "outline"),
        ("preview 샘플", "1,000개 — 듬성, 분석 불가",
         "outline"),
        ("BBOX 스트리밍", "FlatGeobuf spatial index 활용\n→ 자치구 하나만 디스크에서 읽음",
         "emphasis"),
    ]
    rs_w = (CONTENT_W - sgap * 2) // 3
    for i, (head, body, tone) in enumerate(rs_items):
        x = MARGIN_X + (rs_w + sgap) * i
        if tone == "emphasis":
            add_rounded(s, x, rs_y, rs_w, rs_h, fill=C.primary, line=None,
                        radius_ratio=radius_for(rs_w, rs_h, 0.21))
            hc, bc, eb = C.on_dark, C.mute, C.mute
        else:
            add_rounded(s, x, rs_y, rs_w, rs_h, fill=C.canvas, line=C.hairline,
                        line_w_pt=0.75,
                        radius_ratio=radius_for(rs_w, rs_h, 0.21))
            hc, bc, eb = C.ink, C.body, C.body
        pad = Inches(0.28)
        eb_label = "FAIL" if tone == "outline" else "OK"
        eb_color = C.mute if tone == "outline" else C.mute
        # small badge
        bw = Inches(0.5); bh = Inches(0.32)
        bg = C.canvas_soft if tone == "outline" else C.canvas
        bt = C.body if tone == "outline" else C.ink
        add_rounded(s, x + rs_w - pad - bw, rs_y + pad,
                    bw, bh, fill=bg, line=None, radius_ratio=0.5)
        add_text(s, x + rs_w - pad - bw, rs_y + pad, bw, bh,
                 [(eb_label, {"style": "caption_b", "color": bt,
                              "letter_spacing_pt": 0.8})],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

        add_text(s, x + pad, rs_y + pad,
                 rs_w - pad * 2 - bw, Inches(0.7),
                 [(head, {"style": "display_sm", "color": hc})])
        add_text(s, x + pad, rs_y + pad + Inches(0.85),
                 rs_w - pad * 2, rs_h - pad * 2 - Inches(0.85),
                 [(body, {"style": "body_sm", "color": bc})])


# ============================================================================
# slide 17 — 필지 bbox 스트리밍 (코드)
# ============================================================================

def slide_parcel_stream(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="PARCEL  ·  BBOX STREAM",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("필지 bbox 스트리밍 — 종로구만 풀 필지",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("FGB spatial index 가 디스크에서 bbox 영역만 읽어옴 (322 MB 전부 안 읽음)",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "# parcels.fgb 는 EPSG:4326 이므로 bbox 도 4326 으로",
        "jongno_bbox_4326 = tuple(jongno_oa.to_crs(4326).total_bounds)",
        "",
        "t0 = time.time()",
        "parcels = gpd.read_file(",
        "    os.path.join(DRV, 'seoul_parcels.fgb'),",
        "    bbox=jongno_bbox_4326)",
        "print(f'로딩 시간     : {time.time() - t0:.1f}s')",
        "print(f'bbox 내 필지  : {len(parcels):,}')",
        "",
        "# 5179 로 분석 변환 + 종로구 경계로 클립 (사각형 → 폴리곤)",
        "parcels = parcels.to_crs(5179)",
        "jongno_union = jongno_oa.geometry.union_all()",
        "parcels = parcels[parcels.geometry.within(jongno_union)].copy()",
        "print(f'종로구 안 필지: {len(parcels):,}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · bbox stream + clip",
                  font_pt=11, line_spacing=1.18)

    # right: flow card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("FLOW", {"style": "eyebrow", "color": C.body})])

    flow_steps = [
        ("1", "bbox 계산", "jongno_oa 의 total_bounds — 4326 좌표"),
        ("2", "FGB read", "spatial index 로 영역 안만 디스크 read"),
        ("3", "to_crs", "5179 로 분석 표준 변환"),
        ("4", "clip", "bbox 는 사각형 → 종로구 폴리곤으로 클립"),
    ]
    fy = Inches(2.55) + pad + Inches(0.45)
    for num, head, body in flow_steps:
        add_text(s, nx + pad, fy, Inches(0.35), Inches(0.6),
                 [(num, {"style": "display_md", "color": C.ink})])
        add_text(s, nx + pad + Inches(0.4), fy,
                 nw - pad * 2 - Inches(0.4), Inches(0.28),
                 [(head, {"style": "body_md_b", "color": C.ink})])
        add_text(s, nx + pad + Inches(0.4), fy + Inches(0.25),
                 nw - pad * 2 - Inches(0.4), Inches(0.6),
                 [(body, {"style": "body_sm", "color": C.body})])
        fy += Inches(1.00)


# ============================================================================
# slide 18 — zone_class 분포 + 색상 매핑
# ============================================================================

def slide_zoneclass_palette(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="PARCEL  ·  ZONE CLASS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("zone_class 분포 + 색상 팔레트",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("blocks/aggregate_landuse.py LU_COLOR 와 동일 톤 — RGB 0-255 → matplotlib 0-1",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "# 종로구 zone_class 분포",
        "print('종로구 zone_class top 10:')",
        "print(parcels['zone_class'].value_counts().head(10))",
        "",
        "from matplotlib.patches import Patch",
        "ZONE_COLOR = {",
        "    '전용주거':           (1.00, 0.90, 0.60),",
        "    '일반주거_저밀(1종)': (1.00, 0.78, 0.47),",
        "    '일반주거_중밀(2종)': (1.00, 0.65, 0.31),",
        "    '일반주거_고밀(3종)': (0.88, 0.47, 0.20),",
        "    '준주거':            (0.78, 0.35, 0.39),",
        "    '중심·일반상업':     (0.86, 0.24, 0.24),",
        "    '근린·유통상업':     (0.94, 0.43, 0.55),",
        "    '일반·준공업':       (0.59, 0.43, 0.86),",
        "    '보전·자연녹지':     (0.43, 0.71, 0.43),",
        "    '생산녹지':          (0.63, 0.82, 0.39),",
        "}",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · zone palette",
                  font_pt=10, line_spacing=1.20)

    # right: color swatches preview
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("PALETTE PREVIEW", {"style": "eyebrow", "color": C.body})])

    from pptx.dml.color import RGBColor
    swatches = [
        ("전용주거",         (0xFF, 0xE5, 0x99)),
        ("일주_저(1종)",     (0xFF, 0xC7, 0x77)),
        ("일주_중(2종)",     (0xFF, 0xA6, 0x4F)),
        ("일주_고(3종)",     (0xE0, 0x78, 0x33)),
        ("준주거",          (0xC7, 0x59, 0x63)),
        ("중심·일반상업",   (0xDB, 0x3D, 0x3D)),
        ("근린·유통상업",   (0xF0, 0x6E, 0x8C)),
        ("일반·준공업",     (0x97, 0x6E, 0xDB)),
        ("보전·자연녹지",   (0x6E, 0xB5, 0x6E)),
        ("생산녹지",        (0xA1, 0xD1, 0x63)),
    ]
    sy = Inches(2.55) + pad + Inches(0.45)
    for label, (r, g, b) in swatches:
        # swatch box
        add_rounded(s, nx + pad, sy, Inches(0.32), Inches(0.32),
                    fill=RGBColor(r, g, b), line=None,
                    radius_ratio=0.18)
        add_text(s, nx + pad + Inches(0.42), sy + Inches(0.02),
                 nw - pad * 2 - Inches(0.42), Inches(0.3),
                 [(label, {"style": "body_sm", "color": C.ink})])
        sy += Inches(0.36)


# ============================================================================
# slide 19 — zone_class choropleth
# ============================================================================

def slide_zoneclass_plot(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="PARCEL  ·  CHOROPLETH",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("zone_class choropleth — 11클래스 색칠",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("PatchCollection 자동 legend 못 잡음 → Patch 핸들 수동 생성",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "fig, ax = plt.subplots(figsize=(12, 11))",
        "handles = []   # 자동 legend 매칭 안됨 → 핸들 수동",
        "for cls, color in ZONE_COLOR.items():",
        "    sub = parcels[parcels['zone_class'] == cls]",
        "    if not len(sub): continue",
        "    sub.plot(ax=ax, color=color,",
        "             edgecolor='white', linewidth=0.05)",
        "    handles.append(Patch(facecolor=color, edgecolor='white',",
        "                         label=f'{cls} ({len(sub):,})'))",
        "",
        "# 종로구 외곽선",
        "jongno_oa.dissolve().boundary.plot(",
        "    ax=ax, color='black', linewidth=0.6)",
        "",
        "ax.legend(handles=handles, loc='lower right',",
        "          fontsize=8, framealpha=0.9)",
        "ax.set_title(f'종로구 — LSMD 필지 {len(parcels):,}개 × zone_class')",
        "ax.set_axis_off(); plt.show()",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · zone_class choropleth",
                  font_pt=10, line_spacing=1.20)

    # right: notes
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("PATTERN NOTES", {"style": "eyebrow", "color": C.body})])
    notes = [
        ("loop per class",
         "각 zone_class 마다 sub.plot 호출 — 동일 색·라인 일관성"),
        ("legend handles",
         "PatchCollection 은 자동 legend 매칭 못해서\nPatch 객체로 직접 만들어 list 에 append"),
        ("외곽선 overlay",
         "dissolve().boundary 로 자치구 경계만 검정선으로\n위에 한 번 더 plot"),
        ("linewidth 0.05",
         "필지 간 흰 hairline — 너무 두꺼우면 색이 가려짐"),
    ]
    ny = Inches(2.55) + pad + Inches(0.45)
    for k, v in notes:
        add_text(s, nx + pad, ny, nw - pad * 2, Inches(0.32),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad, ny + Inches(0.28),
                 nw - pad * 2, Inches(0.8),
                 [(v, {"style": "body_sm", "color": C.body})])
        ny += Inches(0.95)


# ============================================================================
# slide 20 — 정리 + 다음 강의
# ============================================================================

def slide_summary(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SUMMARY  ·  RECAP",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("정리 — Lecture 1 에서 챙길 5가지",
               {"style": "display_xl", "color": C.ink})])

    # 5 takeaway cards in a row
    row_y = Inches(2.2)
    card_w = (CONTENT_W - Inches(0.2) * 4) // 5
    card_h = Inches(2.6)
    cards = [
        ("1", "4단계 모형",       "본 강좌 = 1·2단계\n(Generation · Distribution)"),
        ("2", "두 트랙",          "메인 — admdong(426)\n부록 — superblock(907)"),
        ("3", "공간 위계",        "필지(89만) ↑ OA(1.9만)\n↑ admdong(426) ↑ 시군구(25)"),
        ("4", "좌표계",          "EPSG:5179 분석 표준 (m)\n4326 시각화 전용 (degree)"),
        ("5", "geopandas",      "read_file · to_crs · area\ndissolve · plot"),
    ]
    for i, (num, head, body) in enumerate(cards):
        x = MARGIN_X + (card_w + Inches(0.2)) * i
        add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(card_w, card_h, 0.21))
        pad = Inches(0.22)
        add_text(s, x + pad, row_y + pad, card_w - pad * 2, Inches(0.5),
                 [(num, {"style": "display_lg", "color": C.mute})])
        add_text(s, x + pad, row_y + pad + Inches(0.55),
                 card_w - pad * 2, Inches(0.5),
                 [(head, {"style": "display_sm", "color": C.ink})])
        add_text(s, x + pad, row_y + pad + Inches(1.10),
                 card_w - pad * 2, Inches(1.4),
                 [(body, {"style": "body_sm", "color": C.body})])

    # bottom: black promo card pointing to Lec2
    pr_y = Inches(5.20)
    pr_h = Inches(1.7)
    add_card_dark(s, MARGIN_X, pr_y, CONTENT_W, pr_h, radius_in=0.21)
    pad = Inches(0.5)
    add_text(s, MARGIN_X + pad, pr_y + pad, Inches(2.5), Inches(0.32),
             [("NEXT  ·  LECTURE 02",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, MARGIN_X + pad, pr_y + pad + Inches(0.3),
             Inches(9), Inches(0.7),
             [("OA 마스터 구축 — SGIS 통계 + LOCAL_PEOPLE 시간대 생활인구 통합",
               {"style": "display_md", "color": C.on_dark})])
    # pill button on right
    btn_w = Inches(2.4); btn_h = Inches(0.55)
    btn_x = MARGIN_X + CONTENT_W - pad - btn_w
    btn_y = pr_y + (pr_h - btn_h) // 2
    add_rounded(s, btn_x, btn_y, btn_w, btn_h, fill=C.canvas, line=None,
                radius_ratio=0.5)
    add_text(s, btn_x, btn_y, btn_w, btn_h,
             [("Open Lecture 02  →", {"style": "button", "color": C.ink})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# main
# ============================================================================

def build():
    prs = Presentation()
    setup_169(prs)

    slides = [
        slide_title,
        slide_course_flow,
        slide_4step_model,
        slide_two_tracks,
        slide_hierarchy,
        slide_imports,
        slide_crs_flow,
        slide_crs_table,
        slide_sgg_1,
        slide_sgg_2,
        slide_sgg_3,
        slide_oa_intro,
        slide_oa_load,
        slide_oa_area,
        slide_oa_jongno,
        slide_parcel_intro,
        slide_parcel_stream,
        slide_zoneclass_palette,
        slide_zoneclass_plot,
        slide_summary,
    ]
    total = len(slides)

    for i, fn in enumerate(slides, start=1):
        fn(prs, i, total)

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "slides", "01_spatial_data.pptx",
    )
    prs.save(out)
    print(f"OK · {total} slides · {out}")
    return out


if __name__ == "__main__":
    build()
