#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BIG yellow rack labels, one per A4 landscape page (277 x 178 mm label, same design as the 78 x 50 mm rack sticker).
 cartons A-D (4) · plastic A-E (5) · boxes A-E (5) · packing supplies: ONE label per item (10, product colour).
usage: python3 make_big_labels.py <out_dir>"""
import os, sys, html
import make_stickers as m
import make_zone1_system as z
from make_stickers import TYPES, LETTERS, INK, YEL, arrow, barcode_svg

esc = html.escape
VER, DATE = 'v1', '2026-10-11'
K = 277 / 78.0      # scale of the small sticker

def big_arrow(down):
    return arrow(down).replace('width="9.5mm" height="10.5mm"', 'width="33mm" height="36.5mm"')

def side(arr, letter, en, ar):
    return ('<div style="width:62mm;display:flex;flex-direction:column;align-items:center;gap:2mm">%s'
            '<span dir="ltr" style="font-weight:900;font-size:15mm;line-height:1">%s</span>'
            '<span style="display:flex;gap:4mm;white-space:nowrap;font-weight:800;font-size:9.5mm;line-height:1.05"><span dir="ltr">%s</span><span dir="rtl">%s</span></span></div>'
            % (arr, letter, en, ar))

def barcode_big(code):
    return barcode_svg(code, 9).replace('width="56mm" height="9mm"', 'width="120mm" height="17mm" preserveAspectRatio="none"')

def frame(inner):
    return ('<div style="position:absolute;left:10mm;top:16mm;width:277mm;height:178mm;background:%s;border:4mm solid %s;border-radius:14mm;overflow:hidden;'
            'direction:ltr;display:flex;flex-direction:column;font-family:\'Cairo\',sans-serif;color:%s;box-sizing:border-box">%s</div>' % (YEL, INK, INK, inner))

def level_label(zt, L_idx):
    T = TYPES[zt]
    L = LETTERS[L_idx - 1]
    tiers = T['tiers']
    dn = ('FLOOR', 'DOWN', 'أسفل · أرضي') if L_idx == 1 else (LETTERS[L_idx - 2], 'DOWN', 'أسفل')
    up = ('TOP', 'UP', 'أعلى · علوي') if L_idx == tiers else (LETTERS[L_idx], 'UP', 'أعلى')
    code = '%s-%s' % (T['code'], L)
    hd = ('<div style="height:34mm;background:%s;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 12mm;font-weight:900;white-space:nowrap">'
          '<span dir="ltr" style="font-size:15mm;min-width:36mm">%s</span><span style="font-size:16mm;display:flex;gap:6mm;align-items:baseline"><span dir="rtl">%s</span><span>·</span><span dir="ltr">%s</span></span>'
          '<span dir="ltr" style="font-size:15mm;min-width:36mm;text-align:right">%s</span></div>' % (T['hdr'], T['tag'], T['ar'], T['en'], T['code']))
    pn = ('<div style="height:26mm;background:#F2C200;border-bottom:1.6mm solid %s;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1.1">'
          '<div dir="rtl" style="font-weight:800;font-size:12mm">%s <span style="font-weight:700">· LEVEL / المستوى %s</span></div>'
          '<div dir="ltr" style="font-weight:700;font-size:7mm;opacity:.85">%s</div></div>' % (INK, esc(T['name_ar']), L, esc(T['desc'])))
    mid = ('<div style="flex:1;display:flex;align-items:center;justify-content:space-between;padding:0 14mm;position:relative">%s'
           '<div dir="ltr" style="font-weight:900;font-size:96mm;line-height:.8;letter-spacing:-2mm;padding-bottom:2mm">%s</div>%s'
           '</div>' % (side(big_arrow(True), dn[0], dn[1], dn[2]), L, side(big_arrow(False), up[0], up[1], up[2])))
    p0 = (L_idx - 1) * 5 + 1
    badge = lambda t, bg, fg, bd='': ('<div dir="ltr" style="background:%s;color:%s;%sborder-radius:6mm;padding:0 6mm;font-weight:900;font-size:10mm;line-height:1.3;white-space:nowrap">%s</div>' % (bg, fg, bd, t))
    ft = ('<div style="height:30mm;display:flex;align-items:center;justify-content:space-between;padding:0 12mm 4mm">'
          '<div style="display:flex;flex-direction:column;gap:2mm">%s%s</div>'
          '<div style="display:flex;flex-direction:column;align-items:center;gap:1mm">%s<span dir="ltr" style="font-weight:900;font-size:8mm;letter-spacing:3mm">%s</span></div>'
          '<div style="width:60mm"></div></div>'
          % (badge('P%d–P%d' % (p0, p0 + 4), YEL, INK, 'border:1.2mm solid %s;' % INK), badge('%s1–%s5' % (L, L), INK, YEL), barcode_big(code), code))
    return frame(hd + pn + mid + ft), code

def supply_label(r):
    it = r['halves'][0]['item']
    T = TYPES['a']
    bg, fg, pill = m.hdr_style(T, it)
    pl = 'background:#fff;color:#111;border-radius:8mm;padding:0 10mm;' if pill else ''
    code = '%s-GN-%d' % (T['code'], r['no'])
    hd = ('<div style="height:34mm;background:%s;color:%s;border-bottom:1.6mm solid %s;display:flex;align-items:center;justify-content:space-between;padding:0 12mm;font-weight:900;white-space:nowrap">'
          '<span dir="ltr" style="font-size:15mm;min-width:36mm;%s">%s</span><span style="font-size:16mm;display:flex;gap:6mm;align-items:baseline;%s"><span dir="rtl">%s</span><span>·</span><span dir="ltr">%s</span></span>'
          '<span dir="ltr" style="font-size:15mm;min-width:36mm;text-align:right;%s">%s</span></div>' % (bg, fg, INK, pl, T['tag'], pl, T['name_ar'], 'SUPPLY', pl, T['code']))
    name = ('<div style="flex:1;background:#F2C200;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 14mm;line-height:1.1;gap:5mm">'
            '<div data-fit dir="rtl" style="white-space:nowrap;font-weight:900;font-size:34mm">%s</div>'
            '<div data-fit dir="ltr" style="white-space:nowrap;font-weight:800;font-size:19mm;opacity:.9">%s</div>'
            '<div style="display:flex;gap:10mm;align-items:center;margin-top:3mm"><span style="width:44mm;height:16mm;border:1.2mm solid %s;border-radius:4mm;background:%s;display:inline-block"></span>'
            '<span dir="ltr" style="font-weight:800;font-size:9mm">%s · %s</span><span dir="rtl" style="font-weight:800;font-size:10mm">%s · %s</span></div></div>'
            % (esc(it['ar']), esc(it['en'].strip()), INK, bg, esc(it['cen']), esc(it['uen']), esc(it['car']), esc(it['uar'])))
    ft = ('<div style="height:44mm;display:flex;align-items:center;justify-content:space-between;padding:0 14mm 4mm;border-top:1.6mm solid %s">'
          '<div style="display:flex;flex-direction:column;align-items:center;line-height:1"><span dir="rtl" style="font-weight:800;font-size:9mm">راك</span>'
          '<span dir="ltr" style="font-weight:800;font-size:8mm">RACK</span></div>'
          '<div dir="ltr" style="font-weight:900;font-size:40mm;line-height:.9">%d</div>'
          '<div style="display:flex;flex-direction:column;align-items:center;gap:1mm">%s<span dir="ltr" style="font-weight:900;font-size:8mm;letter-spacing:3mm">%s</span></div></div>'
          % (INK, r['no'], barcode_big(code), code))
    return frame(hd + name + ft), code

def big_pages():
    """list of (section html, id, en, ar)"""
    out = []
    for zt in ('c', 'p', 'b'):
        T = TYPES[zt]
        for i in range(1, T['tiers'] + 1):
            lab, code = level_label(zt, i)
            L = LETTERS[i - 1]
            out.append(('<section class="pg l" id="big-%s-%s">%s</section>' % (zt, L, lab), 'big-%s-%s' % (zt, L),
                       'Big rack label %s %s · level %s' % (T['tag'], T['en'], L), 'ليبل راك كبير %s %s · المستوى %s' % (T['tag'], T['ar'], L)))
    for r in m.build_racks()['a']:
        lab, code = supply_label(r)
        it = r['halves'][0]['item']
        out.append(('<section class="pg l" id="big-a-%d">%s</section>' % (r['no'], lab), 'big-a-%d' % r['no'],
                   'Big rack label A4 SUPPLY · %s' % it['en'].strip(), 'ليبل راك كبير A4 · %s' % it['ar']))
    return out

def build(out):
    os.makedirs(out, exist_ok=True)
    pages = big_pages()
    doc = ('<!-- VERSION: %s | %s -->\n<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><title>Al-Munajem Big rack labels %s</title><style>%s</style></head><body>%s%s</body></html>'
           % (VER, DATE, VER, z.css(), ''.join(p[0] for p in pages), m.FIT_JS))
    p = os.path.join(out, 'almunajem_BIG_rack_labels_A4_%s_%s.html' % (VER, DATE))
    open(p, 'w', encoding='utf-8').write(doc)
    print(p, len(pages))

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '.')
