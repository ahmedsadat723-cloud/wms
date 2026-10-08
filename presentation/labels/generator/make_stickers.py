#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Al-Munajem pallet location stickers — generator v2
- one rack = one item (shared racks: two items, lower/upper half, each with its own stickers)
- rack = NUMBER inside its brand group, level = LETTER (A = floor level)
- outputs: A4 + SRA3 HTML (fonts embedded, taken from the v1 HTML next to this folder)
Usage: python3 make_stickers.py <out_dir>      (then render_pdf.py for the PDFs)
"""
import json, os, re, sys, html
from barcode import Code128

HERE = os.path.dirname(os.path.abspath(__file__))
V1_A4 = os.path.join(HERE, '..', 'almunajem_location_stickers_A4_2026-10-08.html')
VERSION = 'v2'
DATE = '2026-10-08'
LETTERS = 'ABCDE'
YEL, INK = '#FFD400', '#111111'

TYPES = {
    'c': dict(tag='A1', code='3L', hdr='#9A6A2F', ar='كرتون', en='CARTON', tiers=4,
              desc='CARTONS · ZONE 3 · SPIC · LEFT', name_ar='الكراتين'),
    'p': dict(tag='A2', code='1R', hdr='#1E8FA3', ar='بلاستيك', en='PLASTIC', tiers=5,
              desc='PLASTIC · ZONE 1 · PKG · RIGHT', name_ar='البلاستيك'),
    'b': dict(tag='A3', code='1L', hdr='#6A3FA0', ar='علب تعبئة', en='BOX', tiers=5,
              desc='PACKAGING BOXES · ZONE 1 · PKG · LEFT', name_ar='علب التعبئة'),
}
BRANDS = {'DX': ('DOUX', '#1F4E9E', 'دو'), 'DR': ('DARI', '#A3261F', 'داري'),
          'HB': ('AL HABRA', '#8A4B0F', 'الهبرة'), 'SA': ('SAUDI', '#14633F', 'السعودي'),
          'GN': ('GENERAL', '#3D5563', 'عام'), 'SP': ('SPARE', '#777777', 'احتياطي')}

# ---------------------------------------------------------------- items (from v1 stickers)
_old = json.load(open(os.path.join(HERE, 'items_v1.json'), encoding='utf-8'))
ITEMS = {}
for (zone, br, rl), its in _old:
    z = {'3L': 'c', '1R': 'p', '1L': 'b'}[zone]
    for i, (ar, size, en) in enumerate(its):
        ITEMS[f'{z}.{br}.{rl}.{i}'] = dict(ar=ar, size=size, en=en)

# ---------------------------------------------------------------- layout v2
# equal division: every item gets its own rack first; only the leftover items share a rack
# (lower half / upper half) with a similar item of the same brand.
LAYOUT = {
    'c': [('DX', ['A.0', 'A.1']), ('DX', ['B.0']), ('DX', ['C.0', 'C.1']), ('DX', ['D.0', 'D.1']),
          ('DX', ['E.0']), ('DX', ['F.0']), ('DX', ['G.0']),
          ('DR', ['A.0']), ('DR', ['B.0']), ('DR', ['B.1']),
          ('HB', ['A.0']), ('HB', ['B.0']),
          ('SA', ['A.0']), ('SA', ['B.0']), ('SA', ['C.0'])],
    'p': [('DX', ['A.0', 'A.1']), ('DX', ['B.0', 'B.1']), ('DX', ['C.0']), ('DX', ['C.1']),
          ('DX', ['D.0']), ('DX', ['E.0']), ('DX', ['E.1']), ('DX', ['F.0', 'F.1']), ('DX', ['G.0', 'G.1']),
          ('DR', ['A.0', 'A.1']), ('DR', ['B.0']), ('DR', ['B.1']), ('DR', ['C.0']),
          ('HB', ['A.0']), ('HB', ['B.0']),
          ('SA', ['A.0', 'A.1']), ('SA', ['B.0']),
          ('GN', ['A.0']), ('GN', ['A.1'])],
    'b': [('DX', ['A.0']), ('DX', ['B.0']), ('DX', ['C.0']), ('DX', ['D.0']), ('DX', ['E.0']), ('SP', [])],
}

def build_racks():
    racks = []   # per zone list of dict
    out = {}
    for z, lst in LAYOUT.items():
        counters, rl = {}, []
        for gi, (br, refs) in enumerate(lst, 1):
            counters[br] = counters.get(br, 0) + 1
            items = [ITEMS[f'{z}.{br}.{r}'] for r in refs]
            tiers = TYPES[z]['tiers']
            if len(items) == 2:
                low = (tiers + 1) // 2          # 4 -> 2 | 5 -> 3 (odd tiers: the lower half gets the extra level)
                halves = [dict(name='lower', levels=list(range(1, low + 1)), item=items[0]),
                          dict(name='upper', levels=list(range(low + 1, tiers + 1)), item=items[1])]
            elif len(items) == 1:
                halves = [dict(name='full', levels=list(range(1, tiers + 1)), item=items[0])]
            else:
                halves = [dict(name='spare', levels=list(range(1, tiers + 1)), item=None)]
            rl.append(dict(zone=z, brand=br, no=counters[br], gno=gi, tiers=tiers, halves=halves))
        out[z] = rl
    return out

# ---------------------------------------------------------------- fonts / css
def font_css():
    s = open(V1_A4, encoding='utf-8').read()
    return ''.join(re.findall(r'@font-face\{[^}]*\}', s))

FIT_JS = """<script>
function fit(){document.querySelectorAll('[data-fit]').forEach(function(el){
 var box=el.parentElement,cs=getComputedStyle(box);
 var max=box.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
 var fs=parseFloat(el.style.fontSize),g=0;
 while(el.scrollWidth>max&&fs>1.3&&g++<80){fs*=0.97;el.style.fontSize=fs+'mm';}});}
