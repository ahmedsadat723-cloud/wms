#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Al-Munajem · SPICES section (SPIC, zone 4 left, 246 cm racks) — complete print file, bilingual AR/EN, yellow rack stickers kept,
spice-themed motifs (hexagon level tile, sawtooth band, per-spice icons, spice-dust pattern).
5 racks · 4 levels (A-D) · 6 pallets deep = 24 pallets per rack · 120 locations · 13 items allocated by LEVEL (a level holds one item).
usage: python3 make_spices.py <out_dir>"""
import os, sys, json, html, re
import make_stickers as m
import make_zone1_system as z
import make_master as mm
import make_forming as f
from make_forming import esc, INK, SLATE, MUTE, YEL, YEL2, fbar, head, sec, tag, tiles as _t, CSS_F

VER, DATE = 'v1', '2026-10-11'
HERE = os.path.dirname(os.path.abspath(__file__))
LETTERS, DEEP, LEVELS = 'ABCD', 6, 4
ACC = '#7B3F00'    # SPIC zone colour from the dry-room plan

BRANDS = dict(f.BRANDS)
BRANDS['LAY'] = ('LAY', 'لاي', '#0B7285')
BRANDS['CFF'] = ('CFF', 'سي إف إف', '#5C940D')

# item -> (brand, icon)
META = {'SPIC-0001': ('ESNAD', 'PEPPER'), 'SPIC-0002': ('ESNAD', 'GARLIC'), 'SPIC-0003': ('ESNAD', 'GINGER'), 'SPIC-0004': ('ESNAD', 'ONION'),
        'SPIC-0005': ('ESNAD', 'PEPPER'), 'SPIC-0006': ('ESNAD', 'ONION'), 'SPIC-0007': ('ESNAD', 'PAPRIKA'), 'SPIC-0008': ('ESNAD', 'CHILLI'),
        'SPIC-0009': ('KERRY', 'SHAKER'), 'SPIC-0010': ('LAY', 'SHAKER'), 'SPIC-0011': ('CFF', 'POTATO'), 'SPIC-0012': ('CFF', 'POTATO'),
        'SPIC-0014': ('KERRY', 'RUSK')}
# rack -> 4 levels (A..D) of item codes: an item that takes 2 levels is listed twice in a row; brand-pure racks where possible
PLAN = [['SPIC-0001', 'SPIC-0001', 'SPIC-0002', 'SPIC-0002'],
        ['SPIC-0003', 'SPIC-0005', 'SPIC-0004', 'SPIC-0004'],
        ['SPIC-0006', 'SPIC-0006', 'SPIC-0007', 'SPIC-0008'],
        ['SPIC-0009', 'SPIC-0009', 'SPIC-0014', 'SPIC-0014'],
        ['SPIC-0010', 'SPIC-0010', 'SPIC-0011', 'SPIC-0012']]

def cl(s):
    s = re.sub(r'\s+', ' ', s).strip().strip('|').strip()
    if s.startswith('(') and s.endswith(')'):
        s = s[1:-1].strip()
    return s.replace('®', '')

def load():
    raw = json.load(open(os.path.join(HERE, 'assets', 'spice_items.json'), encoding='utf-8'))
    items = {}
    for n, code in enumerate(sorted(META), 1):
        r = raw[code]
        items[code] = dict(code=code, no=n, en=cl(r['nameEn']), ar=cl(r['cat']), brand=META[code][0], icon=META[code][1], levels=[])
    racks = []
    for ri, lv in enumerate(PLAN, 1):
        rk = dict(no=ri, id='S%d' % ri, levels=lv, gno=ri)
        racks.append(rk)
        for li, code in enumerate(lv):
            items[code]['levels'].append((rk, li + 1))
    return items, racks

ITEMS, RACKS = load()
loc = lambda rk, L, pos: '4L-%02d%s%d' % (rk['no'], L, pos)

def pnum(code, rk, lv):
    """pallet range of one level inside its item (an item with 2 levels: P1-P6, P7-P12)"""
    idx = [(r['no'], l) for r, l in ITEMS[code]['levels']].index((rk['no'], lv))
    return idx * DEEP + 1

# ---------------------------------------------------------------- icons (24x24, white on the brand shape)
IC = {
 'PEPPER': '<circle cx="12" cy="12" r="8.5" fill="#fff"/><g fill="%(c)s"><circle cx="9" cy="9" r="1.2"/><circle cx="14" cy="8.5" r="1"/><circle cx="15.5" cy="13" r="1.2"/><circle cx="10" cy="14.5" r="1.1"/><circle cx="12.5" cy="11.5" r=".9"/></g>',
 'GARLIC': '<path d="M12 2c1 3 7 5 7 12a7 7 0 01-14 0c0-7 6-9 7-12z" fill="#fff"/><path d="M12 6v14M8.5 9c-1 3-1 7 1 10M15.5 9c1 3 1 7-1 10" stroke="%(c)s" stroke-width="1.2" fill="none"/>',
 'GINGER': '<path d="M3 15c0-3 3-4 5-4l1-5 3 1-1 4c3 0 8 2 8 5s-4 4-7 4H8c-3 0-5-2-5-5z" fill="#fff"/><path d="M9 14l3 .5M13 17l3 .3" stroke="%(c)s" stroke-width="1.3" stroke-linecap="round"/>',
 'ONION': '<path d="M12 2c0 3-8 5-8 12a8 8 0 0016 0c0-7-8-9-8-12z" fill="#fff"/><path d="M12 5v15M8 8c-2 4-2 8 1 11M16 8c2 4 2 8-1 11" stroke="%(c)s" stroke-width="1.2" fill="none"/>',
 'PAPRIKA': '<path d="M8 8c0-3 3-4 4-4s4 1 4 4c3 2 3 9-1 12-2 1-6 1-8 0-4-3-4-10 1-12z" fill="#fff"/><path d="M12 4c0-1.5 1-2.2 2.5-2.2" stroke="%(c)s" stroke-width="1.6" fill="none" stroke-linecap="round"/><path d="M9 11c-.5 3 0 6 2 8" stroke="%(c)s" stroke-width="1.2" fill="none"/>',
 'CHILLI': '<path d="M5 6c4-3 11 0 13 7 1 3 0 6-2 8 0-5-3-9-8-9-1-1-2-3-3-6z" fill="#fff"/><path d="M5 6c-1-2-3-2-3-2" stroke="#fff" stroke-width="2" stroke-linecap="round" fill="none"/>',
 'SHAKER': '<path d="M8 2h8l1 5H7z" fill="#fff"/><path d="M7 8h10v14H7z" fill="#fff"/><g fill="%(c)s"><circle cx="10" cy="4.2" r=".7"/><circle cx="14" cy="4.2" r=".7"/><circle cx="12" cy="5.4" r=".7"/></g><path d="M9 13h6M9 17h6" stroke="%(c)s" stroke-width="1.4"/>',
 'POTATO': '<ellipse cx="12" cy="13" rx="9" ry="6.5" fill="#fff" transform="rotate(-18 12 13)"/><g fill="%(c)s"><circle cx="8" cy="12" r=".9"/><circle cx="13" cy="10.5" r=".9"/><circle cx="15" cy="15" r=".9"/><circle cx="10" cy="16" r=".8"/></g>',
 'RUSK': '<path d="M4 10a5 5 0 015-5h6a5 5 0 015 5v10H4z" fill="#fff"/><path d="M8 11h8M8 15h8" stroke="%(c)s" stroke-width="1.4" stroke-linecap="round"/>',
}
HEX = 'polygon(25% 3%,75% 3%,100% 50%,75% 97%,25% 97%,0 50%)'

def icon(ic, bc, size, ring=True):
    return ('<span style="width:%smm;height:%smm;display:inline-flex;align-items:center;justify-content:center;flex:none;background:%s;clip-path:%s;filter:drop-shadow(.4mm .4mm 0 %s)">'
            '<svg viewBox="0 0 24 24" width="%smm" height="%smm">%s</svg></span>'
            % (size, size, bc, HEX, INK, size * .56, size * .56, IC[ic] % dict(c=bc)))

# ---------------------------------------------------------------- level sticker (78 x 50 mm): yellow body, spice motifs
DUST = 'background-image:radial-gradient(#0000002e .38mm,transparent .42mm);background-size:2.6mm 2.6mm'

def arr(down, col=YEL):
    st = ' style="transform:rotate(180deg)"' if down else ''
    return ('<svg%s viewBox="0 0 100 110" width="5.4mm" height="5.9mm"><polygon points="50,2 98,52 68,52 68,108 32,108 32,52 2,52" fill="%s"/></svg>' % (st, col))

def sside(down, letter, w_en, w_ar):
    return ('<div style="width:14.5mm;display:flex;flex-direction:column;align-items:center;gap:.5mm"><div style="width:9mm;height:9mm;border-radius:2.2mm;background:%s;display:flex;align-items:center;justify-content:center;transform:rotate(45deg)"><div style="transform:rotate(-45deg);display:flex">%s</div></div>'
            '<span dir="ltr" style="font-weight:900;font-size:3.1mm;line-height:1;margin-top:.6mm">%s</span><span style="display:flex;gap:.9mm;white-space:nowrap;font-weight:800;font-size:2.2mm;line-height:1"><span dir="ltr">%s</span><span dir="rtl">%s</span></span></div>'
            % (INK, arr(down), letter, w_en, w_ar))

def ssticker(rk, lv, spare=False):
    code = rk['levels'][lv - 1]
    it = ITEMS[code]
    bc = BRANDS[it['brand']][2]
    L = LETTERS[lv - 1]
    dn = ('FLOOR', 'DOWN', 'أسفل') if lv == 1 else (LETTERS[lv - 2], 'DOWN', 'أسفل')
    up = ('TOP', 'UP', 'أعلى') if lv == LEVELS else (LETTERS[lv], 'UP', 'أعلى')
    bcode = '4L-%02d%s' % (rk['no'], L)
    saw = ('background:linear-gradient(135deg,%s 25%%,transparent 25%%) 0 0/3.2mm 2.2mm,linear-gradient(225deg,%s 25%%,transparent 25%%) 0 0/3.2mm 2.2mm' % (bc, bc))
    top = ('<div style="height:7.4mm;background:%s;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 3mm;font-weight:900;white-space:nowrap">'
           '<span style="display:flex;gap:1.4mm;align-items:center;font-size:3mm"><span dir="ltr">SPICES</span><span>·</span><span dir="rtl">البهارات</span></span>'
           '<span dir="ltr" style="font-size:3.3mm;letter-spacing:.2mm">4L-%02d · RACK S%d</span></div><div style="height:2.2mm;%s;flex:none"></div>' % (bc, rk['no'], rk['no'], saw))
    name = ('<div style="height:9.2mm;margin-top:-2.2mm;padding:0 2.2mm;display:flex;align-items:center;gap:2mm;background:%s;border-bottom:.5mm solid %s;overflow:hidden;position:relative;padding-top:2.2mm;box-sizing:content-box">%s'
            '<div style="flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center">'
            '<div data-fit dir="rtl" style="white-space:nowrap;font-weight:900;font-size:3.3mm;line-height:1.15">%s</div>'
            '<div data-fit dir="ltr" style="white-space:nowrap;font-weight:700;font-size:2.4mm;line-height:1.15">%s</div></div></div>'
            % (YEL2, INK, icon(it['icon'], bc, 7.4), esc(it['ar']), esc(it['en'])))
    mid = ('<div style="flex:1;display:flex;align-items:center;justify-content:space-between;padding:0 2mm;position:relative;%s">%s'
           '<div style="display:flex;align-items:center;gap:1.6mm"><div dir="ltr" style="background:%s;color:#fff;font-weight:900;font-size:4.8mm;line-height:1;padding:.9mm 1.8mm;border-radius:.8mm;transform:skewX(-8deg)">S%d</div>'
           '<div style="position:relative;width:19mm;height:17.6mm;filter:drop-shadow(.9mm .9mm 0 %s)"><div style="position:absolute;inset:0;background:%s;clip-path:%s"></div>'
           '<div style="position:absolute;inset:.9mm;background:%s;clip-path:%s"></div><div dir="ltr" style="position:absolute;inset:0;color:#fff;font-weight:900;font-size:13mm;line-height:17.2mm;text-align:center">%s</div></div></div>%s</div>'
           % (DUST, sside(True, dn[0], dn[1], dn[2]), INK, rk['no'], INK, INK, HEX, bc, HEX, L, sside(False, up[0], up[1], up[2])))
    p0 = pnum(code, rk, lv)
    pill = lambda t, bg, fg, bd='': '<span dir="ltr" class="chip" style="background:%s;color:%s;%sfont-size:2.9mm;padding:0 1.8mm;border-radius:1mm">%s</span>' % (bg, fg, bd, t)
    note = ('<span dir="ltr" style="font-weight:800;font-size:2.4mm;opacity:.6;margin:0 1mm">SPARE · احتياطي</span>') if spare else ''
    bot = ('<div style="height:8.6mm;display:flex;align-items:center;justify-content:space-between;padding:0 2.2mm 1mm;gap:2mm"><div style="display:flex;gap:1.2mm;align-items:center">%s%s%s</div>'
           '<div style="display:flex;flex-direction:column;align-items:center;gap:.2mm;background:#fff;border-radius:1.4mm;padding:.5mm 1.4mm .3mm;border:.3mm solid %s">%s<span dir="ltr" style="font-weight:800;font-size:2.2mm;letter-spacing:.5mm;line-height:1">%s</span></div></div>'
           % (pill('P%d–P%d' % (p0, p0 + DEEP - 1), INK, YEL), pill('%s1–%s%d' % (L, L, DEEP), '#fff', INK, 'border:.3mm solid %s;' % INK), note, INK, fbar(bcode, 3.8, 24), bcode))
    return ('<div class="stk" style="width:78mm;height:50mm;box-sizing:border-box;background:%s;border:1.1mm solid %s;border-radius:4mm;overflow:hidden;direction:ltr;display:flex;flex-direction:column;font-family:\'Cairo\',sans-serif;color:%s;position:relative">%s%s%s%s</div>'
            % (YEL, INK, INK, top, name, mid, bot))

def label_pages():
    out = []
    for rk in RACKS:
        cells = [ssticker(rk, lv) for lv in range(LEVELS, 0, -1) for _ in range(2)] + [ssticker(rk, 1, True)] * 2
        hd = ('<div style="position:absolute;left:24.5mm;top:3.2mm;width:161mm;height:10mm;display:flex;justify-content:space-between;align-items:flex-start;font-weight:900;font-size:3.4mm;line-height:1.15;color:%s;white-space:nowrap">'
              '<span dir="ltr">SPICES · RACK S%d · LEVELS A–D<br><span style="font-weight:700;font-size:3mm">RACK-LEVEL LABELS · 2 PER LEVEL · 2 SPARE</span></span>'
              '<span dir="rtl" style="text-align:right">البهارات · راك S%d · المستويات A–D<br><span style="font-weight:700;font-size:3mm">ملصقات مستويات الراك · 2 لكل مستوى · 2 احتياطي</span></span></div>' % (INK, rk['no'], rk['no']))
        out.append(('<section class="pg p fm" id="s-lbl-S%d" style="background:#fff">%s<div style="position:absolute;left:24.5mm;top:18mm;width:161mm;height:%dmm;display:grid;direction:ltr;grid-template-columns:repeat(2,78mm);grid-auto-rows:50mm;gap:5mm">%s</div>%s</section>'
                    % (rk['no'], hd, 5 * 50 + 4 * 5, ''.join(cells), m.overlay(210, 297, 24.5, 18, 2, 5)), 's-lbl-S%d' % rk['no'], 'Spices rack labels · rack S%d' % rk['no'], 'ليبل راك البهارات · راك S%d' % rk['no']))
    return out

# ---------------------------------------------------------------- big item labels (A4 landscape, yellow)
def big_pages():
    out = []
    for it in ITEMS.values():
        be, ba, bc = BRANDS[it['brand']]
        rl = ['S%d-%s' % (r['no'], LETTERS[l - 1]) for r, l in it['levels']]
        rng = rl[0] if len(rl) == 1 else '%s → %s' % (rl[0], rl[-1])
        saw = 'background:linear-gradient(135deg,%s 25%%,transparent 25%%) 0 0/9mm 6mm,linear-gradient(225deg,%s 25%%,transparent 25%%) 0 0/9mm 6mm' % (bc, bc)
        inner = ('<div style="position:absolute;left:10mm;top:12mm;width:277mm;height:186mm;background:%s;border:4mm solid %s;border-radius:14mm;overflow:hidden;display:flex;flex-direction:column;direction:ltr;box-sizing:border-box">'
                 '<div style="height:34mm;background:%s;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 14mm;font-weight:900;white-space:nowrap">'
                 '<span style="font-size:12mm;display:flex;gap:4mm;align-items:baseline"><span dir="ltr">SPICES</span><span>·</span><span dir="rtl">البهارات</span></span>'
                 '<span style="font-size:12mm;display:flex;gap:4mm;align-items:baseline"><span dir="ltr">%s</span><span>|</span><span dir="rtl">%s</span></span></div><div style="height:6mm;%s;flex:none"></div>'
                 '<div style="flex:1;margin-top:-6mm;padding-top:6mm;background:%s;display:flex;align-items:center;gap:12mm;padding-left:14mm;padding-right:14mm;border-bottom:1.6mm solid %s;%s">%s'
                 '<div style="flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4mm">'
                 '<div data-fit dir="rtl" style="white-space:nowrap;font-weight:900;font-size:27mm;line-height:1.1">%s</div>'
                 '<div data-fit dir="ltr" style="white-space:nowrap;font-weight:800;font-size:15mm;line-height:1.1">%s</div>'
                 '<div style="display:flex;gap:6mm;margin-top:1mm"><span class="chip" style="background:%s;color:%s;font-size:7.4mm;padding:0 7mm;border-radius:2mm" dir="ltr">%s</span>'
                 '<span class="chip" style="background:#fff;color:%s;border:.8mm solid %s;font-size:7.4mm;padding:0 7mm;border-radius:2mm" dir="ltr">%s</span></div></div></div>'
                 '<div style="height:38mm;display:flex;align-items:center;justify-content:space-between;padding:0 14mm 3mm">'
                 '<div style="display:flex;flex-direction:column;white-space:nowrap;flex:none"><span dir="ltr" style="font-weight:800;font-size:4.4mm">LEFT · 246 cm · 6 deep</span><span dir="rtl" style="font-weight:800;font-size:4.4mm">اليسار · 246 سم · 6 بالتات بالعمق</span></div>'
                 '<div style="display:flex;align-items:center;gap:4mm"><div dir="ltr" style="background:%s;color:#fff;border:1.2mm solid %s;box-shadow:2mm 2mm 0 %s;border-radius:2mm;font-weight:900;font-size:11mm;line-height:1;padding:1mm 4mm;white-space:nowrap">%s</div>'
                 '<span style="font-weight:800;font-size:5mm;line-height:1.1"><span dir="ltr">LEVELS</span><br><span dir="rtl">المستويات</span></span></div>'
                 '<div style="display:flex;flex-direction:column;align-items:center;gap:1mm;background:#fff;border-radius:3mm;padding:2mm 4mm;border:.6mm solid %s">%s<span dir="ltr" style="font-weight:800;font-size:5mm;letter-spacing:2mm">%s</span></div></div></div>'
                 % (YEL, INK, bc, esc(be), esc(ba), saw, YEL2, INK, DUST, icon(it['icon'], bc, 46), esc(it['ar']), esc(it['en']),
                    INK, YEL, it['code'], INK, INK, it['code'], bc, INK, INK, rng, INK, fbar(it['code'], 11, 70), it['code']))
        pid = 's-big-' + it['code']
        out.append((sec('l', pid, inner), pid, 'Big item label · %s' % it['en'][:40], 'ليبل صنف كبير · %s' % it['ar'][:34]))
    return out

# ---------------------------------------------------------------- pallet paper (A4 portrait)  — same field geometry as forming, spice styling
def pallet_page(rk, lv, n_in_level):
    code = rk['levels'][lv - 1]
    it = ITEMS[code]
    be, ba, bc = BRANDS[it['brand']]
    L = LETTERS[lv - 1]
    pn = pnum(code, rk, lv) + n_in_level - 1
    lc = loc(rk, L, n_in_level)
    a = lambda x, y, w, h, inner, st='': '<div style="position:absolute;left:%smm;top:%smm;width:%smm;height:%smm;%s">%s</div>' % (x, y, w, h, st, inner)
    saw = 'background:linear-gradient(135deg,%s 25%%,transparent 25%%) 0 0/6mm 4mm,linear-gradient(225deg,%s 25%%,transparent 25%%) 0 0/6mm 4mm' % (bc, bc)
    o = a(10, 10, 34, 24, '', 'background:var(--logo) left center/contain no-repeat')
    o += a(100, 10, 100, 24, '<div dir="ltr" style="font-weight:900;font-size:8mm;line-height:1">PALLET LABEL</div><div dir="rtl" style="font-weight:900;font-size:8mm;line-height:1.1">ليبل بالت</div>'
           '<div style="margin-top:1mm">%s</div>' % tag('SPICES · ZONE 4', 'البهارات · المنطقة 4', ACC, '#fff', 3), 'text-align:right;display:flex;flex-direction:column;align-items:flex-end')
    o += a(10, 38, 190, 30, '<div style="display:flex;flex-direction:column;justify-content:center;height:100%%;padding:0 8mm;color:#fff"><div style="display:flex;justify-content:space-between;align-items:baseline"><span dir="ltr" style="font-weight:900;font-size:13mm;line-height:1.1">%s</span><span dir="rtl" style="font-weight:900;font-size:13mm;line-height:1.1">%s</span></div>'
           '<div style="display:flex;justify-content:space-between;font-weight:700;font-size:3.6mm"><span dir="ltr">BRAND · SUPPLIER</span><span dir="rtl">الماركة · المورّد</span></div></div>' % (esc(be), esc(ba)),
           'background:%s;border-radius:2mm' % bc)
    o += a(10, 68, 190, 4, '', saw + ';opacity:1')
    o += a(10, 76, 100, 56, '<div dir="ltr" style="font-weight:900;font-size:60mm;line-height:56mm;color:%s;text-align:center;letter-spacing:-2mm">P%d</div>' % (YEL, pn), 'background:%s;clip-path:polygon(0 0,94%% 0,100%% 12%%,100%% 100%%,6%% 100%%,0 88%%)' % INK)
    o += a(114, 76, 86, 56, ('<div style="padding:5mm 6mm;display:flex;flex-direction:column;justify-content:space-between;height:100%%;%s"><div style="display:flex;justify-content:space-between;font-weight:800;font-size:3.2mm;color:%s"><span dir="ltr">LOCATION</span><span dir="rtl">الموقع</span></div>'
           '<div dir="ltr" style="font-weight:900;font-size:13mm;line-height:1;color:%s;text-align:center">%s</div>'
           '<div style="text-align:center;line-height:1.3"><div dir="ltr" style="font-weight:800;font-size:3.4mm">RACK S%d · LEVEL %s · POSITION %d</div><div dir="rtl" style="font-weight:800;font-size:3.6mm">راك S%d · مستوى %s · موضع %d</div></div></div>'
           % (DUST, MUTE, bc, lc, rk['no'], L, n_in_level, rk['no'], L, n_in_level)), 'background:%s;border:.8mm solid %s;border-radius:2mm' % (YEL, INK))
    o += a(10, 136, 190, 28, ('<div style="padding:3mm 7mm;display:flex;justify-content:space-between;align-items:center;height:100%%;gap:6mm"><div style="min-width:0"><div dir="ltr" style="font-weight:800;font-size:3mm;color:%s">PRODUCT · %s</div>'
           '<div dir="ltr" style="font-weight:800;font-size:5mm;line-height:1.15">%s</div></div><div style="display:flex;align-items:center;gap:4mm">%s<div style="text-align:right;min-width:0"><div dir="rtl" style="font-weight:800;font-size:3mm;color:%s">المنتج</div><div dir="rtl" style="font-weight:900;font-size:6mm;line-height:1.15">%s</div></div></div></div>'
           % (MUTE, esc(it['code']), esc(it['en']), icon(it['icon'], bc, 16), MUTE, esc(it['ar']))), 'background:#F1F5F9;border-left:2.4mm solid %s;border-radius:2mm' % bc)
    for key, en, ar, x, y, w, h in f.FIELDS:
        o += a(x, y, w, h, '<div style="position:absolute;left:3mm;right:3mm;top:1.2mm;display:flex;justify-content:space-between;font-weight:800;font-size:3mm;color:%s"><span dir="ltr">%s</span><span dir="rtl">%s</span></div>'
               '<div style="position:absolute;left:0;right:0;top:%smm;bottom:0"><input class="fi" name="S%d_%s_P%d"></div>' % (SLATE, en, ar, f.LABEL_H - 1.4, rk['no'], key, pn),
               'border:.4mm solid #CBD5E1;border-left:2mm solid %s;border-radius:1.4mm;background:#fff;' % bc if h < 28 else 'border-bottom:.4mm solid %s;' % INK)
    return '<section class="pg p fm pl" id="s-pn-%d%s%d" style="background:#fff">%s</section>' % (rk['no'], L, n_in_level, o), lc, code, pn

def pallet_pages():
    out = []
    for rk in RACKS:
        for lv in range(1, LEVELS + 1):
            for k in range(1, DEEP + 1):
                h, lc, code, pn = pallet_page(rk, lv, k)
                it = ITEMS[code]
                out.append((h, 's-pn-%d%s%d' % (rk['no'], LETTERS[lv - 1], k), 'Pallet P%d · %s · %s' % (pn, lc, it['en'][:34]), 'ورقة بالت P%d · %s' % (pn, lc),
                            dict(rack='S%d' % rk['no'], n=pn, loc=lc, item=code)))
    return out

# ---------------------------------------------------------------- plan pages
def tiles():
    t = [('5', 'RACKS', 'راك'), ('4', 'LEVELS A–D', 'مستويات'), ('6', 'PALLETS DEEP', 'بالت بالعمق'), ('24', 'PALLETS / RACK', 'بالت للراك'), ('120', 'LOCATIONS', 'موقع'), ('13', 'ITEMS', 'صنف')]
    return ''.join('<div class="tile" style="flex:1;padding:3mm 4mm;text-align:center"><div style="font-weight:900;font-size:11mm;line-height:1;color:%s">%s</div>'
                   '<div dir="ltr" style="font-weight:800;font-size:3mm;color:%s">%s</div><div dir="rtl" style="font-weight:800;font-size:3.4mm">%s</div></div>' % (ACC, n, SLATE, e, a) for n, e, a in t)

def rack_strip():
    cells = ''
    for rk in RACKS:
        lv = ''
        for l in range(LEVELS, 0, -1):
            it = ITEMS[rk['levels'][l - 1]]
            lv += ('<div style="height:15mm;background:%s;color:#fff;border-radius:1.6mm;margin-bottom:1mm;display:flex;align-items:center;justify-content:space-between;padding:0 3mm;font-weight:900"><span dir="ltr" style="font-size:5mm">%s</span>'
                   '<span dir="ltr" style="font-size:3.4mm;opacity:.95">#%d</span></div>' % (BRANDS[it['brand']][2], LETTERS[l - 1], it['no']))
        cells += ('<div style="width:48mm;margin:0 3mm"><div style="text-align:center;font-weight:900;font-size:6mm;background:%s;color:%s;border-radius:2mm;margin-bottom:1.4mm" dir="ltr">S%d</div>%s'
                  '<div style="text-align:center;font-weight:800;font-size:2.8mm;color:%s" dir="ltr">4L-%02d</div></div>' % (INK, YEL, rk['no'], lv, MUTE, rk['no']))
    return '<div style="display:flex;direction:ltr;justify-content:center;margin:2mm 0 4mm">%s</div>' % cells

def legend():
    rows = ''
    for it in ITEMS.values():
        lv = ','.join('S%d%s' % (r['no'], LETTERS[l - 1]) for r, l in it['levels'])
        rows += ('<div style="display:flex;align-items:center;gap:2mm;padding:.5mm 0;border-bottom:.2mm solid #E2E8F0"><span style="width:5.4mm;height:5.4mm;border-radius:1.4mm;background:%s;color:#fff;font-weight:900;font-size:2.8mm;display:flex;align-items:center;justify-content:center;flex:none" dir="ltr">%d</span>'
                 '<span dir="ltr" style="flex:1;font-size:2.7mm;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">%s</span><span dir="rtl" style="flex:1;font-size:2.9mm;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">%s</span>'
                 '<span dir="ltr" style="width:20mm;font-size:2.6mm;font-weight:800;color:%s">%s</span></div>' % (BRANDS[it['brand']][2], it['no'], esc(it['en']), esc(it['ar']), MUTE, lv))
    return rows

def overview():
    inner = ('<div style="position:absolute;left:12mm;right:12mm;top:9mm">%s<div style="display:flex;gap:4mm;margin-bottom:3mm">%s</div>%s<div style="column-count:2;column-gap:8mm">%s</div></div>'
             % (head('SPICES SECTION · SPIC · LEFT SIDE', 'قسم البهارات · SPIC · الجهة اليسار', 'Spices · seasonings · fibres — a level holds one item — colour = brand', 'بهارات · توابل · ألياف — المستوى الواحد لصنف واحد — اللون = الماركة'),
                tiles(), rack_strip(), legend()))
    return sec('l', 's-overview', inner)

def method():
    paras = [
        ('قسم البهارات (SPIC) على اليسار: 5 راكات بارتفاع 246 سم، كل راك 4 مستويات (A = الأرض ثم B C D) و6 بالتات بالعمق = 24 بالت للراك، والإجمالي 120 موقعاً.',
         'Spices (SPIC), left side: 5 racks 246 cm high, each with 4 levels (A = floor, then B C D) and 6 pallets deep = 24 pallets per rack, 120 locations in total.'),
        ('الأصناف 13 صنفاً على 20 مستوى، فنوزّع حسب المستوى: كل مستوى لصنف واحد، والصنف الأكثر حركة يأخذ مستويين متجاورين.',
         '13 items over 20 levels, so we allocate by LEVEL: one item per level, and the faster-moving items take two adjacent levels.'),
        ('اللون = الماركة / المورّد: إسناد (3 راكات) · كيري (راك) · لاي + سي إف إف (راك)، والراك بماركة واحدة قدر الإمكان.',
         'Colour = brand / supplier: Esnad (3 racks) · Kerry (1 rack) · LAY + CFF (1 rack); a rack holds one brand wherever possible.'),
        ('على كل راك ليبل أصفر لكل مستوى بنسختين: حرف المستوى والأسهم (أعلى/أسفل) واسم صنف ذلك المستوى ورمزه ونطاق بالتاته.',
         'Each rack carries a yellow label per level, two copies: level letter, UP/DOWN arrows, that level’s item name and icon, and its pallet range.'),
        ('ترقيم البالت داخل الصنف: الصنف بمستوى واحد P1–P6، وبمستويين P1–P12؛ وكل بالت له ورقة بالت مرقمة قابلة للتعبئة.',
         'Pallets are numbered inside the item: one level P1–P6, two levels P1–P12; every pallet carries a numbered, fillable pallet paper.'),
        ('رمز الموقع: 4L-02C3 = المنطقة 4 · اليسار · الراك 02 · المستوى C · الموضع 3.',
         'Location code: 4L-02C3 = zone 4 · left · rack 02 · level C · position 3.'),
    ]
    rows = ''.join('<div style="display:flex;gap:6mm;align-items:flex-start;padding:2.6mm 0;border-bottom:.25mm solid #E2E8F0"><div style="width:7mm;height:7mm;border-radius:1mm;background:%s;color:#fff;font-weight:900;display:flex;align-items:center;justify-content:center;flex:none;transform:rotate(45deg)"><span style="transform:rotate(-45deg)">%d</span></div>'
                   '<div dir="ltr" style="flex:1;font-size:3.5mm;line-height:1.35;font-weight:600;color:%s">%s</div><div dir="rtl" style="flex:1;font-size:4mm;line-height:1.4;font-weight:800">%s</div></div>'
                   % (ACC, i, SLATE, esc(e), esc(a)) for i, (a, e) in enumerate(paras, 1))
    key = ''.join('<div class="tile" style="padding:2mm 3mm;display:flex;align-items:center;gap:2mm"><span style="width:8mm;height:8mm;border-radius:1mm;background:%s"></span><div><div dir="ltr" style="font-weight:900;font-size:3.2mm;line-height:1">%s</div><div dir="rtl" style="font-weight:800;font-size:3.2mm;line-height:1.1">%s</div></div></div>'
                  % (BRANDS[k][2], BRANDS[k][0], BRANDS[k][1]) for k in ('ESNAD', 'KERRY', 'LAY', 'CFF'))
    inner = ('<div style="position:absolute;left:14mm;right:14mm;top:10mm">%s%s<div style="display:flex;gap:3mm;margin-top:5mm">%s</div></div>'
             % (head('DISTRIBUTION METHOD', 'طريقة التوزيع', 'Spices section — how the racks are used', 'قسم البهارات — كيف تُستخدم الراكات'), rows, key))
    return sec('l', 's-method', inner)

def table():
    rows = ''
    for rk in RACKS:
        for l in range(LEVELS, 0, -1):
            code = rk['levels'][l - 1]
            it = ITEMS[code]
            be, ba, bc = BRANDS[it['brand']]
            rows += ('<tr>%s<td style="text-align:center;font-weight:900" dir="ltr">%s</td><td style="background:%s;color:#fff;font-weight:900;text-align:center" dir="ltr">%s | %s</td><td style="text-align:center;font-weight:800" dir="ltr">#%d</td>'
                     '<td dir="ltr" style="font-weight:700">%s</td><td dir="rtl" style="font-weight:800">%s</td><td style="text-align:center;font-weight:800" dir="ltr">P%d–P%d</td></tr>'
                     % (('<td rowspan="4" style="font-weight:900;text-align:center" dir="ltr">S%d<br><span style="font-size:2.4mm;font-weight:700">4L-%02d</span></td>' % (rk['no'], rk['no'])) if l == LEVELS else '',
                        LETTERS[l - 1], bc, be, ba, it['no'], esc(code + ' · ' + it['en']), esc(it['ar']), pnum(code, rk, l), pnum(code, rk, l) + DEEP - 1))
    hd = '<tr style="background:%s;color:#fff"><th>RACK<br>راك</th><th>LEVEL<br>المستوى</th><th>BRAND · الماركة</th><th>ITEM #</th><th dir="ltr">ITEM (EN)</th><th dir="rtl">الصنف (عربي)</th><th>PALLETS</th></tr>' % INK
    inner = ('<div style="position:absolute;left:12mm;right:12mm;top:8mm">%s<table class="ft" style="border-collapse:collapse;width:100%%;font-size:2.9mm;line-height:1.1">%s%s</table>'
             '<style>.ft td,.ft th{border:.2mm solid #CBD5E1;padding:.4mm 1.6mm}</style></div>' % (head('LEVEL TABLE — 5 racks × 4 levels', 'جدول المستويات — 5 راكات × 4 مستويات'), hd, rows))
    return sec('l', 's-table', inner)

# ---------------------------------------------------------------- master assembly
mm.SPEC.update({
    'sinfo': dict(orient=('Landscape', 'أفقي'), mm='297 × 210', note=('Spices plan / reference page', 'صفحة خطة / مرجع للبهارات'), fmt='l'),
    'sstk': dict(orient=('Portrait', 'عمودي'), mm='210 × 297', note=('10 labels · 78 × 50 mm each (2 × 5) · cut on the pink marks', '10 ملصقات · 78 × 50 مم للملصق (2 × 5) · قص على العلامات الوردية'), fmt='p'),
    'sbig': dict(orient=('Landscape', 'أفقي'), mm='297 × 210', note=('ONE big item label · 277 × 186 mm', 'ليبل صنف كبير واحد · 277 × 186 مم'), fmt='l'),
    'spal': dict(orient=('Portrait', 'عمودي'), mm='210 × 297', note=('One pallet paper · full page · fillable on screen', 'ورقة بالت واحدة · صفحة كاملة · قابلة للتعبئة على الشاشة'), fmt='p'),
})
SG = [('S0', 'sinfo', 'Spices plan — overview, method, level table', 'البهارات — النظرة العامة والطريقة وجدول المستويات'),
      ('S1', 'sstk', 'Spices rack labels (5 racks × 4 levels × 2 copies)', 'ليبل راكات البهارات (5 راكات × 4 مستويات × نسختان)'),
      ('S2', 'sbig', 'Big item labels A4 (13 items)', 'ليبل الأصناف الكبير A4 (13 صنفاً)'),
      ('S3', 'spal', 'Numbered pallet papers (120)', 'أوراق البالت المرقمة (120 ورقة)')]

def index_page(P):
    cnt = {g: sum(1 for p in P if p[1] == g) for g, *_ in SG}
    first = {}
    for p in P:
        first.setdefault(p[1], p[2])
    rows = ''.join('<tr><td dir="ltr" style="font-weight:800"><a href="#w-%s">%s</a></td><td dir="rtl" style="font-weight:800">%s</td><td style="text-align:center;font-weight:900">%d</td><td dir="ltr" style="text-align:center">A4 %s · %s mm</td><td dir="rtl" style="text-align:center">A4 %s · %s مم</td><td dir="ltr" style="font-size:2.7mm">%s</td><td dir="rtl" style="font-size:2.9mm">%s</td></tr>'
                   % (first[g], esc(en), esc(ar), cnt[g], mm.SPEC[k]['orient'][0], mm.SPEC[k]['mm'], mm.SPEC[k]['orient'][1], mm.SPEC[k]['mm'], esc(mm.SPEC[k]['note'][0]), esc(mm.SPEC[k]['note'][1])) for g, k, en, ar in SG)
    th = '<tr style="background:%s;color:#fff"><th dir="ltr">SECTION</th><th dir="rtl">القسم</th><th>PAGES</th><th colspan="2">PAPER · الورق</th><th dir="ltr">NOTES</th><th dir="rtl">ملاحظات</th></tr>' % INK
    inner = ('<div style="position:absolute;left:12mm;right:12mm;top:9mm">%s<div style="display:flex;gap:4mm;margin-bottom:5mm">%s</div>'
             '<table class="ft" style="border-collapse:collapse;width:100%%;font-size:3.3mm">%s%s</table>'
             '<div style="display:flex;gap:8mm;margin-top:4mm;font-size:3.2mm;line-height:1.4;font-weight:700"><div dir="ltr" style="flex:1"><b>HOW TO PRINT</b><br>• Square 🖨 button on every page = print that page only; top bar = a whole section or the whole file.<br>• Print dialog: A4 · Scale 100%% (not “fit”) · Margins None · Background graphics ON · Single-sided.<br>• Orientation is set automatically per page. ↗ Share = share the page link.</div>'
             '<div dir="rtl" style="flex:1;font-size:3.5mm"><b>طريقة الطباعة</b><br>• زر 🖨 المربع على كل ورقة = طباعة هذه الورقة فقط؛ الشريط العلوي = قسم كامل أو الملف كله.<br>• نافذة الطباعة: A4 · القياس 100%% (وليس «ملاءمة») · الهوامش بدون · الخلفيات تعمل · وجه واحد.<br>• الاتجاه يتحدد تلقائياً لكل صفحة. زر ↗ = مشاركة رابط الصفحة.</div></div>'
             '<style>.ft td,.ft th{border:.2mm solid #CBD5E1;padding:1.2mm 2mm}.ft a{color:%s}</style></div>'
             % (head('AL-MUNAJEM · SPICES SECTION — MASTER PRINT FILE', 'المنجم · قسم البهارات — الملف الشامل للطباعة', '%s · SPIC · 13 items · 5 racks · %d pages' % (VER, len(P) + 1), '%s · SPIC · 13 صنفاً · 5 راكات · %d صفحة' % (VER, len(P) + 1)),
                tiles(), th, rows, INK))
    return sec('l', 's-index', inner)

def collect():
    P = [(overview(), 'S0', 's-overview', 'Spices · overview & level map', 'البهارات · النظرة العامة وخريطة المستويات', 'sinfo'),
         (method(), 'S0', 's-method', 'Spices · distribution method', 'البهارات · طريقة التوزيع', 'sinfo'),
         (table(), 'S0', 's-table', 'Spices · level table', 'البهارات · جدول المستويات', 'sinfo')]
    for h, pid, en, ar in label_pages():
        P.append((h, 'S1', pid, en, ar, 'sstk'))
    for h, pid, en, ar in big_pages():
        P.append((h, 'S2', pid, en, ar, 'sbig'))
    meta = []
    for h, pid, en, ar, mt in pallet_pages():
        P.append((h, 'S3', pid, en, ar, 'spal')); meta.append(mt)
    return P, meta

def build(out):
    os.makedirs(out, exist_ok=True)
    P, meta = collect()
    total = len(P) + 1
    parts = [mm.wrap(index_page(P), 's-index', 'SIDX', 1, total, 'Index & print specifications', 'الفهرس ومواصفات الطباعة', 'sinfo')]
    first = {}
    for i, (h, g, pid, en, ar, k) in enumerate(P, 2):
        first.setdefault(g, pid)
        parts.append(mm.wrap(h, pid, g, i, total, en, ar, k))
    opts = '<option value="ALL">🖨 ALL · الملف كله (%d)</option>' % total + ''.join('<option value="%s">%s · %s</option>' % (g, esc(en), esc(ar)) for g, k, en, ar in SG)
    links = ''.join('<a href="#w-%s">%s</a>' % (first[g], t) for g, t in (('S0', 'Plan · الخطة'), ('S1', 'Rack labels · ليبل الراك'), ('S2', 'Big labels · الكبير'), ('S3', 'Pallet papers · أوراق البالت')))
    nav = ('<div class="nav" style="background:%s"><b>AL-MUNAJEM · SPICES (SPIC) · MASTER %s</b><a href="#w-s-index">Index · الفهرس</a>%s<select id="gsel">%s</select>'
           '<button class="topbtn" onclick="PG(document.getElementById(\'gsel\').value)">🖨 Print · طباعة</button></div>' % (ACC, VER, links, opts))
    css = z.css() + mm.CSS_X + CSS_F
    doc = ('<!-- VERSION: %s | %s -->\n<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>Al-Munajem Spices Section — Master %s</title><style>%s</style></head><body>%s%s<div class="toast" id="toast"></div>%s%s</body></html>'
           % (VER, DATE, VER, css, nav, ''.join(parts), mm.JS, m.FIT_JS))
    name = 'almunajem_SPICES_MASTER_print_%s_%s' % (VER, DATE)
    open(os.path.join(out, name + '.html'), 'w', encoding='utf-8').write(doc)
    json.dump([dict(id=p[2], grp=p[1], en=p[3], ar=p[4]) for p in P], open(os.path.join(out, 'spices_pages.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(dict(meta=meta, fields=[[k, x, y, w, h] for k, _, _, x, y, w, h in f.FIELDS], laby=f.LABEL_H), open(os.path.join(out, 'spices_pallet_meta.json'), 'w', encoding='utf-8'))
    print(name, total, 'pages')

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '.')
