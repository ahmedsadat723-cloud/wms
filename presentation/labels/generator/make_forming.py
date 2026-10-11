#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Al-Munajem · FORMING section (zone 2, FORM) — complete print file, modern visual language, bilingual AR/EN.
39 racks (19 right x 175 cm + 20 left x 195 cm) · 5 levels (A-E) · 6 pallets deep = 30 pallets per rack · 1170 locations.
Colour = BRAND/supplier (Kerry, Esnad, Symrise, IFFCO, Almunajem, Amber). usage: python3 make_forming.py <out_dir>"""
import os, sys, json, html, re
import make_stickers as m
import make_zone1_system as z
import make_master as mm

esc = html.escape
VER, DATE = 'v1', '2026-10-11'
HERE = os.path.dirname(os.path.abspath(__file__))
LETTERS = 'ABCDE'
DEEP, LEVELS = 6, 5
INK, SLATE, MUTE, ORG = '#0F172A', '#334155', '#64748B', '#E65100'

BRANDS = {  # key: (EN, AR, colour)
    'KERRY': ('KERRY', 'كيري', '#E8590C'), 'ESNAD': ('ESNAD', 'إسناد', '#5F3DC4'), 'SYMRISE': ('SYMRISE', 'سيمرايز', '#C2255C'),
    'IFFCO': ('IFFCO', 'إيفكو', '#1971C2'), 'ALMUNAJEM': ('AL MUNAJEM', 'المنجم', '#2F9E44'), 'AMBER': ('AMBER', 'عنبر', '#B7791F'),
}
TYPES_F = {'CR': ('CRUMBS', 'بقسماط'), 'BR': ('BREADING MIX', 'خلطة تغطية'), 'BT': ('BATTER', 'باتر'), 'FL': ('FLAVOUR', 'نكهة'), 'OL': ('OIL', 'زيت')}
# code -> (brand, type, racks on its side)  — racks per item: right 19 / left 20 (oils = heaviest, 4 racks each)
PLAN = [('R', [('FORM-0001', 'ESNAD', 'CR', 3), ('FORM-0002', 'KERRY', 'CR', 3), ('FORM-0003', 'KERRY', 'BR', 3), ('FORM-0004', 'KERRY', 'CR', 3),
               ('FORM-0005', 'KERRY', 'CR', 3), ('FORM-0006', 'KERRY', 'BT', 2), ('FORM-0007', 'KERRY', 'BR', 2)], 175),
        ('L', [('FORM-0008', 'SYMRISE', 'FL', 2), ('FORM-0009', 'SYMRISE', 'FL', 2), ('FORM-0010', 'IFFCO', 'OL', 4), ('FORM-0011', 'IFFCO', 'OL', 4),
               ('FORM-0012', 'ALMUNAJEM', 'OL', 4), ('FORM-0013', 'AMBER', 'OL', 4)], 195)]
NAME_FIX = {'FORM-0010': 'FRYLITE BLENDED OIL NOOR', 'FORM-0009': 'AROMAX FLAVOR INTENSIVE'}

def clean(s):
    return re.sub(r'\s+', ' ', s.replace('/', ' ') if s.startswith('/') else s).strip()

def load():
    raw = json.load(open(os.path.join(HERE, 'assets', 'forming_items.json'), encoding='utf-8'))
    items, racks, n_item = {}, [], 0
    for side, lst, h in PLAN:
        no = 0
        for code, br, ty, cnt in lst:
            n_item += 1
            r = raw[code]
            it = dict(code=code, no=n_item, en=NAME_FIX.get(code, clean(r['nameEn'])), ar=clean(r['cat']), brand=br, type=ty, side=side)
            items[code] = it
            for _ in range(cnt):
                no += 1
                racks.append(dict(side=side, no=no, item=it, h=h, gno=len(racks) + 1, id='%s%02d' % (side, no)))
    return items, racks

ITEMS, RACKS = load()
loc = lambda r, L, pos: '2%s-%02d%s%d' % (r['side'], r['no'], L, pos)

# ---------------------------------------------------------------- css (modern)
CSS_F = """
.fm{font-family:'Cairo',sans-serif;color:%(ink)s}
.fm .h1{font-weight:900;letter-spacing:-.2mm}
.chip{display:inline-flex;align-items:center;gap:1.4mm;border-radius:99mm;padding:.2mm 2.6mm;font-weight:800;line-height:1.5;white-space:nowrap}
.tile{background:#fff;border:.35mm solid #E2E8F0;border-radius:4mm;box-shadow:0 .4mm 1.4mm #0f172a14}
.fmpage{background:#F8FAFC}
.fi{position:absolute;border:0;background:transparent;font:800 14pt 'Cairo',sans-serif;color:%(ink)s;padding:0 3mm;outline:0;width:100%%;height:100%%}
.fi:focus{background:#FFF7E0}
@media print{.fi{background:transparent}}
""" % dict(ink=INK)

def tag(en, ar, bg=INK, fg='#fff', fs=3):
    return '<span class="chip" style="background:%s;color:%s;font-size:%smm"><span dir="ltr">%s</span><span dir="rtl">%s</span></span>' % (bg, fg, fs, esc(en), esc(ar))

def bchip(b, fs=3):
    be, ba, bc = BRANDS[b]
    return '<span class="chip" style="background:%s;color:#fff;font-size:%smm"><span dir="ltr">%s</span><span>|</span><span dir="rtl">%s</span></span>' % (bc, fs, be, ba)

def sec(cls, pid, inner, extra=''):
    return '<section class="pg %s fm fmpage" id="%s" %s>%s</section>' % (cls, pid, extra, inner)

def head(en, ar, sub_en='', sub_ar=''):
    return ('<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:8mm;margin-bottom:4mm">'
            '<div><div class="h1" dir="ltr" style="font-size:6.4mm">%s</div><div dir="ltr" style="font-size:3.2mm;font-weight:600;color:%s">%s</div></div>'
            '<div style="text-align:right"><div class="h1" dir="rtl" style="font-size:7.2mm">%s</div><div dir="rtl" style="font-size:3.4mm;font-weight:600;color:%s">%s</div></div></div>'
            % (esc(en), MUTE, esc(sub_en), esc(ar), MUTE, esc(sub_ar)))

# ---------------------------------------------------------------- page 1: overview
def tiles():
    t = [('39', 'RACKS', 'راك'), ('5', 'LEVELS A–E', 'مستويات'), ('6', 'PALLETS DEEP', 'بالت بالعمق'), ('30', 'PALLETS / RACK', 'بالت للراك'), ('1,170', 'LOCATIONS', 'موقع')]
    return ''.join('<div class="tile" style="flex:1;padding:3mm 4mm;text-align:center"><div style="font-weight:900;font-size:11mm;line-height:1;color:%s">%s</div>'
                   '<div dir="ltr" style="font-weight:800;font-size:3mm;color:%s">%s</div><div dir="rtl" style="font-weight:800;font-size:3.4mm">%s</div></div>' % (ORG, n, SLATE, e, a) for n, e, a in t)

def strip_side(side):
    rl = [r for r in RACKS if r['side'] == side]
    cw = 273.0 / 20
    cells = ''.join('<div style="width:%.2fmm;flex:none;padding:0 .5mm"><div style="height:21mm;background:%s;border-radius:2.2mm;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1.05;font-weight:900">'
                    '<span dir="ltr" style="font-size:4.6mm">%s</span><span dir="ltr" style="font-size:2.3mm;opacity:.92">#%d</span></div></div>'
                    % (cw, BRANDS[r['item']['brand']][2], r['id'], r['item']['no']) for r in rl)
    en = 'RIGHT SIDE · 19 racks · height 175 cm' if side == 'R' else 'LEFT SIDE · 20 racks · height 195 cm'
    ar = 'الجهة اليمين · 19 راك · الارتفاع 175 سم' if side == 'R' else 'الجهة اليسار · 20 راك · الارتفاع 195 سم'
    return ('<div style="margin-bottom:5mm"><div style="display:flex;justify-content:space-between;font-weight:900;font-size:4mm;margin-bottom:1.4mm"><span dir="ltr">%s</span><span dir="rtl">%s</span></div>'
            '<div style="display:flex;direction:ltr">%s</div></div>' % (en, ar, cells))

def legend():
    rows = ''
    for it in ITEMS.values():
        rows += ('<div style="display:flex;align-items:center;gap:2mm;padding:.6mm 0;border-bottom:.2mm solid #E2E8F0"><span style="width:5.4mm;height:5.4mm;border-radius:1.4mm;background:%s;color:#fff;font-weight:900;font-size:2.8mm;display:flex;align-items:center;justify-content:center;flex:none" dir="ltr">%d</span>'
                 '<span dir="ltr" style="flex:1;font-size:2.7mm;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">%s</span><span dir="rtl" style="flex:1;font-size:2.9mm;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">%s</span>'
                 '<span dir="ltr" style="width:17mm;font-size:2.6mm;font-weight:800;color:%s">%s</span></div>'
                 % (BRANDS[it['brand']][2], it['no'], esc(it['en']), esc(it['ar']), MUTE,
                    ','.join(r['id'] for r in RACKS if r['item'] is it).replace(',', ' ') if False else '%s×%d' % (it['side'], sum(1 for r in RACKS if r['item'] is it))))
    return rows

def overview():
    inner = ('<div style="position:absolute;left:12mm;right:12mm;top:9mm">%s<div style="display:flex;gap:4mm;margin-bottom:5mm">%s</div>%s%s'
             '<div style="column-count:2;column-gap:8mm">%s</div></div>'
             % (head('FORMING SECTION · ZONE 2 · FORM', 'قسم التشكيل · المنطقة 2 · FORM', 'Flour · breading · batter · flavours · oils — color = brand', 'بقسماط · خلطات تغطية · باتر · نكهات · زيوت — اللون = الماركة'),
                tiles(), strip_side('R'), strip_side('L'), legend()))
    return sec('l', 'f-overview', inner)

# ---------------------------------------------------------------- page 2: method + key
def method():
    paras = [
        ('المنطقة 2 «التشكيل»: 39 راك — اليمين 19 راك (ارتفاع 175 سم) واليسار 20 راك (ارتفاع 195 سم)، بينهما باب الطوارئ.',
         'Zone 2 “Forming”: 39 racks — right 19 (175 cm high) and left 20 (195 cm high), with the emergency door between them.'),
        ('كل راك 5 مستويات (A = الأرض ثم B C D E) وفي كل مستوى 6 بالتات بالعمق = 30 بالت للراك، والإجمالي 1,170 موقعاً.',
         'Each rack has 5 levels (A = floor, then B C D E) with 6 pallets deep per level = 30 pallets per rack, 1,170 locations in total.'),
        ('اللون = الماركة / المورّد: كيري · إسناد (اليمين) — سيمرايز · إيفكو · المنجم · عنبر (اليسار)، فلا يختلط صنف ماركة بماركة أخرى.',
         'Colour = brand / supplier: Kerry · Esnad (right) — Symrise · IFFCO · Al Munajem · Amber (left), so brands never mix.'),
        ('كل صنف (13 صنفاً) يأخذ 2 إلى 4 راكات متجاورة؛ الزيوت (الأثقل) 4 راكات لكل صنف، والنكهات راكان لكل صنف.',
         'Each of the 13 items takes 2–4 adjacent racks; oils (the heaviest) 4 racks each, flavours 2 racks each.'),
        ('ليبل لكل مستوى (A–E) بنسختين، عليه الراك والصنف والسهمان (أعلى/أسفل) ونطاق البالتات P1–P6 لكل مستوى.',
         'One label per level (A–E), two copies, showing rack, item, the UP/DOWN arrows and the level’s pallets P1–P6.'),
        ('كل بالت يحمل ورقة بالت مرقمة P1–P30 (للراك الواحد) فيها الماركة والموقع والصنف وحقول الاستلام القابلة للتعبئة.',
         'Every pallet carries a numbered pallet paper P1–P30 (per rack) with brand, location, item and fillable receiving fields.'),
        ('رمز الموقع: 2R-07B3 = المنطقة 2 · اليمين · الراك 07 · المستوى B · الموضع 3 (و L لليسار).',
         'Location code: 2R-07B3 = zone 2 · right · rack 07 · level B · position 3 (L = left).'),
    ]
    rows = ''.join('<div style="display:flex;gap:6mm;align-items:flex-start;padding:2.4mm 0;border-bottom:.25mm solid #E2E8F0"><div style="width:7mm;height:7mm;border-radius:2mm;background:%s;color:#fff;font-weight:900;display:flex;align-items:center;justify-content:center;flex:none">%d</div>'
                   '<div dir="ltr" style="flex:1;font-size:3.5mm;line-height:1.35;font-weight:600;color:%s">%s</div><div dir="rtl" style="flex:1;font-size:4mm;line-height:1.4;font-weight:800">%s</div></div>'
                   % (ORG, i, SLATE, esc(e), esc(a)) for i, (a, e) in enumerate(paras, 1))
    key = ''.join('<div class="tile" style="padding:2mm 3mm;display:flex;align-items:center;gap:2mm"><span style="width:8mm;height:8mm;border-radius:2mm;background:%s"></span><div><div dir="ltr" style="font-weight:900;font-size:3.2mm;line-height:1">%s</div><div dir="rtl" style="font-weight:800;font-size:3.2mm;line-height:1.1">%s</div></div></div>'
                  % (c, e, a) for e, a, c in BRANDS.values())
    inner = ('<div style="position:absolute;left:14mm;right:14mm;top:10mm">%s%s<div style="display:flex;gap:3mm;margin-top:5mm">%s</div></div>'
             % (head('DISTRIBUTION METHOD', 'طريقة التوزيع', 'Forming section — how the racks are used', 'قسم التشكيل — كيف تُستخدم الراكات'), rows, key))
    return sec('l', 'f-method', inner)

# ---------------------------------------------------------------- tables (right / left)
def table(side):
    rl = [r for r in RACKS if r['side'] == side]
    rows = ''
    for r in rl:
        it = r['item']
        be, ba, bc = BRANDS[it['brand']]
        te, ta = TYPES_F[it['type']]
        rows += ('<tr><td style="font-weight:900;text-align:center" dir="ltr">%s</td><td style="text-align:center;font-weight:800" dir="ltr">%d</td><td style="background:%s;color:#fff;font-weight:900;text-align:center" dir="ltr">%s | %s</td>'
                 '<td dir="ltr" style="font-weight:700">%s</td><td dir="rtl" style="font-weight:800">%s</td><td style="text-align:center;font-weight:800" dir="ltr">%s · %s</td><td style="text-align:center;font-weight:800" dir="ltr">A–E · P1–P30</td></tr>'
                 % (r['id'], it['no'], bc, be, ba, esc(it['code'] + ' · ' + it['en']), esc(it['ar']), te, ta))
    hd = ('<tr style="background:%s;color:#fff"><th>RACK<br>راك</th><th>ITEM #<br>الصنف</th><th>BRAND · الماركة</th><th dir="ltr">ITEM (EN)</th><th dir="rtl">الصنف (عربي)</th><th>TYPE · النوع</th><th>LEVELS · PALLETS</th></tr>' % INK)
    en, ar = (('RIGHT · 19 racks · 175 cm', 'اليمين · 19 راك · 175 سم') if side == 'R' else ('LEFT · 20 racks · 195 cm', 'اليسار · 20 راك · 195 سم'))
    inner = ('<div style="position:absolute;left:12mm;right:12mm;top:8mm">%s<table class="ft" style="border-collapse:collapse;width:100%%;font-size:%smm;line-height:1.1">%s%s</table>'
             '<style>.ft td,.ft th{border:.2mm solid #CBD5E1;padding:.4mm 1.6mm}.ft tr:nth-child(even) td:not([style*=background]){background:#F8FAFC}</style></div>'
             % (head('RACK TABLE — ' + en, 'جدول الراكات — ' + ar), 2.9 if side == 'L' else 3.0, hd, rows))
    return sec('l', 'f-table-' + side, inner)

# ---------------------------------------------------------------- rack-level sticker (78 x 50 mm), modern
YEL, YEL2 = '#FFD400', '#F2C200'
ICONS = {  # 24x24 simple symbols, drawn in white on the brand circle
    'OL': '<path d="M12 2C12 2 5 10 5 15a7 7 0 0014 0C19 10 12 2 12 2z" fill="#fff"/><path d="M9 15a3 3 0 003 3" stroke="%(c)s" stroke-width="1.6" fill="none" stroke-linecap="round"/>',
    'FL': '<path d="M12 1l2.6 8.4L23 12l-8.4 2.6L12 23l-2.6-8.4L1 12l8.4-2.6z" fill="#fff"/>',
    'CR': '<circle cx="7" cy="8" r="2.6" fill="#fff"/><circle cx="15" cy="6" r="2.2" fill="#fff"/><circle cx="18" cy="13" r="2.8" fill="#fff"/><circle cx="10" cy="14" r="3" fill="#fff"/><circle cx="6" cy="19" r="2" fill="#fff"/><circle cx="15" cy="19" r="2.2" fill="#fff"/>',
    'BR': '<path d="M5 8h14l2 13H3z" fill="#fff"/><path d="M8 8c0-3 1.5-5 4-5s4 2 4 5" stroke="#fff" stroke-width="2" fill="none"/><path d="M8 14h8" stroke="%(c)s" stroke-width="1.8"/>',
    'BT': '<path d="M3 11h18a8 8 0 01-8 9h-2a8 8 0 01-8-9z" fill="#fff"/><path d="M8 8c1-3 3-3 4 0s3 3 4 0" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>',
}

def icon(ty, bc, size):
    return ('<span style="width:%smm;height:%smm;border-radius:50%%;background:%s;border:.5mm solid %s;display:inline-flex;align-items:center;justify-content:center;flex:none"><svg viewBox="0 0 24 24" width="%smm" height="%smm">%s</svg></span>'
            % (size, size, bc, INK, size * .62, size * .62, ICONS[ty] % dict(c=bc)))

def arr(down, col=YEL):
    st = ' style="transform:rotate(180deg)"' if down else ''
    return ('<svg%s viewBox="0 0 100 110" width="5.4mm" height="5.9mm"><polygon points="50,2 98,52 68,52 68,108 32,108 32,52 2,52" fill="%s"/></svg>' % (st, col))

def fside(down, letter, w_en, w_ar):
    return ('<div style="width:14.5mm;display:flex;flex-direction:column;align-items:center;gap:.5mm"><div style="width:9.4mm;height:9.4mm;border-radius:50%%;background:%s;display:flex;align-items:center;justify-content:center">%s</div>'
            '<span dir="ltr" style="font-weight:900;font-size:3.1mm;line-height:1">%s</span><span style="display:flex;gap:.9mm;white-space:nowrap;font-weight:800;font-size:2.2mm;line-height:1"><span dir="ltr">%s</span><span dir="rtl">%s</span></span></div>'
            % (INK, arr(down), letter, w_en, w_ar))

def fbar(code, h, w):
    return m.barcode_svg(code, 9).replace('width="56mm" height="9mm"', 'width="%smm" height="%smm" preserveAspectRatio="none"' % (w, h)).replace('fill="%s"' % m.INK, 'fill="%s"' % INK)

def fsticker(r, lv):
    it = r['item']
    bc = BRANDS[it['brand']][2]
    L = LETTERS[lv - 1]
    dn = ('FLOOR', 'DOWN', 'أسفل') if lv == 1 else (LETTERS[lv - 2], 'DOWN', 'أسفل')
    up = ('TOP', 'UP', 'أعلى') if lv == LEVELS else (LETTERS[lv], 'UP', 'أعلى')
    code = '2%s-%02d%s' % (r['side'], r['no'], L)
    p0 = (lv - 1) * DEEP + 1
    stripes = 'background:repeating-linear-gradient(135deg,%s 0 1.1mm,transparent 1.1mm 2.2mm)' % YEL
    top = ('<div style="height:7.6mm;background:%s;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 0 0 3mm;font-weight:900;white-space:nowrap;position:relative;border-bottom:.5mm solid %s">'
           '<span style="display:flex;gap:1.4mm;align-items:center;font-size:3mm"><span dir="ltr">FORMING</span><span>·</span><span dir="rtl">التشكيل</span></span>'
           '<span style="display:flex;align-items:center;height:100%%"><span dir="ltr" style="font-size:3.3mm;letter-spacing:.2mm;padding-right:2mm">%s</span><span style="width:13mm;height:100%%;%s"></span></span></div>'
           % (bc, INK, code[:2] + '-' + code[3:5], stripes))
    name = ('<div style="height:10.8mm;padding:0 2.2mm;display:flex;align-items:center;gap:2mm;background:%s;border-bottom:.5mm solid %s;overflow:hidden">%s'
            '<div style="flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center">'
            '<div data-fit dir="rtl" style="white-space:nowrap;font-weight:900;font-size:3.3mm;line-height:1.15">%s</div>'
            '<div data-fit dir="ltr" style="white-space:nowrap;font-weight:700;font-size:2.4mm;line-height:1.15">%s</div></div></div>'
            % (YEL2, INK, icon(it['type'], bc, 7.4), esc(it['ar']), esc(it['en'])))
    mid = ('<div style="flex:1;display:flex;align-items:center;justify-content:space-between;padding:0 2mm 0 2mm;position:relative">%s'
           '<div style="display:flex;align-items:center;gap:1.6mm"><div dir="ltr" style="background:%s;color:#fff;font-weight:900;font-size:4.8mm;line-height:1;padding:.9mm 1.8mm;border-radius:1.8mm">%s</div>'
           '<div dir="ltr" style="width:17mm;height:17mm;border-radius:3.4mm;background:%s;color:#fff;border:.8mm solid %s;box-shadow:1mm 1mm 0 %s;font-weight:900;font-size:14mm;line-height:15.4mm;text-align:center">%s</div></div>%s</div>'
           % (fside(True, dn[0], dn[1], dn[2]), INK, r['id'], bc, INK, INK, L, fside(False, up[0], up[1], up[2])))
    pill = lambda t, bg, fg, bd='': '<span dir="ltr" class="chip" style="background:%s;color:%s;%sfont-size:2.9mm;padding:0 1.8mm">%s</span>' % (bg, fg, bd, t)
    bot = ('<div style="height:8.6mm;display:flex;align-items:center;justify-content:space-between;padding:0 2.2mm 1mm;gap:2mm"><div style="display:flex;gap:1.2mm">%s%s</div>'
           '<div style="display:flex;flex-direction:column;align-items:center;gap:.2mm;background:#fff;border-radius:1.4mm;padding:.5mm 1.4mm .3mm;border:.3mm solid %s">%s<span dir="ltr" style="font-weight:800;font-size:2.2mm;letter-spacing:.5mm;line-height:1">%s</span></div></div>'
           % (pill('P%d–P%d' % (p0, p0 + DEEP - 1), INK, YEL), pill('%s1–%s%d' % (L, L, DEEP), '#fff', INK, 'border:.3mm solid %s;' % INK), INK, fbar(code, 3.8, 24), code))
    return ('<div class="stk" style="width:78mm;height:50mm;box-sizing:border-box;background:%s;border:1.1mm solid %s;border-radius:4mm;overflow:hidden;direction:ltr;display:flex;flex-direction:column;font-family:\'Cairo\',sans-serif;color:%s;position:relative">%s%s%s%s</div>'
            % (YEL, INK, INK, top, name, mid, bot))

def label_pages():
    out = []
    for r in RACKS:
        cells = ''.join(fsticker(r, lv) for lv in range(LEVELS, 0, -1) for _ in range(2))
        it = r['item']
        hd = ('<div style="position:absolute;left:24.5mm;top:3.2mm;width:161mm;height:10mm;display:flex;justify-content:space-between;align-items:flex-start;font-weight:900;font-size:3.4mm;line-height:1.15;color:%s;white-space:nowrap">'
              '<span dir="ltr">FORMING · RACK %s · %s · LEVELS A–E<br><span style="font-weight:700;font-size:3mm">RACK-LEVEL LABELS · 2 PER LEVEL</span></span>'
              '<span dir="rtl" style="text-align:right">التشكيل · راك %s · %s · المستويات A–E<br><span style="font-weight:700;font-size:3mm">ملصقات مستويات الراك · 2 لكل مستوى</span></span></div>'
              % (INK, r['id'], BRANDS[it['brand']][0], r['id'], BRANDS[it['brand']][1]))
        out.append(('<section class="pg p fm" id="f-lbl-%s" style="background:#fff">%s<div style="position:absolute;left:24.5mm;top:18mm;width:161mm;height:%dmm;display:grid;direction:ltr;grid-template-columns:repeat(2,78mm);grid-auto-rows:50mm;gap:5mm">%s</div>%s</section>'
                    % (r['id'], hd, 5 * 50 + 4 * 5, cells, m.overlay(210, 297, 24.5, 18, 2, 5)), 'f-lbl-' + r['id'], 'Forming rack labels · rack %s · %s' % (r['id'], it['en'][:34]), 'ليبل راك التشكيل · راك %s · %s' % (r['id'], it['ar'][:30])))
    return out

# ---------------------------------------------------------------- big item labels (A4 landscape)
def big_pages():
    out = []
    for it in ITEMS.values():
        be, ba, bc = BRANDS[it['brand']]
        te, ta = TYPES_F[it['type']]
        rl = [r['id'] for r in RACKS if r['item'] is it]
        rng = '%s – %s' % (rl[0], rl[-1])
        side_en, side_ar = ('RIGHT · 175 cm', 'اليمين · 175 سم') if it['side'] == 'R' else ('LEFT · 195 cm', 'اليسار · 195 سم')
        stripes = 'background:repeating-linear-gradient(135deg,%s 0 4mm,transparent 4mm 8mm)' % YEL
        inner = ('<div style="position:absolute;left:10mm;top:12mm;width:277mm;height:186mm;background:%s;border:4mm solid %s;border-radius:14mm;overflow:hidden;display:flex;flex-direction:column;direction:ltr;box-sizing:border-box">'
                 '<div style="height:36mm;background:%s;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 0 0 12mm;font-weight:900;white-space:nowrap;border-bottom:1.6mm solid %s">'
                 '<span style="font-size:11mm;display:flex;gap:4mm;align-items:baseline"><span dir="ltr">FORMING</span><span>·</span><span dir="rtl">التشكيل</span></span>'
                 '<span style="display:flex;align-items:center;height:100%%;gap:6mm"><span style="font-size:11mm;display:flex;gap:4mm;align-items:baseline"><span dir="ltr">%s</span><span>|</span><span dir="rtl">%s</span></span><span style="width:40mm;height:100%%;%s"></span></span></div>'
                 '<div style="flex:1;background:%s;display:flex;align-items:center;gap:12mm;padding:0 14mm;border-bottom:1.6mm solid %s">%s'
                 '<div style="flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4mm">'
                 '<div data-fit dir="rtl" style="white-space:nowrap;font-weight:900;font-size:26mm;line-height:1.1">%s</div>'
                 '<div data-fit dir="ltr" style="white-space:nowrap;font-weight:800;font-size:15mm;line-height:1.1">%s</div>'
                 '<div style="display:flex;gap:6mm;margin-top:1mm"><span class="chip" style="background:%s;color:%s;font-size:7.4mm;padding:0 7mm"><span dir="ltr">%s</span><span dir="rtl">%s</span></span>'
                 '<span class="chip" style="background:#fff;color:%s;border:.8mm solid %s;font-size:7.4mm;padding:0 7mm" dir="ltr">%s</span></div></div></div>'
                 '<div style="height:40mm;display:flex;align-items:center;justify-content:space-between;padding:0 14mm 3mm">'
                 '<div style="display:flex;flex-direction:column"><span dir="ltr" style="font-weight:800;font-size:5.4mm;white-space:nowrap">%s</span><span dir="rtl" style="font-weight:800;font-size:5.4mm;white-space:nowrap">%s</span></div>'
                 '<div style="display:flex;align-items:center;gap:6mm"><div dir="ltr" style="background:%s;color:#fff;border:1.2mm solid %s;box-shadow:2mm 2mm 0 %s;border-radius:6mm;font-weight:900;font-size:15mm;line-height:1;padding:1mm 6mm;white-space:nowrap">%s</div>'
                 '<span style="font-weight:800;font-size:6.4mm;line-height:1.1"><span dir="ltr">RACKS</span><br><span dir="rtl">الراكات</span></span></div>'
                 '<div style="display:flex;flex-direction:column;align-items:center;gap:1mm;background:#fff;border-radius:3mm;padding:2mm 4mm;border:.6mm solid %s">%s<span dir="ltr" style="font-weight:800;font-size:5mm;letter-spacing:2mm">%s</span></div></div></div>'
                 % (YEL, INK, bc, INK, esc(be), esc(ba), stripes, YEL2, INK, icon(it['type'], bc, 46), esc(it['ar']), esc(it['en']),
                    INK, YEL, te, ta, INK, INK, it['code'], esc(side_en), esc(side_ar), bc, INK, INK, rng, INK, fbar(it['code'], 11, 70), it['code']))
        out.append((sec('l', 'f-big-' + it['code'], inner).replace('fm fmpage"', 'fm" style="background:#fff"', 1) if False else sec('l', 'f-big-' + it['code'], inner), 'f-big-' + it['code'], 'Big item label · %s' % it['en'][:40], 'ليبل صنف كبير · %s' % it['ar'][:34]))
    return out

# ---------------------------------------------------------------- pallet paper (A4 portrait), modern + fillable fields (mm layout)
FIELDS = [  # key, EN, AR, x, y, w, h
    ('DATE_OF_REC', 'DATE OF REC', 'تاريخ الاستلام', 10, 168, 92, 25), ('EXPIRY_DATE', 'EXPIRY DATE', 'تاريخ الانتهاء', 108, 168, 92, 25),
    ('QUANTITY', 'QUANTITY', 'الكمية', 10, 197, 92, 25), ('CONTAINER_NO', 'CONTAINER NO.', 'رقم الحاوية', 108, 197, 92, 25),
    ('FORKLIFT_OPER', 'FORKLIFT OPER.', 'سائق الرافعة', 10, 226, 92, 25), ('REC_FOREMAN', 'REC. FOREMAN', 'مراقب الاستلام', 108, 226, 92, 25),
    ('RECEIVING_OFFICER', 'RECEIVING OFFICER', 'مسؤول الاستلام', 10, 257, 92, 28), ('WAREHOUSE_SUPERVISOR', 'WAREHOUSE SUPERVISOR', 'مشرف المستودع', 108, 257, 92, 28),
]
LABEL_H = 7.5

def pallet_page(r, n):
    it = r['item']
    be, ba, bc = BRANDS[it['brand']]
    te, ta = TYPES_F[it['type']]
    lv = (n - 1) // DEEP + 1
    L = LETTERS[lv - 1]
    pos = (n - 1) % DEEP + 1
    lc = loc(r, L, pos)
    a = lambda x, y, w, h, inner, st='': '<div style="position:absolute;left:%smm;top:%smm;width:%smm;height:%smm;%s">%s</div>' % (x, y, w, h, st, inner)
    o = a(10, 10, 34, 24, '', 'background:var(--logo) left center/contain no-repeat')
    o += a(100, 10, 100, 24, '<div dir="ltr" style="font-weight:900;font-size:8mm;line-height:1">PALLET LABEL</div><div dir="rtl" style="font-weight:900;font-size:8mm;line-height:1.1">ليبل بالت</div>'
           '<div style="margin-top:1mm">%s</div>' % tag('FORMING · ZONE 2', 'التشكيل · المنطقة 2', INK, '#fff', 3), 'text-align:right;display:flex;flex-direction:column;align-items:flex-end')
    o += a(10, 38, 190, 30, '<div style="display:flex;flex-direction:column;justify-content:center;height:100%%;padding:0 8mm;color:#fff"><div style="display:flex;justify-content:space-between;align-items:baseline"><span dir="ltr" style="font-weight:900;font-size:13mm;line-height:1.1">%s</span><span dir="rtl" style="font-weight:900;font-size:13mm;line-height:1.1">%s</span></div>'
           '<div style="display:flex;justify-content:space-between;font-weight:700;font-size:3.6mm"><span dir="ltr">%s</span><span dir="rtl">%s</span></div></div>' % (esc(be), esc(ba), 'BRAND · SUPPLIER', 'الماركة · المورّد'),
           'background:%s;border-radius:6mm' % bc)
    o += a(10, 72, 100, 60, '<div dir="ltr" style="font-weight:900;font-size:64mm;line-height:60mm;color:#fff;text-align:center;letter-spacing:-2mm">P%d</div>' % n, 'background:%s;border-radius:6mm' % INK)
    o += a(114, 72, 86, 60, ('<div style="padding:5mm 6mm;display:flex;flex-direction:column;justify-content:space-between;height:100%%"><div style="display:flex;justify-content:space-between;font-weight:800;font-size:3.2mm;color:%s"><span dir="ltr">LOCATION</span><span dir="rtl">الموقع</span></div>'
           '<div dir="ltr" style="font-weight:900;font-size:13mm;line-height:1;color:%s;text-align:center">%s</div>'
           '<div style="text-align:center;line-height:1.3"><div dir="ltr" style="font-weight:800;font-size:3.4mm">RACK %s · LEVEL %s · POSITION %d</div><div dir="rtl" style="font-weight:800;font-size:3.6mm">راك %s · مستوى %s · موضع %d</div></div></div>'
           % (MUTE, bc, lc, r['id'], L, pos, r['id'], L, pos)), 'background:#fff;border:.5mm solid %s;border-radius:6mm' % bc)
    o += a(10, 136, 190, 28, ('<div style="padding:3mm 7mm;display:flex;justify-content:space-between;align-items:center;height:100%%;gap:6mm"><div style="min-width:0"><div dir="ltr" style="font-weight:800;font-size:3mm;color:%s">PRODUCT · %s</div>'
           '<div dir="ltr" style="font-weight:800;font-size:5mm;line-height:1.15">%s</div></div><div style="text-align:right;min-width:0"><div dir="rtl" style="font-weight:800;font-size:3mm;color:%s">المنتج · %s</div><div dir="rtl" style="font-weight:900;font-size:6mm;line-height:1.15">%s</div></div></div>'
           % (MUTE, esc(it['code']), esc(it['en']), MUTE, esc(ta), esc(it['ar']))), 'background:#F1F5F9;border-radius:5mm')
    for key, en, ar, x, y, w, h in FIELDS:
        o += a(x, y, w, h, '<div style="position:absolute;left:3mm;right:3mm;top:1.2mm;display:flex;justify-content:space-between;font-weight:800;font-size:3mm;color:%s"><span dir="ltr">%s</span><span dir="rtl">%s</span></div>'
               '<div style="position:absolute;left:0;right:0;top:%smm;bottom:0"><input class="fi" name="%s_%s_P%d"></div>' % (SLATE, en, ar, LABEL_H - 1.4, r['id'], key, n),
               'border:.4mm solid #CBD5E1;border-radius:3.4mm;background:#fff;' if h < 28 else 'border-bottom:.4mm solid %s;' % INK)
    return ('<section class="pg p fm pl" id="f-pn-%s-%d" style="background:#fff">%s</section>' % (r['id'], n, o)), lc

def pallet_pages():
    out = []
    for r in RACKS:
        for n in range(1, LEVELS * DEEP + 1):
            h, lc = pallet_page(r, n)
            out.append((h, 'f-pn-%s-%d' % (r['id'], n), 'Pallet P%d · %s · %s' % (n, lc, r['item']['en'][:36]), 'ورقة بالت P%d · %s' % (n, lc), dict(rack=r['id'], n=n, loc=lc, item=r['item']['code'])))
    return out

# ---------------------------------------------------------------- master assembly
mm.SPEC.update({
    'finfo': dict(orient=('Landscape', 'أفقي'), mm='297 × 210', note=('Forming plan / reference page', 'صفحة خطة / مرجع للتشكيل'), fmt='l'),
    'fstk': dict(orient=('Portrait', 'عمودي'), mm='210 × 297', note=('10 labels · 78 × 50 mm each (2 × 5) · cut on the pink marks', '10 ملصقات · 78 × 50 مم للملصق (2 × 5) · قص على العلامات الوردية'), fmt='p'),
    'fbig': dict(orient=('Landscape', 'أفقي'), mm='297 × 210', note=('ONE big item label · 277 × 186 mm', 'ليبل صنف كبير واحد · 277 × 186 مم'), fmt='l'),
    'fpal': dict(orient=('Portrait', 'عمودي'), mm='210 × 297', note=('One pallet paper · full page · fillable on screen', 'ورقة بالت واحدة · صفحة كاملة · قابلة للتعبئة على الشاشة'), fmt='p'),
})
FG = [('F0', 'finfo', 'Forming plan — overview, method, tables', 'التشكيل — النظرة العامة والطريقة والجداول'),
      ('F1', 'fstk', 'Forming rack labels (39 racks × 5 levels × 2 copies)', 'ليبل راكات التشكيل (39 راك × 5 مستويات × نسختان)'),
      ('F2', 'fbig', 'Big item labels A4 (13 items)', 'ليبل الأصناف الكبير A4 (13 صنفاً)'),
      ('F3', 'fpal', 'Numbered pallet papers P1–P30 (1,170)', 'أوراق البالت المرقمة P1–P30 (1170 ورقة)')]

def index_page(P):
    cnt = {g: sum(1 for p in P if p[1] == g) for g, *_ in FG}
    rows = ''.join('<tr><td dir="ltr" style="font-weight:800"><a href="#w-%s">%s</a></td><td dir="rtl" style="font-weight:800">%s</td><td style="text-align:center;font-weight:900">%d</td><td dir="ltr" style="text-align:center">A4 %s · %s mm</td><td dir="rtl" style="text-align:center">A4 %s · %s مم</td><td dir="ltr" style="font-size:2.7mm">%s</td><td dir="rtl" style="font-size:2.9mm">%s</td></tr>'
                   % (next(p[0] for p in P if p[1] == g)[0:0] or next(p[2] for p in P if p[1] == g), esc(en), esc(ar), cnt[g], mm.SPEC[k]['orient'][0], mm.SPEC[k]['mm'], mm.SPEC[k]['orient'][1], mm.SPEC[k]['mm'], esc(mm.SPEC[k]['note'][0]), esc(mm.SPEC[k]['note'][1]))
                   for g, k, en, ar in FG)
    th = '<tr style="background:%s;color:#fff"><th dir="ltr">SECTION</th><th dir="rtl">القسم</th><th>PAGES</th><th colspan="2">PAPER · الورق</th><th dir="ltr">NOTES</th><th dir="rtl">ملاحظات</th></tr>' % INK
    inner = ('<div style="position:absolute;left:12mm;right:12mm;top:9mm">%s<div style="display:flex;gap:4mm;margin-bottom:5mm">%s</div>'
             '<table class="ft" style="border-collapse:collapse;width:100%%;font-size:3.3mm">%s%s</table>'
             '<div style="display:flex;gap:8mm;margin-top:4mm;font-size:3.2mm;line-height:1.4;font-weight:700"><div dir="ltr" style="flex:1"><b>HOW TO PRINT</b><br>• Square 🖨 button on every page = print that page only; top bar = a whole section or the whole file.<br>• Print dialog: A4 · Scale 100%% (not “fit”) · Margins None · Background graphics ON · Single-sided.<br>• Orientation is set automatically per page. ↗ Share = share the page link.</div>'
             '<div dir="rtl" style="flex:1;font-size:3.5mm"><b>طريقة الطباعة</b><br>• زر 🖨 المربع على كل ورقة = طباعة هذه الورقة فقط؛ الشريط العلوي = قسم كامل أو الملف كله.<br>• نافذة الطباعة: A4 · القياس 100%% (وليس «ملاءمة») · الهوامش بدون · الخلفيات تعمل · وجه واحد.<br>• الاتجاه يتحدد تلقائياً لكل صفحة. زر ↗ = مشاركة رابط الصفحة.</div></div>'
             '<style>.ft td,.ft th{border:.2mm solid #CBD5E1;padding:1.2mm 2mm}.ft a{color:%s}</style></div>'
             % (head('AL-MUNAJEM · FORMING SECTION — MASTER PRINT FILE', 'المنجم · قسم التشكيل — الملف الشامل للطباعة', '%s · zone 2 (FORM) · 13 items · 39 racks · %d pages' % (VER, len(P) + 1), '%s · المنطقة 2 (FORM) · 13 صنفاً · 39 راك · %d صفحة' % (VER, len(P) + 1)),
                tiles(), th, rows, INK))
    return sec('l', 'f-index', inner)

def collect():
    P = []   # (html, grp, id, en, ar, kind)
    P.append((overview(), 'F0', 'f-overview', 'Forming · overview & colour scale', 'التشكيل · النظرة العامة والمقياس', 'finfo'))
    P.append((method(), 'F0', 'f-method', 'Forming · distribution method', 'التشكيل · طريقة التوزيع', 'finfo'))
    P.append((table('R'), 'F0', 'f-table-R', 'Forming · table right side', 'التشكيل · جدول اليمين', 'finfo'))
    P.append((table('L'), 'F0', 'f-table-L', 'Forming · table left side', 'التشكيل · جدول اليسار', 'finfo'))
    for h, pid, en, ar in label_pages():
        P.append((h, 'F1', pid, en, ar, 'fstk'))
    for h, pid, en, ar in big_pages():
        P.append((h, 'F2', pid, en, ar, 'fbig'))
    meta = []
    for h, pid, en, ar, mt in pallet_pages():
        P.append((h, 'F3', pid, en, ar, 'fpal')); meta.append(mt)
    return P, meta

def build(out):
    os.makedirs(out, exist_ok=True)
    P, meta = collect()
    total = len(P) + 1
    parts = [mm.wrap(index_page(P), 'f-index', 'FIDX', 1, total, 'Index & print specifications', 'الفهرس ومواصفات الطباعة', 'finfo')]
    first = {}
    for i, (h, g, pid, en, ar, k) in enumerate(P, 2):
        first.setdefault(g, pid)
        parts.append(mm.wrap(h, pid, g, i, total, en, ar, k))
    opts = '<option value="ALL">🖨 ALL · الملف كله (%d)</option>' % total + ''.join('<option value="%s">%s · %s</option>' % (g, esc(en), esc(ar)) for g, k, en, ar in FG)
    links = ''.join('<a href="#w-%s">%s</a>' % (first[g], t) for g, t in (('F0', 'Plan · الخطة'), ('F1', 'Rack labels · ليبل الراك'), ('F2', 'Big labels · الكبير'), ('F3', 'Pallet papers · أوراق البالت')))
    nav = ('<div class="nav" style="background:%s"><b>AL-MUNAJEM · FORMING (FORM) · MASTER %s</b><a href="#w-f-index">Index · الفهرس</a>%s<select id="gsel">%s</select>'
           '<button class="topbtn" onclick="PG(document.getElementById(\'gsel\').value)">🖨 Print · طباعة</button></div>' % (INK, VER, links, opts))
    css = z.css() + mm.CSS_X + CSS_F
    doc = ('<!-- VERSION: %s | %s -->\n<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>Al-Munajem Forming Section — Master %s</title><style>%s</style></head><body>%s%s<div class="toast" id="toast"></div>%s%s</body></html>'
           % (VER, DATE, VER, css, nav, ''.join(parts), mm.JS, m.FIT_JS))
    name = 'almunajem_FORMING_MASTER_print_%s_%s' % (VER, DATE)
    open(os.path.join(out, name + '.html'), 'w', encoding='utf-8').write(doc)
    json.dump([dict(id=p[2], grp=p[1], en=p[3], ar=p[4]) for p in P], open(os.path.join(out, 'forming_pages.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(dict(meta=meta, fields=[[k, x, y, w, h] for k, _, _, x, y, w, h in FIELDS], laby=LABEL_H), open(os.path.join(out, 'forming_pallet_meta.json'), 'w', encoding='utf-8'))
    print(name, total, 'pages')

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '.')
