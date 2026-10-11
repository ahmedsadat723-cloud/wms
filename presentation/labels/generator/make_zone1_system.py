#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Al-Munajem DRY SECTION — PART 1 : rack-level letter system (v1, bilingual AR/EN)
  1. distribution method (written) + linear colour scale of the racks (one rack = one equal length)
  2. rack distribution tables (A1 cartons · A2 plastic · A3 boxes · A4 supplies)
  3. rack-level LETTER stickers (A–E only, brand colour band, arrows) — no pallet numbers on the racks
  4. PALLET LABEL sheets (one paper per pallet, brand colours) — fillable PDF + HTML
usage: python3 make_zone1_system.py <out_dir>      (then render_pdf.py for the PDFs, add_widgets.py for the fillable one)
"""
import os, sys, html, base64
import make_stickers as m
from make_stickers import TYPES, LETTERS, build_racks, overlay, arrow, font_css, FIT_JS

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION, DATE = 'v3', '2026-10-11'
LOGO = os.path.join(HERE, 'assets', 'almunajem_logo.png')
esc = html.escape
INK, YEL = '#111111', '#FFD400'

# one palette for everything new = the colours of the pallet label paper supplied by Ahmed
BR = {'DX': ('DOUX', 'دو', '#1F5FA8'), 'DR': ('DARI', 'داري', '#C62828'), 'HB': ('AL HABRA', 'الهبرة', '#7A4A2B'),
      'SA': ('SAUDI', 'السعودي', '#2E7D32'), 'GN': ('GENERAL', 'عام', '#3D5563'), 'SP': ('SPARE', 'احتياطي', '#777777')}
ORDER = ['DX', 'DR', 'HB', 'SA', 'GN', 'SP']
ZONE_TXT = {  # where each category lives (from the dry-room plan / earlier agreed layout)
    'c': ('Zone 3 · Left · tall rack 246 cm', 'المنطقة 3 · اليسار · الراك العالي 246 سم'),
    'p': ('Zone 1 · Right', 'المنطقة 1 · اليمين'),
    'b': ('Zone 1 · Left', 'المنطقة 1 · اليسار'),
    'a': ('Zone 1 · Left · after the boxes', 'المنطقة 1 · اليسار · بعد علب التعبئة'),
}

def bil(en, ar, sz_en, sz_ar=None, w=800, col=None, gap=1.5):
    """one bilingual line: Arabic on the right, English on the left (screen/print safe)"""
    c = ';color:%s' % col if col else ''
    return ('<div style="display:flex;justify-content:space-between;align-items:baseline;gap:%smm%s">'
            '<span dir="ltr" style="font-size:%smm;font-weight:%s">%s</span>'
            '<span dir="rtl" style="font-size:%smm;font-weight:%s">%s</span></div>' % (gap, c, sz_en, w, en, sz_ar or sz_en, w, ar))

# ------------------------------------------------------------------ css
def css():
    return (font_css() + ':root{--logo:url(%s)}' % logo_uri() + """
