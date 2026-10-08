#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Al-Munajem RACK SIDE SIGN (لوحة جانب الراك) — one sign per rack, stuck on both sides (print x2).
Shows: zone / goods type, load type, number of pallets, rack capacity = pallets x carton-pallet weight (1100 kg).
No pure black anywhere: ink = deep navy.
usage: python3 make_rack_signs.py <out_dir>   then render_pdf.py in.html out.pdf
"""
import os, sys, html
import make_stickers as m
from make_stickers import TYPES, BRANDS, LETTERS, build_racks, barcode_svg

DATE, VERSION = '2026-10-08', 'v1'
KG, PER_TIER = 1100, 5          # kg per pallet (carton pallet), pallets per level
SW, SH = 180, 262               # sign size mm
PGW, PGH = 210, 297
LEFT, TOP = (PGW - SW) / 2, (PGH - SH) / 2
INK, PAPER, YEL, MUTE = '#0E2A47', '#F7F5EF', '#FFC800', '#5B6B7C'
esc = html.escape
nf = lambda v: '{:,}'.format(v)


def pallet_grid(r, color):
    rows = ''
    for lvl in range(r['tiers'], 0, -1):
        cells = ''.join('<div style="flex:1;background:%s;border:.5mm solid %s;border-bottom:2.2mm solid #C0271C;border-radius:1mm;'
                        'display:flex;align-items:center;justify-content:center;font-weight:900;font-size:4.6mm;color:%s">%s</div>'
                        % (YEL, INK, INK, nf(KG)) for _ in range(PER_TIER))
        rows += ('<div style="display:flex;align-items:stretch;gap:2mm;height:%.1fmm;margin-bottom:1.6mm">'
                 '<div style="width:11mm;background:%s;color:#fff;border-radius:1.5mm;display:flex;align-items:center;'
                 'justify-content:center;font-weight:900;font-size:7mm">%s</div>'
                 '<div style="flex:1;display:flex;gap:1.6mm;padding-bottom:.6mm;border-bottom:1.4mm solid #E08A1E">%s</div>'
                 '<div style="width:26mm;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1">'
                 '<span style="font-weight:900;font-size:5.4mm;color:%s">%s</span><span style="font-size:2.8mm;font-weight:700;color:%s">kg</span></div></div>'
                 % (11.2 if r['tiers'] == 5 else 14, INK, LETTERS[lvl - 1], cells, INK, nf(PER_TIER * KG), MUTE))
    return rows


def sign(z, r):
    t = TYPES[z]
    bn, bc, bar = BRANDS[r['brand']]
    spare = r['halves'][0]['name'] == 'spare'
    pallets = r['tiers'] * PER_TIER
    total = pallets * KG
    code = '%s-%s-%d' % (t['code'], r['brand'], r['no'])
    # goods block
    goods = ''
    for h in r['halves']:
        it = h['item']
        rng = LETTERS[h['levels'][0] - 1] + ('–' + LETTERS[h['levels'][-1] - 1] if len(h['levels']) > 1 else '')
        tag = ''
        if h['name'] != 'full':
            tag = ('<span style="background:%s;color:%s;border-radius:1.5mm;padding:.2mm 2.4mm;font-weight:900;font-size:3.6mm;'
                   'white-space:nowrap;%s">%s %s</span>'
                   % (((INK, YEL, '') if h['name'] == 'lower' else (YEL, INK, 'border:.4mm solid ' + INK))
                      + (rng, 'سفلي ↓' if h['name'] == 'lower' else 'علوي ↑')))
        ar = (it['ar'] + ' ' + it['size']) if it else 'مكان احتياطي'
        en = it['en'] if it else 'SPARE LOCATION'
        goods += ('<div style="display:flex;align-items:center;gap:3mm;margin-bottom:1.6mm"><div style="flex:1;min-width:0">'
                  '<div dir="rtl" style="white-space:nowrap"><span data-fit style="display:inline-block;font-weight:900;font-size:%.1fmm;'
                  'color:%s;white-space:nowrap">%s</span></div>'
                  '<div dir="ltr" style="white-space:nowrap"><span data-fit style="display:inline-block;font-weight:700;font-size:3.4mm;'
                  'color:%s;white-space:nowrap">%s</span></div></div>%s</div>'
                  % (8.6 if len(r['halves']) == 1 else 6.6, INK, esc(ar), MUTE, esc(en), tag))
    bc_svg = barcode_svg(code, 8).replace('width="56mm" height="8mm"', 'width="64mm" height="9.1mm"')
    return (
        '<div style="width:%dmm;height:%dmm;background:%s;color:%s;border-radius:5mm;overflow:hidden;position:relative;'
        'font-family:Cairo,sans-serif;display:flex;flex-direction:column;direction:ltr;border:1.2mm solid %s;box-sizing:border-box">'
        # zone header
        '<div style="background:%s;color:#fff;display:flex;align-items:center;padding:0 7mm;height:30mm;gap:6mm">'
        '<div style="font-weight:900;font-size:21mm;line-height:1">%s</div>'
        '<div style="flex:1;line-height:1.15"><div style="font-weight:900;font-size:7.4mm">%s · %s</div>'
        '<div dir="rtl" style="font-weight:900;font-size:9mm">%s</div></div>'
        '<div style="background:%s;color:%s;border-radius:2mm;padding:1.4mm 4mm;text-align:center;line-height:1.1">'
        '<div style="font-weight:900;font-size:6.4mm">%s</div><div dir="rtl" style="font-weight:900;font-size:5.4mm">%s</div></div></div>'
        '<div style="height:2.4mm;background:repeating-linear-gradient(135deg,%s 0 3mm,%s 3mm 6mm)"></div>'
        '<div style="padding:4mm 7mm 0 7mm;display:flex;flex-direction:column;flex:1;min-height:0">'
        # rack number + load type
        '<div style="display:flex;align-items:center;gap:6mm">'
        '<div style="line-height:.9"><span style="font-weight:900;font-size:6mm;color:%s">RACK · راك</span><br>'
        '<span style="font-weight:900;font-size:30mm;color:%s">%d</span></div>'
        '<div style="flex:1;border-left:.6mm solid %s;padding-left:6mm;line-height:1.2">'
        '<div style="font-weight:900;font-size:3.6mm;color:%s">LOAD TYPE · نوع الحمولة</div>'
        '<div dir="rtl" style="font-weight:900;font-size:8mm;color:%s">%s · %s</div>'
        '<div style="font-weight:700;font-size:3.8mm;color:%s">GMA WOODEN PALLET · 1200 × 1000 mm<br>'
        '<span dir="rtl">بالت خشبي قياسي</span></div></div></div>'
        # goods
        '<div style="margin-top:3mm;border-top:.6mm solid %s;padding-top:2.4mm">'
        '<div style="font-weight:900;font-size:3.6mm;color:%s;margin-bottom:1mm">GOODS · نوع البضاعة</div>%s</div>'
        # capacity hero
        '<div style="margin-top:1.4mm;background:%s;color:#fff;border-radius:3mm;padding:2.4mm 6mm;display:flex;align-items:center;gap:5mm">'
        '<div style="line-height:1"><div style="font-weight:900;font-size:3.4mm;color:%s">RACK CAPACITY · وزن الراك</div>'
        '<div style="font-weight:900;font-size:20mm;color:%s;line-height:1">%s<span style="font-size:8mm;color:#fff"> kg</span></div></div>'
        '<div style="flex:1;text-align:right;line-height:1.15"><div style="font-weight:900;font-size:9mm;color:#fff">%d × %s</div>'
        '<div dir="rtl" style="font-weight:900;font-size:5mm;color:%s">%d بالت × %s كجم</div>'
        '<div style="font-size:3.2mm;font-weight:700;color:#C9D3DE">PALLETS × KG PER PALLET</div></div></div>'
        # grid
        '<div style="margin-top:2.4mm;flex:1;min-height:0">%s</div>'
        '</div>'
        # footer
        '<div style="background:%s;display:flex;align-items:center;gap:4mm;padding:1.6mm 7mm;height:17mm;box-sizing:border-box">'
        '<div style="background:%s;padding:1mm 1.4mm .4mm 1.4mm;border-radius:1mm;line-height:0">%s</div>'
        '<div style="font-weight:900;font-size:7mm;color:%s;letter-spacing:.3mm">%s</div>'
        '<div dir="rtl" style="flex:1;text-align:left;font-weight:900;font-size:4.6mm;color:#fff;line-height:1.2">'
        'لا تتجاوز الحمولة<br><span dir="ltr" style="font-size:3.4mm;color:%s">DO NOT OVERLOAD</span></div></div>'
        '</div>'
        % (SW, SH, PAPER, INK, INK,
           t['hdr'], t['code'], t['tag'], t['en'], t['name_ar'],
           bc, '#fff', bn, bar,
           YEL, INK,
           MUTE, INK, r['no'], MUTE, MUTE, INK, t['ar'], t['en'], MUTE,
           MUTE, MUTE, goods,
           INK, YEL, YEL, nf(total), pallets, nf(KG), YEL, pallets, nf(KG),
           pallet_grid(r, t['hdr']),
           INK, PAPER, bc_svg, YEL, code, YEL))


def marks():
    f = lambda v: '%.1f' % v
    x0, y0, x1, y1 = LEFT, TOP, LEFT + SW, TOP + SH
    k = []
    for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        sx, sy = (-1 if x == x0 else 1), (-1 if y == y0 else 1)
        k.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(x + sx * 2), f(y), f(x + sx * 8), f(y)))
        k.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(x), f(y + sy * 2), f(x), f(y + sy * 8)))
    return ('<svg style="position:absolute;left:0;top:0" width="%dmm" height="%dmm" viewBox="0 0 %d %d">'
            '<g stroke="#555" stroke-width=".25" fill="none">%s</g>'
            '<rect x="%s" y="%s" width="%d" height="%d" rx="5" stroke="#E6007E" stroke-width=".3" fill="none" stroke-dasharray="2.2 1.2"/></svg>'
            % (PGW, PGH, PGW, PGH, ''.join(k), f(x0), f(y0), SW, SH))


def build(out_dir):
    racks = build_racks()
    pages, n = [], 0
    for z in ('c', 'p', 'b'):
        for r in racks[z]:
            n += 1
            note = ('<div style="position:absolute;left:0;right:0;bottom:3mm;text-align:center;font:700 3mm Cairo,sans-serif;color:#7A8896">'
                    '%s-%s-%d · اطبع نسختين (جانبي الراك) · PRINT ×2</div>' % (TYPES[z]['code'], r['brand'], r['no']))
            pages.append('<div class="pg" style="width:%dmm;height:%dmm"><div style="position:absolute;left:%.1fmm;top:%.1fmm">%s</div>%s%s</div>'
                         % (PGW, PGH, LEFT, TOP, sign(z, r), marks(), note))
    doc = ('<!doctype html><html lang="ar"><head><meta charset="utf-8"><title>Al-Munajem Rack Side Signs %s</title>'
           '<style>%s</style></head><body>%s%s</body></html>' % (VERSION, m.page_css(PGW, PGH), ''.join(pages), m.FIT_JS))
    p = os.path.join(out_dir, 'almunajem_rack_side_signs_%s_%s.html' % (VERSION, DATE))
    open(p, 'w', encoding='utf-8').write(doc)
    return p, n


if __name__ == '__main__':
    print(build(sys.argv[1] if len(sys.argv) > 1 else '.'))