if(document.fonts&&document.fonts.ready){document.fonts.ready.then(fit);}window.addEventListener('load',fit);
</script>"""

def page_css(w, h):
    return ('@media screen{body{background:#888}.pg{margin:8px auto;box-shadow:0 0 6px #0006}}' + font_css() +
            '@page{size:%smm %smm;margin:0}html,body{margin:0;background:#fff}'
            '.pg{position:relative;overflow:hidden;background:#fff;page-break-after:always;break-after:page}'
            '.pg:last-child{page-break-after:auto}' % (w, h))

# ---------------------------------------------------------------- barcode
def barcode_svg(code, h):
    mods = Code128(code).build()[0]
    m = 56.0 / len(mods)
    rects, i = [], 0
    while i < len(mods):
        if mods[i] == '1':
            j = i
            while j < len(mods) and mods[j] == '1':
                j += 1
            rects.append('<rect x="%.3f" y="0" width="%.3f" height="%s"/>' % (i * m, (j - i) * m, h))
            i = j
        else:
            i += 1
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="56mm" height="%smm" viewBox="0 0 56 %s" fill="%s" '
            'shape-rendering="crispEdges">%s</svg>' % (h, h, INK, ''.join(rects)))

# ---------------------------------------------------------------- sticker
ARROW = '<polygon points="50,2 98,52 68,52 68,108 32,108 32,52 2,52" fill="%s"/>' % INK
def arrow(down):
    st = ' style="transform:rotate(180deg)"' if down else ''
    return '<svg%s viewBox="0 0 100 110" width="9.5mm" height="10.5mm">%s</svg>' % (st, ARROW)
BAR_FLOOR = ('<div style="width:9.5mm;height:10.5mm;display:flex;align-items:flex-start"><div style="width:9.5mm;'
             'height:2.2mm;background:repeating-linear-gradient(90deg,%s 0 1.4mm,transparent 1.4mm 2.4mm)"></div></div>' % INK)
BAR_TOP = ('<div style="width:9.5mm;height:10.5mm;display:flex;align-items:flex-end"><div style="width:9.5mm;'
           'height:2.2mm;background:%s"></div></div>' % INK)
LBL = 'font-weight:900;font-size:3.6mm;line-height:1'

def side(inner, label):
    return ('<div style="width:11mm;display:flex;flex-direction:column;align-items:center;gap:.4mm">%s'
            '<span dir="ltr" style="%s">%s</span></div>' % (inner, LBL, label))

def half_tag(half, levels, fs=2.5, mt='.5mm'):
    rng = LETTERS[levels[0] - 1] + ('–' + LETTERS[levels[-1] - 1] if len(levels) > 1 else '')
    if half == 'lower':
        st, ar, en, arrow_ = 'background:%s;color:%s' % (INK, YEL), 'النصف السفلي', 'LOWER', '↓'
    else:
        st, ar, en, arrow_ = 'background:%s;color:%s;border:.35mm solid %s' % (YEL, INK, INK), 'النصف العلوي', 'UPPER', '↑'
    return ('<div style="%s;display:flex;align-items:center;gap:1.2mm;padding:0 2mm;border-radius:1.6mm;'
            'font-weight:900;font-size:%smm;line-height:1.5;white-space:nowrap;margin-top:%s">'
            '<span dir="ltr">%s %s · %s</span><span dir="rtl">%s</span></div>' % (st, fs, mt, arrow_, en, rng, ar))

def item_lines(item, big, small):
    ar = html.escape(item['ar']) + (' <bdi dir="ltr">%s</bdi>' % html.escape(item['size']) if item['size'] else '')
    return ('<div data-fit dir="rtl" style="white-space:nowrap;font-weight:800;font-size:%smm;line-height:1.15">%s</div>'
            '<div data-fit dir="ltr" style="white-space:nowrap;font-weight:700;font-size:%smm;line-height:1.15;opacity:.85">%s</div>'
            % (big, ar, small, html.escape(item['en'].strip())))

def sticker(z, br, rack_no, lvl, pal, item, half, levels, tiers):
    T = TYPES[z]
    bname = BRANDS[br][0]
    L = LETTERS[lvl - 1]
    code = '%s-%s-%d%s-%d' % (T['code'], br, rack_no, L, pal)
    spare = item is None
    shared = half in ('lower', 'upper')
    head = ('<div style="height:9mm;background:%s;color:#fff;display:flex;align-items:center;justify-content:space-between;'
            'padding:0 3mm;font-weight:900;font-size:4.2mm;line-height:1;white-space:nowrap">'
            '<span dir="ltr" style="min-width:16mm">%s</span><span dir="rtl" style="color:#fff;letter-spacing:.2mm">%s · %s</span>'
            '<span dir="ltr" style="min-width:16mm;text-align:right">%s</span></div>'
            % (T['hdr'], bname, T['ar'], T['en'], T['code']))
    panel_css = ('background:#F2C200;border-bottom:.5mm solid %s;display:flex;flex-direction:column;align-items:center;'
                 'justify-content:center;padding:0 1.5mm;overflow:hidden' % INK)
    if spare:
        panel, big, bh, svgh = '', 25, 13.5, 7.4
    elif shared:
        panel = '<div style="height:12mm;%s">%s%s</div>' % (panel_css, item_lines(item, 3.0, 2.3), half_tag(half, levels))
        big, bh, svgh = 13.5, 11.8, 6
    else:
        panel = '<div style="height:8.2mm;%s">%s</div>' % (panel_css, item_lines(item, 3.3, 2.6))
        big, bh, svgh = 17, 11.8, 6
    left = side(BAR_FLOOR, 'FLOOR') if lvl == 1 else side(arrow(True), '%d%s' % (rack_no, LETTERS[lvl - 2]))
    right = side(BAR_TOP, 'TOP') if lvl == tiers else side(arrow(False), '%d%s' % (rack_no, LETTERS[lvl]))
    mid = ('<div style="flex:1;display:flex;align-items:center;justify-content:space-between;padding:0 2.6mm;position:relative">'
           '%s<div dir="ltr" style="font-weight:900;font-size:%smm;line-height:.82;letter-spacing:-.5mm;padding-bottom:1mm">%d'
           '<span style="margin-left:1mm">%s</span></div>%s</div>' % (left, big, rack_no, L, right))
    bar = ('<div style="height:%smm;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;gap:.3mm;'
           'padding-bottom:1.6mm">%s<span dir="ltr" style="font-weight:900;font-size:3.5mm;line-height:1;letter-spacing:.8mm">%s</span></div>'
           % (bh, barcode_svg(code, svgh), code))
    pal_b = ('<div dir="ltr" style="position:absolute;right:1.6mm;bottom:1.4mm;background:%s;color:%s;border-radius:2mm;'
             'padding:0 1.8mm;font-weight:900;font-size:4.6mm;line-height:1.35">P%d</div>' % (INK, YEL, pal))
    return ('<div class="stk" style="width:78mm;height:50mm;box-sizing:border-box;background:%s;border:1.1mm solid %s;'
            'border-radius:4mm;overflow:hidden;direction:ltr;display:flex;flex-direction:column;font-family:\'Cairo\',sans-serif;'
            'color:%s;position:relative">%s%s%s%s%s</div>' % (YEL, INK, INK, head, panel, mid, bar, pal_b))

# ---------------------------------------------------------------- cut guides
def overlay(W, H, L, T, cols, rows):
    right = L + cols * 78 + (cols - 1) * 5
    bottom = T + rows * 50 + (rows - 1) * 5
    f = lambda v: ('%.1f' % v)
    k = []
    k += ['<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(L - 2.2), f(T), f(L - 8.2), f(T)),
          '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(L), f(T - 2.2), f(L), f(T - 8.2)),
          '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(right + 2.2), f(T), f(right + 8.2), f(T)),
          '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(right), f(T - 2.2), f(right), f(T - 8.2)),
          '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(L - 2.2), f(bottom), f(L - 8.2), f(bottom)),
          '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(L), f(bottom + 2.2), f(L), f(bottom + 8.2)),
          '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(right + 2.2), f(bottom), f(right + 8.2), f(bottom)),
          '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(right), f(bottom + 2.2), f(right), f(bottom + 8.2))]
    for c in range(1, cols):
        x = L + c * 83 - 2.5
        k += ['<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(x), f(T - 2.2), f(x), f(T - 6.2)),
              '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(x), f(bottom + 2.2), f(x), f(bottom + 6.2))]
    for r in range(1, rows):
        y = T + r * 55 - 2.5
        k += ['<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(L - 2.2), f(y), f(L - 6.2), f(y)),
              '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(right + 2.2), f(y), f(right + 6.2), f(y))]
    rects = ''.join('<rect x="%s" y="%s" width="79.8" height="51.8" rx="4.9"/>' % (f(L + c * 83 - .9), f(T + r * 55 - .9))
                    for r in range(rows) for c in range(cols))
    return ('<svg style="position:absolute;left:0;top:0" width="%smm" height="%smm" viewBox="0 0 %s %s">'
            '<g stroke="#000" stroke-width="0.25" fill="none">%s</g>'
            '<g stroke="#E6007E" stroke-width="0.3" fill="none" stroke-dasharray="2.2 1.2">%s</g></svg>'
            % (W, H, W, H, ''.join(k), rects))

# ---------------------------------------------------------------- rack stickers (ordered top level first)
def rack_stickers(r, pals):
    out = []
    for lvl in range(r['tiers'], 0, -1):
        h = next(h for h in r['halves'] if lvl in h['levels'])
        for p in pals:
            out.append(sticker(r['zone'], r['brand'], r['no'], lvl, p, h['item'], h['name'], h['levels'], r['tiers']))
    return ''.join(out)

def rack_title_ar(r):
    hs = r['halves']
    def nm(h):
        i = h['item']
        return html.escape(i['ar']) + (' <bdi dir="ltr">%s</bdi>' % html.escape(i['size']) if i['size'] else '')
    line = lambda name, pill='': ('<div style="display:flex;align-items:center;justify-content:flex-end;gap:3mm;direction:rtl;'
                                  'font-weight:900;font-size:5.2mm;line-height:1.3"><span>%s</span>%s</div>' % (name, pill))
    if hs[0]['name'] == 'spare':
        return [line('راك احتياطي (غير مخصص)')]
    if len(hs) == 1:
        return [line(nm(hs[0]))]
    return [line(nm(h), half_tag(h['name'], h['levels'], 3.6, '0')) for h in (hs[1], hs[0])]

# ---------------------------------------------------------------- A4 pages
def a4_pages(racks):
    secs = []
    for z in ('c', 'p', 'b'):
        T = TYPES[z]
        for r in racks[z]:
            bname = BRANDS[r['brand']][0]
            chunks = [[1, 2], [3, 4], [5]]
            for ci, ch in enumerate(chunks, 1):
                rows = r['tiers']
                gh = rows * 50 + (rows - 1) * 5
                pr = ('PALLETS %d–%d' % (ch[0], ch[-1])) if len(ch) > 1 else ('PALLETS %d' % ch[0])
                secs.append(
                    '<section class="pg" style="width:210mm;height:297mm">'
                    '<div style="position:absolute;left:24.5mm;top:3.2mm;width:161mm;height:6mm;display:flex;align-items:center;'
                    'justify-content:space-between;font-family:Cairo;direction:ltr;color:#111;font-weight:900;font-size:3.6mm;'
                    'white-space:nowrap"><span dir="ltr">%s · %s · RACK %d · %s</span><span dir="ltr">%s · PAGE %d/3</span></div>'
                    '<div style="position:absolute;left:24.5mm;top:18mm;width:161mm;height:%dmm;display:grid;direction:ltr;'
                    'grid-template-columns:repeat(2,78mm);grid-auto-rows:50mm;gap:5mm">%s</div>%s</section>'
                    % (T['tag'], bname, r['no'], T['code'], pr, ci, gh, rack_stickers(r, ch),
                       overlay(210, 297, 24.5, 18, len(ch), rows)))
    return secs

# ---------------------------------------------------------------- SRA3 pages
def chip(bg, txt, fs=9):
    return ('<span dir="ltr" style="background:%s;color:#fff;border-radius:9mm;padding:0 5mm;font-weight:900;font-size:%smm;'
            'line-height:1.35">%s</span>' % (bg, fs, txt))

def sra3_pages(racks):
    secs = []
    for z in ('c', 'p', 'b'):
        T = TYPES[z]
        for r in racks[z]:
            bname, bcol, _ = BRANDS[r['brand']]
            rows = r['tiers']
            gh = rows * 50 + (rows - 1) * 5
            titles = ''.join(rack_title_ar(r))
            sub = '%s · RACK #%d · LEVELS A–%s × 5 PALLETS' % (T['desc'], r['gno'], LETTERS[rows - 1])
            secs.append(
                '<section class="pg" style="width:450mm;height:320mm">'
                '<div style="position:absolute;left:20mm;top:12mm;width:410mm;height:21mm;display:flex;align-items:center;'
                'justify-content:space-between;font-family:\'Cairo\',sans-serif;color:#111;direction:ltr">'
                '<div style="display:flex;align-items:center;gap:4mm">%s%s<span dir="ltr" style="font-weight:900;font-size:13mm;'
                'line-height:1">RACK %d</span><span style="font-weight:900;font-size:12mm;line-height:1">راك %d</span></div>'
                '<div style="text-align:right;line-height:1.2;max-width:215mm">%s<div dir="ltr" style="font-weight:600;'
                'font-size:4.2mm;letter-spacing:.3mm">%s</div></div></div>'
                '<div style="position:absolute;left:20mm;top:40mm;width:410mm;height:%dmm;display:grid;direction:ltr;'
                'grid-template-columns:repeat(5,78mm);grid-auto-rows:50mm;gap:5mm">%s</div>%s</section>'
                % (chip(T['hdr'], T['tag']), chip(bcol, bname), r['no'], r['no'], titles, sub, gh,
                   rack_stickers(r, [1, 2, 3, 4, 5]), overlay(450, 320, 20, 40, 5, rows)))
    return secs

# ---------------------------------------------------------------- legend (SRA3-size page)
def summary(racks):
    rows = []
    for z in ('c', 'p', 'b'):
        T = TYPES[z]
        per = {}
        for r in racks[z]:
            per.setdefault(r['brand'], []).append(r)
        parts = []
        for br, lst in per.items():
            nm = BRANDS[br][2]
            parts.append('%s 1–%d' % (nm, len(lst)) if len(lst) > 1 else '%s 1' % nm)
        shared = [r for r in racks[z] if len(r['halves']) == 2]
        sh = ' · '.join('%s%d' % (BRANDS[r['brand']][2], r['no']) for r in shared) or '—'
        rows.append((T, len(racks[z]), ' · '.join(parts), len(shared), sh))
    return rows

def legend_page(racks):
    sample = sticker('c', 'DX', 1, 3, 2, racks['c'][0]['halves'][1]['item'], 'upper', racks['c'][0]['halves'][1]['levels'], 4)
    S = 3.1
    sx, sy = 40, 56
    def badge(n, x, y):
        return ('<div style="position:absolute;left:%.1fmm;top:%.1fmm;width:9mm;height:9mm;border-radius:50%%;background:#111;'
                'color:#FFD400;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:6mm;'
                'font-family:Cairo">%d</div>' % (x - 4.5, y - 4.5, n))
    def line(x1, y1, x2, y2):
        return ('<svg style="position:absolute;left:0;top:0" width="450mm" height="320mm" viewBox="0 0 450 320">'
                '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#111" stroke-width=".8"/></svg>' % (x1, y1, x2, y2))
    sw, sh = 78 * S, 50 * S
    xl, xr = sx - 14, sx + sw + 14
    ly = lambda m: sy + m * S
    marks = ''
    # left side: 1 header, 2 item, 5 arrow below
    for n, m in ((1, 4.5), (2, 13), (5, 29.5)):
        marks += line(xl + 4.5, ly(m), sx, ly(m)) + badge(n, xl, ly(m))
    # right side: 3 half tag, 6 arrow above, 8 pallet badge
    for n, m in ((3, 18.8), (6, 29.5), (8, 44.5)):
        marks += line(sx + sw, ly(m), xr - 4.5, ly(m)) + badge(n, xr, ly(m))
    marks += line(sx + sw / 2, sy - 6, sx + sw / 2, sy) + badge(4, sx + sw / 2, sy - 10.5)
    marks += line(sx + sw / 2, sy + sh, sx + sw / 2, sy + sh + 6) + badge(7, sx + sw / 2, sy + sh + 10.5)
    legend_items = [
        ('اسم المجموعة (الماركة) + نوع الراك ورمز المنطقة', 'BRAND GROUP · RACK TYPE · ZONE'),
        ('اسم الصنف كاملاً بالعربي والإنجليزي — صنف واحد فقط على كل ملصق', 'ONE ITEM ONLY ON EACH STICKER'),
        ('علامة النصف: تظهر في الراكات المشتركة فقط (↓ سفلي / ↑ علوي) مع حروف مستوياته', 'HALF TAG · SHARED RACKS ONLY'),
        ('رقم الراك داخل المجموعة + حرف المستوى (1C = الراك 1، المستوى C)', 'RACK No. + LEVEL LETTER (A = FLOOR LEVEL)'),
        ('سهم لأسفل = المستوى الأدنى (FLOOR = الأرض)', 'ARROW DOWN = LEVEL BELOW'),
        ('سهم لأعلى = المستوى الأعلى (TOP = القمة)', 'ARROW UP = LEVEL ABOVE'),
        ('باركود Code 128 قابل للمسح: المنطقة-المجموعة-الراك+المستوى-البالت', 'SCANNABLE · 3L-DX-1C-2'),
        ('رقم البالت داخل المستوى P1–P5', 'PALLET No. IN THE LEVEL'),
    ]
    items_html = ''
    for i, (a, e) in enumerate(legend_items):
        y = 40 + i * 14.6
        items_html += (badge(i + 1, 303, y + 5) +
                       '<div style="position:absolute;left:312mm;top:%.1fmm;width:118mm;direction:rtl;font-family:Cairo;color:#111">'
                       '<div style="font-weight:800;font-size:3.7mm;line-height:1.25">%s</div>'
                       '<div dir="ltr" style="font-weight:600;font-size:3mm;line-height:1.2;opacity:.8;text-align:left">%s</div></div>'
                       % (y, a, e))
    # rack example grid (rack 1 of cartons)
    r1 = racks['c'][0]
    ex = ('<div style="position:absolute;left:300mm;top:166mm;width:130mm;font-family:Cairo;direction:rtl;color:#111">'
          '<div style="font-weight:900;font-size:4.6mm;margin-bottom:1.5mm">مثال: راك 1 (دو · كراتين) — 4 مستويات × 5 بالتات</div>')
    for lvl in range(4, 0, -1):
        h = next(h for h in r1['halves'] if lvl in h['levels'])
        cells = ''.join('<div dir="ltr" style="width:17.5mm;height:7mm;border:.4mm solid #111;background:#FFD400;display:flex;'
                        'align-items:center;justify-content:center;font-weight:900;font-size:3.4mm">1%s·P%d</div>' % (LETTERS[lvl - 1], p)
                        for p in range(1, 6))
        col = '#111' if h['name'] == 'lower' else '#B58A00'
        ex += ('<div style="display:flex;direction:ltr;gap:1mm;margin-bottom:1mm;align-items:center">%s'
               '<div style="font-weight:800;font-size:3.2mm;direction:rtl;margin-left:2mm;white-space:nowrap;color:%s">%s</div></div>'
               % (cells, col, ('↑ علوي' if h['name'] == 'upper' else '↓ سفلي')))
    ex += '</div>'
    # summary table
    tb = ('<div style="position:absolute;left:22mm;top:236mm;width:262mm;font-family:Cairo;direction:rtl;color:#111">'
          '<div style="font-weight:900;font-size:4.6mm;margin-bottom:2mm">التوزيع: كل صنف راك لوحده، والزائد فقط يشارك مناصفة</div>'
          '<div style="display:flex;gap:4mm;direction:rtl">')
    for T, n, per, ns, shd in summary(racks):
        tb += ('<div style="flex:1;background:#fff;border:.4mm solid #111;border-radius:3mm;padding:2mm 3mm"><div style="font-weight:900;'
               'font-size:3.9mm"><span dir="ltr" style="background:%s;color:#fff;border-radius:5mm;padding:0 3mm;margin-left:2mm">%s</span>'
               '%s · %s — %d راك</div><div style="font-weight:700;font-size:3.2mm;line-height:1.35;margin-top:1mm">%s</div>'
               '<div style="font-weight:600;font-size:3mm;line-height:1.35;opacity:.85">مشتركة (%d): %s</div></div>'
               % (T['hdr'], T['tag'], T['name_ar'], T['code'], n, per, ns, shd))
    tb += '</div></div>'
    total = sum(len(r['halves']) and r['tiers'] * 5 for z in racks for r in racks[z])
    note = ('<div style="position:absolute;left:300mm;top:218mm;width:130mm;font-family:Cairo;direction:rtl;color:#111;'
            'font-weight:700;font-size:3.6mm;line-height:1.55">الإجمالي: %d ملصق · خط القص الوردي المتقطع حول كل ملصق.<br>'
            'الراك المشترك: النصف السفلي بلاصق أسود، والعلوي بلاصق بإطار — كل نصف باسم صنفه فقط، وحروف مستوياته مكتوبة على العلامة.<br>'
            'اطبع بحجم 100%% بدون «ملاءمة الصفحة» ثم قصّ على الخط الوردي.</div>' % total)
    return ('<section class="pg" data-row="legend" style="width:450mm;height:320mm;font-family:Cairo;color:#111;background:#FBF7EE;'
            'direction:ltr"><div style="position:absolute;left:18mm;top:12mm;right:18mm;display:flex;justify-content:space-between;'
            'align-items:baseline"><span dir="ltr" style="font-weight:900;font-size:7.5mm;letter-spacing:1.4mm">PALLET LOCATION STICKERS · '
            'AL-MUNAJEM · %s</span><span style="font-weight:900;font-size:13mm">ملصقات مواقع البالتات</span></div>'
            '<div style="position:absolute;left:%.1fmm;top:%.1fmm;width:%.1fmm;height:%.1fmm"><div style="transform:scale(%s);'
            'transform-origin:top left;width:78mm;height:50mm">%s</div></div>%s%s%s%s%s</section>'
            % (VERSION.upper(), sx, sy, sw, sh, S, sample, marks, items_html, ex, tb, note)), total

def build(out_dir):
    racks = build_racks()
    os.makedirs(out_dir, exist_ok=True)
    leg, total = legend_page(racks)
    head = '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>'
    stamp = '<!-- VERSION: %s | %s -->' % (VERSION, DATE)
    # SRA3
    sra = (stamp + head % ('ملصقات مواقع البالتات SRA3', page_css(450, 320)) + leg + ''.join(sra3_pages(racks)) + FIT_JS + '</body></html>')
    p1 = os.path.join(out_dir, 'almunajem_location_stickers_%s_SRA3_%s.html' % (VERSION, DATE))
    open(p1, 'w', encoding='utf-8').write(sra)
    # A4 : legend page = scaled SRA3 legend + notes
    leg_a4 = ('<section class="pg" style="width:210mm;height:297mm;background:#FBF7EE;font-family:Cairo;direction:ltr">'
              '<div style="position:absolute;left:1.5mm;top:8mm;width:207mm;height:147.2mm;overflow:hidden"><div style="transform:scale(0.46);'
              'transform-origin:top left;width:450mm;height:320mm">%s</div></div>'
              '<div style="position:absolute;left:12mm;top:165mm;width:186mm;direction:rtl;font-family:Cairo;color:#111;font-weight:700;'
              'font-size:3.8mm;line-height:1.6"><b>طريقة الطباعة (A4):</b><br>اطبع بحجم 100%% بدون «ملاءمة الصفحة».<br>'
              'كل صفحة: عمودان (بالتان) × مستويات الراك — 8 ملصقات للكراتين و10 للبلاستيك والعلب، بمقاس 78×50 مم.<br>'
              'لكل راك 3 صفحات: البالتات 1–2، ثم 3–4، ثم 5. قصّ على الخط الوردي المتقطع.<br>'
              'الباركود: تأكد أن الطابعة لا تُصغّر الصفحة.</div></section>' % leg.replace('<section class="pg"', '<div class="pg"', 1).replace('</section>', '</div>'))
    a4 = (stamp + head % ('ملصقات مواقع البالتات A4', page_css(210, 297)) + leg_a4 + ''.join(a4_pages(racks)) + FIT_JS + '</body></html>')
    p2 = os.path.join(out_dir, 'almunajem_location_stickers_%s_A4_%s.html' % (VERSION, DATE))
    open(p2, 'w', encoding='utf-8').write(a4)
    return racks, total, (p1, p2)

def distribution_md(racks):
    L = ['# توزيع الراكات — %s' % VERSION, '',
         'كل صنف له راك لوحده؛ الأصناف الزائدة فقط تشارك راكاً مناصفة (سفلي/علوي). الراك رقم داخل مجموعته، والمستوى حرف (A = الأرض).', '']
    for z in ('c', 'p', 'b'):
        T = TYPES[z]
        L += ['## %s %s — %s (%d مستويات × 5 بالتات)' % (T['tag'], T['name_ar'], T['code'], T['tiers']), '',
              '| # | الماركة | الراك | الصنف (السفلي ↓) | الصنف (العلوي ↑) |', '|---|---|---|---|---|']
        for r in racks[z]:
            hs = r['halves']
            fmt = lambda h: ('%s %s (%s)' % (h['item']['ar'], h['item']['size'], LETTERS[h['levels'][0] - 1] + '–' + LETTERS[h['levels'][-1] - 1])
                             if h['item'] else 'احتياطي')
            if len(hs) == 2:
                L.append('| %d | %s | %d | %s | %s |' % (r['gno'], BRANDS[r['brand']][2], r['no'], fmt(hs[0]), fmt(hs[1])))
            else:
                L.append('| %d | %s | %d | %s (راك كامل A–%s) | — |' % (r['gno'], BRANDS[r['brand']][2], r['no'],
                         (hs[0]['item']['ar'] + ' ' + hs[0]['item']['size']) if hs[0]['item'] else 'احتياطي', LETTERS[r['tiers'] - 1]))
        L.append('')
    return '\n'.join(L)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    racks, total, paths = build(out)
    open(os.path.join(out, 'DISTRIBUTION_%s.md' % VERSION), 'w', encoding='utf-8').write(distribution_md(racks))
    print('stickers:', total, 'racks:', {z: len(v) for z, v in racks.items()}); print(*paths, sep='\n')