@page port{size:210mm 297mm;margin:0}@page land{size:297mm 210mm;margin:0}
*{box-sizing:border-box}html,body{margin:0;background:#fff;font-family:'Cairo',sans-serif;color:#111}
.pg{position:relative;overflow:hidden;background:#fff;break-after:page;page-break-after:always}
.pg:last-child{break-after:auto;page-break-after:auto}
.p{page:port;width:210mm;height:297mm}.l{page:land;width:297mm;height:210mm}
.nav{position:sticky;top:0;z-index:9;background:#14181F;color:#fff;display:flex;gap:10px;padding:8px 14px;align-items:center;
 font-weight:800;font-size:13px;flex-wrap:wrap}.nav a{color:#FFD400;text-decoration:none;border:1px solid #FFD40088;border-radius:14px;padding:2px 10px}
.nav b{margin-inline-end:auto}
@media screen{body{background:#8a8f98}.pg{margin:10px auto;box-shadow:0 0 8px #0007}}
@media print{.nav{display:none}}
.pl input,.pl textarea{font:700 12pt 'Cairo',sans-serif;border:0;background:transparent;width:100%;height:100%;padding:2pt 4pt;outline:0;color:#111;resize:none}
.pl input:focus,.pl textarea:focus{background:#FFF8C2}
@media print{.pl input,.pl textarea{background:transparent}}
""")

# ------------------------------------------------------------------ data helpers
def rack_levels_txt(r):
    return 'A–%s' % LETTERS[r['tiers'] - 1]

def groups(racks):
    """(zone, brand) groups in print order with their racks"""
    out = []
    for z in TYPES:
        seen = []
        for r in racks[z]:
            if r['brand'] not in seen:
                seen.append(r['brand'])
        for b in sorted(seen, key=ORDER.index):
            out.append((z, b, [r for r in racks[z] if r['brand'] == b]))
    return out

# ------------------------------------------------------------------ PAGE 1 : method + linear colour scale (landscape)
UNIT = 13.3   # mm per rack — the same length for every rack, so strips are comparable (linear scale)

def strip(label_en, label_ar, loc_en, loc_ar, segs, total_racks=19):
    """segs: list of (brand, text, half_split, tiers_note)"""
    cells = ''
    for br, txt, split, empty in segs:
        name, nar, col = BR[br] if br else ('', '', '#fff')
        if empty:
            bg = 'repeating-linear-gradient(135deg,#fff 0 1.6mm,#DDD 1.6mm 2.2mm)'
            fg, bd = '#999', '.3mm dashed #999'
        elif split:
            bg = 'linear-gradient(180deg,%s 0 50%%,%sCC 50%% 100%%)' % (col, col)
            fg, bd = '#fff', '.3mm solid #fff'
        else:
            bg, fg, bd = col, '#fff', '.3mm solid #fff'
        cells += ('<div style="width:%smm;height:15mm;background:%s;color:%s;border:%s;display:flex;flex-direction:column;'
                  'align-items:center;justify-content:center;font-weight:900;line-height:1.05;flex:none"><span dir="ltr" '
                  'style="font-size:4.6mm">%s</span><span dir="ltr" style="font-size:2.3mm;opacity:.95">%s</span></div>'
                  % (UNIT, bg, fg, bd, esc(txt[0]), esc(txt[1])))
    ticks = ''.join('<div style="width:%smm;flex:none;border-left:.25mm solid #333;height:2.6mm;font-size:2.4mm;font-weight:800;'
                    'padding-left:.6mm;line-height:3.2mm;margin-top:.3mm;direction:ltr">%d</div>' % (UNIT, i + 1) for i in range(len(segs)))
    return ('<div style="margin-bottom:5mm"><div style="display:flex;justify-content:space-between;align-items:baseline;gap:6mm;'
            'margin-bottom:1.2mm"><span dir="ltr" style="font-weight:900;font-size:3.9mm;white-space:nowrap">%s &nbsp;<span style="font-weight:700;'
            'font-size:2.9mm;color:#444">%s</span></span><span dir="rtl" style="font-weight:900;font-size:4mm;white-space:nowrap">%s '
            '<span style="font-weight:700;font-size:3mm;color:#444">· %s</span></span></div>'
            '<div style="display:flex;direction:ltr;border:.5mm solid #111;width:fit-content">%s</div>'
            '<div style="display:flex;direction:ltr;width:fit-content">%s</div></div>'
            % (esc(label_en), esc(loc_en), esc(label_ar), esc(loc_ar), cells, ticks))

def guide_page(racks):
    # ---- strips
    def segs_of(z):
        out = []
        for r in racks[z]:
            split = len(r['halves']) == 2
            out.append((r['brand'], (BR[r['brand']][0][:2] if r['brand'] != 'AL' else 'HB', str(r['no'])), split, False))
        # replace brand abbreviation text
        ab = {'DX': 'DOUX', 'DR': 'DARI', 'HB': 'HABRA', 'SA': 'SAUDI', 'GN': 'GEN', 'SP': 'SPARE'}
        return [(b, (str(t[1]), ab[b]), s, e) for (b, t, s, e) in out]
    s_c, s_p = segs_of('c'), segs_of('p')
    s_left = segs_of('b') + segs_of('a')
    s_left += [(None, ('', 'FREE · فارغ'), False, True)] * (19 - len(s_left))
    strips = (strip('A1 CARTONS', 'A1 الكراتين', 'Zone 3 · Left · 15 racks × 4 levels', 'المنطقة 3 · اليسار · 15 راك × 4 مستويات', s_c) +
              strip('A2 PLASTIC', 'A2 البلاستيك', 'Zone 1 · Right · 19 racks × 5 levels', 'المنطقة 1 · اليمين · 19 راك × 5 مستويات', s_p) +
              strip('A3 BOXES + A4 SUPPLIES', 'A3 علب + A4 مستلزمات',
                    'Zone 1 · Left · 6 + 10 racks × 5 levels · 3 free', 'المنطقة 1 · اليسار · 6 + 10 راك × 5 مستويات · 3 فارغة', s_left))
    leg = ''.join('<span style="display:inline-flex;align-items:center;gap:1.6mm;margin-inline-end:5mm;font-weight:800;font-size:3.4mm">'
                  '<i style="width:9mm;height:5mm;background:%s;display:inline-block;border-radius:1mm"></i>%s · %s</span>'
                  % (BR[b][2], BR[b][0], BR[b][1]) for b in ORDER)
    leg += ('<span style="display:inline-flex;align-items:center;gap:1.6mm;font-weight:800;font-size:3.4mm"><i style="width:9mm;height:5mm;'
            'display:inline-block;border-radius:1mm;background:linear-gradient(180deg,#555 0 50%,#555A 50% 100%)"></i>'
            'Shared rack · راك مشترك (½ + ½)</span>')
    # ---- written method (Arabic paragraph, then English)
    paras = [
        ('كل صنف يأخذ راكاً لوحده؛ والأصناف الزائدة فقط تشارك راكاً مناصفة (النصف السفلي ↓ والنصف العلوي ↑).',
         'Each item gets its own rack; only the leftover items share a rack by halves (lower half ↓ and upper half ↑).'),
        ('الراك له رقم داخل ماركته (دو · داري · الهبرة · السعودي · عام)، واللون هو الماركة.',
         'A rack is numbered inside its brand group (Doux · Dari · Al Habra · Saudi · General); the colour is the brand.'),
        ('يوضع على الراك حرف المستوى فقط: A = الأرض ثم B C D E للأعلى — 4 مستويات للكراتين (A–D) و5 للبقية (A–E).',
         'The rack carries the level letter only: A = floor, then B C D E upwards — 4 levels for cartons (A–D), 5 for the rest (A–E).'),
        ('البالتات داخل المستوى (بالعرض وبالعمق) بلا ملصق موقع؛ تُوضع على كل بالت ورقة «ليبل بالت» بلون ماركته وفيها رقم البالت والموقع (رقم الراك + الحرف).',
         'Pallets inside a level (across and in depth) carry no location sticker; each pallet gets one “Pallet Label” paper in its brand colour with the pallet no. and location (rack no. + letter).'),
        ('عرض المستوى 5 بالتات؛ سعة الراك = المستويات × 5 (الكراتين 20 بالت، البقية 25 بالت).',
         'A level holds 5 pallets across; rack capacity = levels × 5 (cartons 20 pallets, the rest 25 pallets).'),
    ]
    ptxt = ''.join('<div style="display:flex;gap:6mm;margin-bottom:2.6mm;align-items:flex-start">'
                   '<div dir="ltr" style="flex:1;font-size:3.35mm;line-height:1.35;font-weight:600;color:#222">%d. %s</div>'
                   '<div dir="rtl" style="flex:1;font-size:3.7mm;line-height:1.4;font-weight:800">%d. %s</div></div>'
                   % (i, esc(e), i, esc(a)) for i, (a, e) in enumerate(paras, 1))
    ptxt = ('<div style="display:flex;justify-content:space-between;font-weight:900;font-size:4.6mm;border-bottom:.4mm solid #111;'
            'padding-bottom:1mm;margin-bottom:2.4mm"><span dir="ltr">DISTRIBUTION METHOD</span><span dir="rtl">طريقة التوزيع</span></div>' + ptxt)
    ptxt2 = ptxt[ptxt.index('</div>', ptxt.index('border-bottom')) + 6:].replace('font-size:3.35mm', 'font-size:4.3mm').replace('font-size:3.7mm', 'font-size:4.9mm').replace('margin-bottom:2.6mm', 'margin-bottom:6.5mm')
    p1 = ('<section class="pg l" id="guide"><div style="position:absolute;left:14mm;right:14mm;top:9mm">'
          '<div style="margin-bottom:3mm"><div dir="ltr" style="font-weight:900;font-size:5.6mm">DRY SECTION · PART 1 — LINEAR COLOUR SCALE</div>'
          '<div dir="rtl" style="font-weight:900;font-size:6.4mm">القسم الجاف · الجزء 1 — المقياس الخطي بالألوان</div></div>'
          '<div style="margin-bottom:4mm">%s</div>%s'
          '<div dir="ltr" style="font-size:3mm;font-weight:700;color:#555;margin-top:-1mm">Every rack = the same length (linear scale) · numbers under a strip = rack position · rack 1 at the entrance end</div>'
          '<div dir="rtl" style="font-size:3.2mm;font-weight:700;color:#555">كل راك بنفس الطول (مقياس خطي) · الأرقام تحت الشريط = ترتيب الراك · الراك 1 من جهة المدخل</div>'
          '</div></section>' % (leg, strips))
    p2 = ('<section class="pg l" id="method"><div style="position:absolute;left:16mm;right:16mm;top:12mm">'
          '<div style="margin-bottom:6mm"><div dir="ltr" style="font-weight:900;font-size:5.6mm">DRY SECTION · PART 1 — DISTRIBUTION METHOD</div>'
          '<div dir="rtl" style="font-weight:900;font-size:6.4mm">القسم الجاف · الجزء 1 — طريقة التوزيع</div></div>%s</div></section>' % ptxt2)
    return p1 + p2

# ------------------------------------------------------------------ PAGE 2..5 : distribution tables
def table_page(z, racks):
    T = TYPES[z]
    zen, zar = ZONE_TXT[z]
    rows = ''
    for r in racks[z]:
        be, bar, col = BR[r['brand']]
        for k, h in enumerate(r['halves']):
            it = h['item']
            rng = LETTERS[h['levels'][0] - 1] + ('–' + LETTERS[h['levels'][-1] - 1] if len(h['levels']) > 1 else '')
            tag = '' if h['name'] == 'full' else (' ↓' if h['name'] == 'lower' else ' ↑')
            nm_ar = (esc(it['ar']) + (' <bdi dir="ltr">%s</bdi>' % esc(it['size']) if it['size'] else '')) if it else 'راك احتياطي (غير مخصص)'
            nm_en = it['en'].strip() if it else 'SPARE RACK (NOT ASSIGNED)'
            first = k == 0
            rows += ('<tr>%s<td dir="ltr" style="font-weight:900">%s%s</td><td dir="ltr" style="font-weight:900;color:#fff;background:%s;text-align:center">'
                     '%s · %s</td><td dir="ltr" style="font-weight:700">%s</td><td dir="rtl" style="font-weight:800">%s</td></tr>'
                     % (('<td rowspan="%d" dir="ltr" style="font-weight:900;text-align:center">%d</td>' % (len(r['halves']), r['gno'])) if first else '',
                        rng, tag, col, be, bar, esc(nm_en), nm_ar))
            if first:
                rows = rows.replace('<tr><td rowspan', '<tr><td rowspan', 1)
        if len(r['halves']) == 2:
            pass
    head = ('<tr style="background:#14181F;color:#fff"><th>#</th><th dir="ltr">LEVELS<br>المستويات</th><th dir="ltr">BRAND · الماركة</th>'
            '<th dir="ltr">ITEM (EN)</th><th dir="rtl">الصنف (عربي)</th></tr>')
    return ('<section class="pg l" id="tbl-%s"><div style="position:absolute;left:14mm;right:14mm;top:9mm">'
            '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2mm">'
            '<span dir="ltr" style="font-weight:900;font-size:5.4mm"><span style="background:%s;color:#fff;border-radius:3mm;padding:0 3mm;margin-inline-end:2mm">%s</span>'
            '%s — RACK DISTRIBUTION <span style="font-weight:700;font-size:3.4mm;color:#444">· %s · %d racks × %d levels</span></span>'
            '<span dir="rtl" style="font-weight:900;font-size:6mm">توزيع الراكات — %s <span style="font-weight:700;font-size:3.6mm;color:#444">· %s</span></span></div>'
            '<table style="border-collapse:collapse;width:100%%;font-size:%smm;line-height:1.15" class="tb">%s%s</table>'
            '<style>.tb td,.tb th{border:.25mm solid #888;padding:.5mm 1.6mm}.tb th{font-size:2.8mm}</style></div></section>'
            % (z, T['hdr'], T['tag'], T['en'], zen, len(racks[z]), T['tiers'], T['name_ar'], zar,
               2.9 if len(racks[z]) > 15 else 3.3, head, rows))

# ------------------------------------------------------------------ rack-level LETTER stickers (A4, 78x50 cut size)
def lv_sticker(col, idx, tiers, spare=False):
    L = LETTERS[idx - 1]
    dn = ('FLOOR', 'أرضي') if idx == 1 else (LETTERS[idx - 2], '')
    up = ('TOP', 'علوي') if idx == tiers else (LETTERS[idx], '')
    def side(arr, lab):
        l2 = '<span dir="rtl" style="font-size:2.7mm;font-weight:800;line-height:1">%s</span>' % lab[1] if lab[1] else ''
        return ('<div style="width:14mm;display:flex;flex-direction:column;align-items:center;gap:.5mm">%s<span dir="ltr" '
                'style="font-weight:900;font-size:%smm;line-height:1">%s</span>%s</div>' % (arr, 3.4 if lab[1] else 4.6, lab[0], l2))
    note = ('<div style="position:absolute;left:2.4mm;bottom:1.3mm;display:flex;flex-direction:column;align-items:center;line-height:1.05;'
            'font-weight:800;font-size:2.5mm;opacity:.55"><span dir="ltr">SPARE</span><span dir="rtl">احتياطي</span></div>') if spare else ''
    return ('<div style="width:78mm;height:50mm;background:%s;border:1.1mm solid %s;border-radius:4mm;overflow:hidden;direction:ltr;'
            'display:flex;flex-direction:column;position:relative"><div style="height:8mm;background:%s"></div>'
            '<div style="flex:1;display:flex;align-items:center;justify-content:space-between;padding:0 3mm 2mm">%s'
            '<div dir="ltr" style="font-weight:900;font-size:33mm;line-height:.8;padding-bottom:3mm">%s</div>%s</div>%s</div>'
            % (YEL, INK, col, side(arrow(True), dn), L, side(arrow(False), up), note))

def sticker_pages(racks):
    secs, total = [], 0
    for z, b, rl in groups(racks):
        T = TYPES[z]
        be, bar, col = BR[b]
        tiers = rl[0]['tiers']
        need = [(lv, False) for lv in range(1, tiers + 1) for _ in rl]   # n racks x each level, grouped by letter
        total += len(need)
        pages = [need[i:i + 10] for i in range(0, len(need), 10)]
        spare_cycle = 0
        for pi, pg in enumerate(pages, 1):
            if len(pg) < 10:
                pg = pg + [(1 + (spare_cycle + k) % tiers, True) for k in range(10 - len(pg))]
            cells = ''.join(lv_sticker(col, lv, tiers, sp) for lv, sp in pg)
            rn = '%d–%d' % (1, len(rl)) if len(rl) > 1 else '1'
            secs.append(
                '<section class="pg p" id="stk-%s-%s-%d"><div style="position:absolute;left:24.5mm;top:3.2mm;width:161mm;height:10mm;display:flex;'
                'justify-content:space-between;align-items:flex-start;font-weight:900;font-size:3.5mm;line-height:1.15;color:#111;white-space:nowrap">'
                '<span dir="ltr">%s · %s · %s · RACKS %s · LEVELS A–%s<br><span style="font-weight:700;font-size:3mm">RACK-LEVEL LETTER STICKERS · PAGE %d/%d</span></span>'
                '<span dir="rtl" style="text-align:right">%s · %s · %s · الراكات %s · المستويات A–%s<br><span style="font-weight:700;font-size:3mm">'
                'ملصقات حرف مستوى الراك · صفحة %d/%d</span></span></div>'
                '<div style="position:absolute;left:24.5mm;top:18mm;width:161mm;height:270mm;display:grid;direction:ltr;grid-template-columns:repeat(2,78mm);'
                'grid-auto-rows:50mm;gap:5mm">%s</div>%s</section>'
                % (z, b, pi, T['tag'], T['en'], be, rn, LETTERS[tiers - 1], pi, len(pages),
                   T['tag'], T['name_ar'], bar, rn, LETTERS[tiers - 1], pi, len(pages), cells, overlay(210, 297, 24.5, 18, 2, 5)))
    return secs, total

# ------------------------------------------------------------------ PALLET LABEL page (A4, geometry of the paper supplied by Ahmed, in pt)
PW, PH = 595.92, 842.88
SC = 595.2756 / PW      # the supplied paper is 595.92 pt wide; A4 is 595.28 pt
FIELDS = [  # key, EN, AR, row top, row bottom, en/ar centre y, input rect (x0,y0,x1,y1)
    ('DATE_OF_REC', 'DATE OF REC', 'تاريخ الاستلام', 221.25, 265.5, 243.0, (299.6, 222.4, 551.9, 263.0)),
    ('EXPIRY_DATE', 'EXPIRY DATE', 'تاريخ الانتهاء', 266.2, 311.2, 288.8, (299.6, 267.7, 551.9, 308.3)),
    ('QUANTITY', 'QUANTITY', 'الكمية', 442.5, 486.75, 464.3, (299.6, 443.5, 551.9, 484.1)),
    ('CONTAINER_NO', 'CONTAINER NO.', 'رقم الحاوية', 487.5, 532.5, 509.3, (299.6, 488.8, 551.9, 529.4)),
    ('FORKLIFT_OPER', 'FORKLIFT OPER.', 'سائق الرافعة', 533.2, 577.5, 555.0, (299.6, 534.2, 551.9, 574.8)),
    ('REC_FOREMAN', 'REC. FOREMAN', 'مراقب الاستلام', 578.2, 622.5, 600.0, (299.6, 579.5, 551.9, 620.1)),
    ('PRODUCT', 'PRODUCT', 'المنتج', 623.2, 678.0, 650.3, (299.6, 624.9, 551.9, 675.4)),
    ('SIZE', 'SIZE', 'الحجم', 678.8, 724.5, 701.3, (299.6, 680.1, 551.9, 721.5)),
]
BIG = [('PALLET_NO', (43.3, 325.1, 295.6, 438.7)), ('LOCATION', (300.4, 325.1, 551.9, 438.7)),
       ('RECEIVING_OFFICER', (38.8, 777.4, 281.5, 807.4)), ('WAREHOUSE_SUPERVISOR', (313.8, 777.4, 556.4, 807.4))]
TIMES = "'Times New Roman','Tinos','FreeSerif','Liberation Serif',serif"

def _abs(x0, y0, x1, y1, inner, extra=''):
    return '<div style="position:absolute;left:%.1fpt;top:%.1fpt;width:%.1fpt;height:%.1fpt;%s">%s</div>' % (x0, y0, x1 - x0, y1 - y0, extra, inner)

def logo_uri():
    return 'data:image/png;base64,' + base64.b64encode(open(LOGO, 'rb').read()).decode()

def pallet_page(br, fillable=True, pre=None, sid=None):
    be, bar, col = BR[br]
    pre = pre or {}
    def inp(key, rect, ml=False):
        if key in pre:
            return _abs(*rect, pre[key], 'display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center')
        if not fillable:
            return ''
        return _abs(*rect, ('<textarea name="%s_%s"></textarea>' if ml else '<input name="%s_%s">') % (br, key))
    o = ''
    o += _abs(36.75, 34.5, 93, 102.75, '', 'background:var(--logo) center/contain no-repeat')
    o += _abs(380, 66, 558.4, 86, '<span style="font-family:%s;font-weight:700;font-size:14pt;letter-spacing:1.6pt;color:#444">PALLET LABEL</span>' % TIMES, 'text-align:right;direction:ltr')
    o += _abs(380, 78, 558.4, 108.3, '<span style="font-weight:800;font-size:16pt;color:#444">ليبل بالت</span>', 'text-align:right;direction:rtl;line-height:30pt')
    # frame + header
    o += _abs(36.75, 111, 558.75, 729, '', 'border:4.5pt solid #111;background:#fff')
    o += _abs(36.75, 111, 558.75, 221.25, '', 'background:%s;border:4.5pt solid #111;border-bottom:0' % col)
    o += _abs(36.75, 116, 558.75, 160, '<span style="font-weight:900;font-size:25pt;color:#fff">مصنع المنجم لإنتاج اللحوم</span>', 'text-align:center;direction:rtl;line-height:44pt')
    o += _abs(36.75, 160, 558.75, 177, '<span style="font-family:%s;font-weight:700;font-size:12.5pt;color:#fff;letter-spacing:.8pt">ALMUNAJEM MEAT PRODUCTION FACTORY</span>' % TIMES, 'text-align:center;direction:ltr;line-height:17pt')
    chx = (202.5, 392.2) if len(be) <= 5 else (178, 417)
    o += _abs(chx[0], 183, chx[1], 207, ('<span dir="ltr" style="font-family:%s;font-weight:700;font-size:10.5pt;color:#333">BRAND / <span dir="rtl" style="font-weight:800">الماركة</span></span>'
              '<span dir="ltr" style="font-family:%s;font-weight:700;font-size:15pt;color:%s;margin-left:10pt">%s&nbsp; | &nbsp;<span dir="rtl" style="font-weight:900;font-size:14pt">%s</span></span>' % (TIMES, TIMES, col, be, bar)),
              'background:#fff;display:flex;align-items:center;justify-content:center;border-radius:2pt;white-space:nowrap')
    # grid lines
    for y in (265.5, 311.25, 441.75, 486.75, 532.5, 577.5, 622.5, 678.0):
        o += _abs(41.25, y, 554.25, y + .8, '', 'background:#111')
    for (a, b) in ((221.25, 311.25), (441.75, 724.5)):
        o += _abs(297.0, a, 297.8, b, '', 'background:#111')
    o += _abs(297.8, 311.5, 298.5, 441.75, '', 'background:#111')
    # rows
    for key, en, ar, r0, r1, cy, rect in FIELDS:
        o += _abs(52.7, cy - 15, 285.5, cy + 15, '<span style="font-family:%s;font-weight:700;font-size:14pt;color:#111">%s</span>' % (TIMES, en), 'display:flex;align-items:center')
        o += _abs(150, cy - 15, 285.5, cy + 15, '<span dir="rtl" style="font-weight:800;font-size:14pt;color:#111">%s</span>' % ar, 'display:flex;align-items:center;justify-content:flex-end;direction:ltr')
        o += inp(key, rect)
    o += _abs(52.7, 315, 200, 332, '<span style="font-family:%s;font-weight:700;font-size:11pt;color:#444">PALLET NO.</span>' % TIMES)
    o += _abs(150, 313, 286.3, 335, '<span style="font-weight:800;font-size:12.5pt;color:#444">رقم البالت</span>', 'text-align:right;direction:rtl')
    o += _abs(309.7, 315, 450, 332, '<span style="font-family:%s;font-weight:700;font-size:11pt;color:#444">LOCATION</span>' % TIMES)
    o += _abs(450, 313, 542.6, 335, '<span style="font-weight:800;font-size:12.5pt;color:#444">الموقع</span>', 'text-align:right;direction:rtl')
    o += inp('PALLET_NO', BIG[0][1], True) + inp('LOCATION', BIG[1][1], True)
    # signatures
    for x0, x1, en, ar, key, rect in ((36.8, 283.5, 'RECEIVING OFFICER', 'مسؤول الاستلام', 'RECEIVING_OFFICER', BIG[2][1]),
                                      (311.8, 558.8, 'WAREHOUSE SUPERVISOR', 'مشرف المستودع', 'WAREHOUSE_SUPERVISOR', BIG[3][1])):
        o += _abs(x0, 752, x1, 776, '<span style="font-family:%s;font-weight:700;font-size:11pt;color:#111">%s</span>' % (TIMES, en), 'display:flex;align-items:center;justify-content:flex-start')
        o += _abs(x0, 752, x1, 776, '<span dir="rtl" style="font-weight:800;font-size:11.5pt;color:#111">%s</span>' % ar, 'display:flex;align-items:center;justify-content:flex-end;direction:ltr')
        o += _abs(x0, 809.2, x1, 810.0, '', 'background:#111')
        o += _abs(x0, 811, x1, 825, '<span dir="ltr" style="font-family:%s;font-size:9pt;color:#777">Signature / <span dir="rtl" style="font-family:Cairo">التوقيع</span></span>' % TIMES, 'text-align:center')
        o += inp(key, rect)
    return ('<section class="pg pl p" id="%s"><div style="position:absolute;left:0;top:0;width:%.2fpt;height:%.2fpt;transform:scale(%.5f);'
            'transform-origin:0 0">%s</div></section>' % (sid or ('pal-' + br), PW, PH, SC, o))

def numbered_sheets():
    """one pallet-label paper per pallet: P1..P20 (cartons, 4 levels) / P1..P25 (5 levels); a shared rack numbers each item from P1"""
    racks = build_racks()
    pages, meta = [], []
    for zt in TYPES:
        T = TYPES[zt]
        for r in racks[zt]:
            for h in r['halves']:
                it = h['item']
                if not it:
                    continue                                   # spare rack: nothing assigned
                n_all = len(h['levels']) * 5
                for n in range(1, n_all + 1):
                    lvl = h['levels'][(n - 1) // 5]
                    L, pos = LETTERS[lvl - 1], (n - 1) % 5 + 1
                    loc = '%s-%s-%d%s%d' % (T['code'], r['brand'], r['no'], L, pos)
                    big = ('<div dir="ltr" style="font-weight:900;font-size:96pt;line-height:1;letter-spacing:-2pt;color:#111">P%d</div>' % n)
                    locb = ('<div dir="ltr" style="font-weight:900;font-size:30pt;line-height:1">%s</div>'
                            '<div dir="ltr" style="font-weight:800;font-size:8.5pt;margin-top:3pt;color:#333">RACK %d · LEVEL %s · POSITION %d</div>'
                            '<div dir="rtl" style="font-weight:800;font-size:9.5pt;color:#333">راك %d · مستوى %s · موضع %d</div>'
                            '<div dir="ltr" style="font-weight:700;font-size:7.5pt;margin-top:3pt;color:#555">%s · %s</div>'
                            % (loc, r['no'], L, pos, r['no'], L, pos, T['tag'] + ' ' + T['en'], T['name_ar']))
                    nm_ar = esc(it['ar']) + (' <bdi dir="ltr">%s</bdi>' % esc(it['size']) if it['size'] else '')
                    prod = ('<div dir="rtl" style="font-weight:800;font-size:11pt;line-height:1.15">%s</div>'
                            '<div dir="ltr" style="font-family:%s;font-weight:700;font-size:8.5pt;line-height:1.15">%s</div>' % (nm_ar, TIMES, esc(it['en'].strip())))
                    pre = {'PALLET_NO': big, 'LOCATION': locb, 'PRODUCT': prod}
                    if it['size']:
                        pre['SIZE'] = '<div dir="ltr" style="font-weight:900;font-size:15pt">%s</div>' % esc(it['size'])
                    sid = 'pn-%s-%s-%d-%s-%d' % (zt, r['brand'], r['no'], h['name'], n)
                    pages.append(pallet_page(r['brand'], True, pre, sid))
                    meta.append(dict(z=zt, tag=T['tag'], name_ar=T['name_ar'], en=T['en'], brand=r['brand'], rack=r['no'], half=h['name'],
                                     n=n, loc=loc, item=it['en'].strip()))
    return pages, meta

def numbered_build(out_dir):
    import json
    pages, meta = numbered_sheets()
    doc = ('<!-- VERSION: v1 | %s -->\n<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><title>Pallet labels P1–P25</title>'
           '<style>%s</style></head><body>%s</body></html>' % (DATE, css(), ''.join(pages)))
    p = os.path.join(out_dir, 'almunajem_pallet_labels_numbered_v1_%s.html' % DATE)
    open(p, 'w', encoding='utf-8').write(doc)
    json.dump(meta, open(os.path.join(out_dir, 'numbered_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    return p, len(pages)

def page_for_pallets_only():
    return ('<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><title>Pallet Label</title><style>%s'
            '</style></head><body>%s</body></html>'
            % (css(), ''.join(pallet_page(b) for b in ('DX', 'DR', 'HB', 'SA', 'GN'))))

# ------------------------------------------------------------------ build
def old_sticker_pages():
    """rack labels = the ORIGINAL sticker design, one sticker per level (2 copies per level), 1 A4 page per rack"""
    return [x.replace('<section class="pg"', '<section class="pg p"', 1) for x in m.level_a4_pages(build_racks())]

def build(out_dir):
    racks = build_racks()
    os.makedirs(out_dir, exist_ok=True)
    stk = old_sticker_pages()
    total = len(stk)
    pal = [pallet_page(b) for b in ('DX', 'DR', 'HB', 'SA', 'GN')]
    nav = ('<div class="nav"><b>AL-MUNAJEM · DRY SECTION PART 1 · القسم الجاف الجزء 1 · %s</b>'
           '<a href="#guide">Colour scale · المقياس</a><a href="#method">Method · الطريقة</a>%s'
           '<a href="#stickers">Rack labels · ليبل الراك</a><a href="#pal-DX">Pallet labels · ليبل البالت</a></div>'
           % (VERSION, ''.join('<a href="#tbl-%s">%s</a>' % (z, TYPES[z]['tag']) for z in TYPES)))
    stk[0] = stk[0].replace('<section class="pg p"', '<section id="stickers" class="pg p"', 1)
    body = nav + guide_page(racks) + ''.join(table_page(z, racks) for z in TYPES) + ''.join(stk) + ''.join(pal)
    doc = ('<!-- VERSION: %s | %s -->\n<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><title>Al-Munajem Dry Part 1 — %s</title>'
           '<style>%s</style></head><body>%s%s</body></html>' % (VERSION, DATE, VERSION, css(), body, FIT_JS))
    p1 = os.path.join(out_dir, 'almunajem_dry_part1_system_%s_%s.html' % (VERSION, DATE))
    open(p1, 'w', encoding='utf-8').write(doc)
    p2 = os.path.join(out_dir, 'almunajem_pallet_labels_fillable_%s_%s.html' % ('v1', DATE))
    open(p2, 'w', encoding='utf-8').write('<!-- VERSION: v1 | %s -->\n' % DATE + page_for_pallets_only())
    return p1, p2, total, len(stk)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    p1, p2, total, npg = build(out)
    print('level sticker pages:', total); print(p1); print(p2)
    print(numbered_build(out))
