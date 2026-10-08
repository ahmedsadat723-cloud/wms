#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Al-Munajem rack LOAD PLATES (لوحات الحمولة) — one plate per rack level, real item data.
Real rack data (from the rack drawing): 1100 kg per pallet position, 2 pallet positions per bay level,
beam pitch 1800 mm, clear opening height 1550 mm, depth 1000 mm.
usage: python3 make_load_plates.py <out_dir>   then render_pdf.py in.html out.pdf
"""
import os, sys, html
import make_stickers as m
from make_stickers import TYPES, BRANDS, LETTERS, YEL, INK, FIT_JS, build_racks, barcode_svg

DATE, VERSION = '2026-10-08', 'v1'
KG, POS, CLEAR, PITCH, DEPTH = 1100, 2, 1550, 1800, 1000
PW, PH = 130, 84               # plate size, mm
PGW, PGH = 297, 210            # A4 landscape
GAP = 10
LEFT = (PGW - (2 * PW + GAP)) / 2
TOP = (PGH - (2 * PH + GAP)) / 2
esc = html.escape


def elevation(color, lvl):
    """mini rack bay: two yellow pallets on a beam, with height + load dimensions"""
    pal = ''
    for i in range(POS):
        x = 8 + i * 25
        pal += ('<rect x="%d" y="7" width="22" height="19" fill="%s" stroke="#111" stroke-width=".5" rx="1"/>'
                '<text x="%d" y="19.5" font-size="6" font-weight="900" text-anchor="middle" fill="#111">%d</text>'
                '<rect x="%d" y="26" width="22" height="3" fill="#C0271C"/>' % (x, YEL, x + 11, KG, x))
    return ('<svg viewBox="0 0 74 46" width="100%%" height="100%%">'
            '<rect x="3" y="2" width="2.6" height="40" fill="#2B4FA3"/><rect x="62.6" y="2" width="2.6" height="40" fill="#2B4FA3"/>'
            '%s<rect x="3" y="29" width="62" height="3.4" fill="#F28C1E"/>'
            '<line x1="70" y1="5" x2="70" y2="29" stroke="#fff" stroke-width=".6"/>'
            '<path d="M68.5 7 L70 4.5 L71.5 7 M68.5 27 L70 29.5 L71.5 27" fill="none" stroke="#fff" stroke-width=".6"/>'
            '<text x="68" y="18" font-size="4.6" font-weight="900" fill="#fff" text-anchor="middle" '
            'transform="rotate(-90 68 18)">%d mm</text>'
            '<text x="34" y="39" font-size="4.4" font-weight="900" fill="%s" text-anchor="middle">%d × %d kg = %d kg</text>'
            '<text x="34" y="44.6" font-size="3.4" font-weight="700" fill="#cfcfcf" text-anchor="middle">LEVEL %s · '
            'BEAM PITCH %d mm</text></svg>'
            % (pal, CLEAR, YEL, POS, KG, POS * KG, LETTERS[lvl - 1], PITCH))


def plate(z, r, lvl, item):
    t = TYPES[z]
    bn, bc, bar = BRANDS[r['brand']]
    letter = LETTERS[lvl - 1]
    code = '%s-%s-%d%s' % (t['code'], r['brand'], r['no'], letter)
    floor = lvl == 1
    top = lvl == r['tiers']
    pos = ('FLOOR · الأرض' if floor else ('TOP · الأعلى' if top else 'LEVEL · مستوى %d' % lvl))
    name_ar = (item['ar'] + ' ' + item['size']) if item else 'مكان احتياطي'
    name_en = item['en'] if item else 'SPARE LOCATION'
    stripe = ('repeating-linear-gradient(135deg,%s 0 2.2mm,%s 2.2mm 4.4mm)' % (YEL, INK))
    return (
        '<div class="pl" style="width:%dmm;height:%dmm;background:#14181F;color:#fff;border-radius:4mm;overflow:hidden;'
        'position:relative;font-family:Cairo,sans-serif;display:flex;flex-direction:column;direction:ltr">'
        # header
        '<div style="height:11mm;display:flex;align-items:stretch;background:%s;color:#fff">'
        '<div style="width:24mm;background:%s;display:flex;align-items:center;justify-content:center;'
        'font-weight:900;font-size:6.2mm;line-height:1">%s</div>'
        '<div style="flex:1;display:flex;align-items:center;justify-content:space-between;padding:0 3mm">'
        '<span style="font-weight:900;font-size:4.6mm;letter-spacing:.3mm">%s · %s</span>'
        '<span dir="rtl" style="font-weight:900;font-size:4.6mm">%s</span></div></div>'
        # body
        '<div style="flex:1;display:flex;padding:2mm 3mm 0 3mm;gap:3mm;min-height:0">'
        # letter block
        '<div style="width:24mm;display:flex;flex-direction:column;align-items:center;justify-content:center">'
        '<div style="width:22mm;height:22mm;background:%s;color:#111;border-radius:3mm;display:flex;align-items:center;'
        'justify-content:center;font-weight:900;font-size:19mm;line-height:1;padding-bottom:1.5mm">%s</div>'
        '<div style="font-weight:900;font-size:2.7mm;margin-top:1.2mm;color:%s;white-space:nowrap">%s</div>'
        '<div style="font-weight:900;font-size:3.4mm;margin-top:.3mm;white-space:nowrap">RACK <span style="color:%s">%d</span></div>'
        '</div>'
        # load hero + elevation
        '<div style="flex:1;display:flex;flex-direction:column;min-width:0">'
        '<div style="display:flex;align-items:baseline;gap:2mm;line-height:.95">'
        '<span style="font-weight:900;font-size:17mm;color:%s">%d</span>'
        '<span style="font-weight:900;font-size:6mm">kg<br><span dir="rtl" style="font-size:4mm;color:#cfcfcf">كجم / بالت</span></span></div>'
        '<div style="font-weight:900;font-size:2.7mm;color:#cfcfcf;margin:.3mm 0 0 0">MAX LOAD PER PALLET · الحمولة القصوى للبالت</div>'
        '<div style="flex:1;min-height:0;margin-top:1mm">%s</div></div></div>'
        # item strip
        '<div style="margin:1.4mm 3mm 0 3mm;background:#fff;color:#111;border-radius:2mm;padding:.8mm 2.5mm;'
        'border-left:2.2mm solid %s;display:flex;flex-direction:column;align-items:center;line-height:1.1;overflow:hidden">'
        '<div dir="rtl" style="max-width:100%%;white-space:nowrap"><span data-fit style="font-weight:900;font-size:4.6mm;'
        'white-space:nowrap;display:inline-block">%s</span></div>'
        '<div dir="ltr" style="max-width:100%%;white-space:nowrap"><span data-fit style="font-weight:700;font-size:2.7mm;'
        'color:#444;white-space:nowrap;display:inline-block">%s</span></div></div>'
        # footer
        '<div style="display:flex;align-items:center;gap:2mm;padding:1mm 3mm 1.2mm 3mm">'
        '<div style="background:#fff;padding:.6mm .8mm 0 .8mm;border-radius:1mm;line-height:0">%s</div>'
        '<div style="flex:1;text-align:center;line-height:1.1"><div dir="ltr" style="font-weight:900;font-size:3.6mm;'
        'letter-spacing:.2mm;color:%s">%s</div></div>'
        '<div style="width:15mm;height:6.4mm;border-radius:1mm;background:%s"></div></div>'
        '</div>'
        % (PW, PH, t['hdr'], bc, bn, t['code'], t['en'], t['ar'],
           YEL, letter, YEL, pos, YEL, r['no'],
           YEL, KG, elevation(YEL, lvl),
           bc, esc(name_ar), esc(name_en),
           barcode_svg(code, 5.2).replace('56mm', '42mm'), YEL, code, stripe))


def cut_marks():
    f = lambda v: '%.1f' % v
    k, rects = [], []
    for c in range(2):
        for rr in range(2):
            x0, y0 = LEFT + c * (PW + GAP), TOP + rr * (PH + GAP)
            x1, y1 = x0 + PW, y0 + PH
            for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                sx = -1 if x == x0 else 1
                sy = -1 if y == y0 else 1
                k.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(x + sx * 2), f(y), f(x + sx * 7), f(y)))
                k.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(x), f(y + sy * 2), f(x), f(y + sy * 7)))
            rects.append('<rect x="%s" y="%s" width="%d" height="%d" rx="4"/>' % (f(x0), f(y0), PW, PH))
    return ('<svg style="position:absolute;left:0;top:0;pointer-events:none" width="%dmm" height="%dmm" viewBox="0 0 %d %d">'
            '<g stroke="#000" stroke-width=".25" fill="none">%s</g>'
            '<g stroke="#E6007E" stroke-width=".3" fill="none" stroke-dasharray="2.2 1.2">%s</g></svg>'
            % (PGW, PGH, PGW, PGH, ''.join(k), ''.join(rects)))


def cover(plates_n, racks):
    rows = ''
    for z in ('c', 'p', 'b'):
        t = TYPES[z]
        n = len(racks[z])
        rows += ('<div style="display:flex;align-items:center;gap:5mm;background:#1d232d;border-radius:3mm;padding:3mm 5mm;'
                 'border-left:4mm solid %s;margin-bottom:3mm"><div style="font-weight:900;font-size:9mm;width:22mm;color:%s">%s</div>'
                 '<div style="flex:1"><div style="font-weight:900;font-size:5.4mm">%s · %s</div>'
                 '<div dir="rtl" style="font-size:4.4mm;color:#cfcfcf">%s</div></div>'
                 '<div style="text-align:center"><div style="font-weight:900;font-size:9mm;color:%s">%d</div>'
                 '<div style="font-size:3mm;color:#cfcfcf">RACKS · راك</div></div>'
                 '<div style="text-align:center"><div style="font-weight:900;font-size:9mm;color:%s">%d</div>'
                 '<div style="font-size:3mm;color:#cfcfcf">LEVELS · مستوى</div></div></div>'
                 % (t['hdr'], YEL, t['code'], t['tag'], t['en'], t['name_ar'], YEL, n, YEL, sum(r['tiers'] for r in racks[z])))
    specs = [(str(KG), 'kg', 'MAX PER PALLET · لكل بالت'), (str(POS * KG), 'kg', 'PER BAY LEVEL · لكل مستوى (%d بالت)' % POS),
             (str(CLEAR), 'mm', 'CLEAR HEIGHT · الارتفاع الصافي'), (str(PITCH), 'mm', 'BEAM PITCH · المسافة بين الأرجل')]
    sp = ''.join('<div style="flex:1;background:#fff;color:#111;border-radius:3mm;padding:3mm;text-align:center">'
                 '<div style="font-weight:900;font-size:13mm;line-height:1">%s<span style="font-size:5mm"> %s</span></div>'
                 '<div style="font-weight:700;font-size:3mm">%s</div></div>' % s for s in specs)
    return ('<div class="pg" style="width:%dmm;height:%dmm;background:#0E1218;color:#fff;font-family:Cairo,sans-serif;direction:ltr;'
            'padding:16mm 18mm;box-sizing:border-box"><div style="display:flex;justify-content:space-between;align-items:flex-end">'
            '<div><div style="font-weight:900;font-size:15mm;line-height:1;color:%s">RACK LOAD PLATES</div>'
            '<div dir="rtl" style="font-weight:900;font-size:10mm;line-height:1.2">لوحات الحمولة للراكات</div></div>'
            '<div style="text-align:right;font-weight:700;font-size:4mm;color:#cfcfcf">AL-MUNAJEM FOODS · JEDDAH<br>%s · %s</div></div>'
            '<div style="height:1.6mm;background:%s;margin:6mm 0"></div>'
            '<div style="display:flex;gap:4mm;margin-bottom:6mm">%s</div>%s'
            '<div dir="rtl" style="font-size:4.2mm;color:#cfcfcf;margin-top:5mm;line-height:1.6">'
            'لوحة واحدة لكل مستوى · %d لوحة · حجم اللوحة %d × %d مم · علامات القص السوداء خارج إطار كل لوحة، والخط الوردي المتقطع هو خط القص.<br>'
            'البيانات من رسم الراك: 1100 كجم لكل بالت، بالتان في كل مستوى، ارتفاع صافٍ 1550 مم. الأصناف والمستويات من توزيع v2.</div></div>'
            % (PGW, PGH, YEL, VERSION, DATE, YEL, sp, rows, plates_n, PW, PH))


def build(out_dir):
    racks = build_racks()
    cells = []
    for z in ('c', 'p', 'b'):
        for r in racks[z]:
            for h in r['halves']:
                for lvl in h['levels']:
                    cells.append(plate(z, r, lvl, h['item']))
    pages = [cover(len(cells), racks)]
    for i in range(0, len(cells), 4):
        grp = cells[i:i + 4]
        body = ''.join('<div style="position:absolute;left:%.1fmm;top:%.1fmm">%s</div>'
                       % (LEFT + (j % 2) * (PW + GAP), TOP + (j // 2) * (PH + GAP), c) for j, c in enumerate(grp))
        pages.append('<div class="pg" style="width:%dmm;height:%dmm">%s%s</div>' % (PGW, PGH, body, cut_marks()))
    doc = ('<!doctype html><html lang="ar"><head><meta charset="utf-8"><title>Al-Munajem Rack Load Plates %s</title>'
           '<style>%s</style></head><body>%s%s</body></html>'
           % (VERSION, m.page_css(PGW, PGH), ''.join(pages), FIT_JS))
    p = os.path.join(out_dir, 'almunajem_rack_load_plates_%s_%s.html' % (VERSION, DATE))
    open(p, 'w', encoding='utf-8').write(doc)
    return p, len(cells), len(pages)


if __name__ == '__main__':
    print(build(sys.argv[1] if len(sys.argv) > 1 else '.'))
