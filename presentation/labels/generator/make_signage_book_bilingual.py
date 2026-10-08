#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dry-storage signage book — pages 1-4 (locator + signage maps) rebuilt FULLY bilingual (AR + EN on every text).
Pages 5-68 (the banners) of the original book are already bilingual and are appended unchanged by the merge step.
usage: python3 make_signage_book_bilingual.py <out.html>
"""
import sys, html
import make_stickers as m

W, H = 458.3, 297.4            # mm, same page size as the original book
BG, INK, MUTE = '#FAF5EC', '#3A2412', '#6B5A4A'
ZC = {'c': '#9A6A2F', 'p': '#1E7A8C', 'b': '#6A3FA0'}
BR = {'DX': ('#1F4E9E', 'دو', 'DOUX'), 'DR': ('#A3261F', 'داري', 'DARI'), 'HB': ('#8A4B0F', 'الهبرة', 'AL HABRA'),
      'SA': ('#14633F', 'السعودي', 'SAUDI'), 'GN': ('#3D5563', 'عام', 'GENERAL')}
esc = html.escape
T = {'ملون': 'COLORED', 'أبيض': 'WHITE', 'فرم': 'MINCE', '': ''}

# (no, arabic name, size, english name)
CART = {
    'DX': [(8, 'كرتون صدور دجاج دو', '10 × 1', 'CARTON CHICKEN BREAST DOUX'), (9, 'كرتون صدور دجاج دو', '5 × 2', 'CARTON CHICKEN BREAST DOUX'),
           (10, 'كرتون ستربس دجاج دو عادي', '12 × 700', 'CARTON DOUX REGULAR CHICKEN STRIPS'), (11, 'كرتون ستربس دجاج دو سبايسي', '12 × 700', 'CARTON DOUX SPICY CHICKEN STRIPS'),
           (13, 'كرتون برجر دجاج دو', '12 × 660', 'CARTON CHICKEN BURGER DOUX'), (14, 'كرتون برجر دجاج بقسماط دو', '12 × 660', 'CARTON CHICKEN BREADED BURGER DOUX'),
           (15, 'كرتون ناجتس دجاج بقسماط دو', '12 × 500', 'CARTON CHICKEN BREADED NUGGETS DOUX'), (16, 'كرتون ناجتس دجاج بقسماط دو', '10 × 1', 'CARTON CHICKEN BREADED NUGGETS DOUX'),
           (17, 'كرتون فنجر دجاج بقسماط دو', '12 × 500', 'CARTON CHICKEN BREADED FINGERS DOUX'), (18, 'كرتون ستيك دجاج بقسماط دو', '12 × 500', 'CARTON CHICKEN BREADED STEAK DOUX')],
    'DR': [(4, 'كرتون ضأن مفروم داري', '20 × 400', 'CARTON MUTTON MINCE DARI'), (6, 'كرتون صدور دجاج داري', '10 × 1', 'CARTON CHICKEN BREAST DARI'),
           (7, 'كرتون صدور دجاج داري', '5 × 2', 'CARTON CHICKEN BREAST DARI')],
    'HB': [(2, 'كرتون هبرة ضأن مفروم أنعام سعودي', '20 × 400', 'CARTON MUTTON MINCE ANAM SAUDI AL HABRA'),
           (12, 'كرتون برجر دجاج بقسماط الهبرة', '8 × 885', 'CARTON BREADED BURGER AL HABRA')],
    'SA': [(1, 'كرتون لحم بقري مفروم أنعام سعودي', '20 × 400', 'CARTON BEEF MINCE ANAM SAUDI'),
           (3, 'كرتون ضأن مفروم أنعام سعودي', '20 × 400', 'CARTON MUTTON MINCE ANAM SAUDI'), (5, 'كرتون دجاج مفروم داري', '20 × 400', 'CARTON CHICKEN MINCE DARI')],
}
PLAS = {
    'DX': [(2, 'صدور دجاج دو', '10 × 1 · ملون', 'CHICKEN BREAST DOUX 10 × 1 · COLORED'), (4, 'صدور دجاج دو', '5 × 2 · ملون', 'CHICKEN BREAST DOUX 5 × 2 · COLORED'),
           (5, 'ستربس دو عادي', '12 × 700 · ملون', 'DOUX REGULAR STRIPS 12 × 700 · COLORED'), (6, 'ستربس دو سبايسي', '12 × 700 · ملون', 'DOUX SPICY STRIPS 12 × 700 · COLORED'),
           (7, 'ناجتس بقسماط دو', '10 × 1 · ملون', 'BREADED NUGGETS DOUX 10 × 1 · COLORED'), (10, 'برجر بقسماط دو', '12 × 660 · أبيض', 'BREADED BURGER DOUX 12 × 660 · WHITE'),
           (11, 'ناجتس بقسماط دو', '12 × 500 · أبيض', 'BREADED NUGGETS DOUX 12 × 500 · WHITE'), (12, 'ناجتس بقسماط دو', '10 × 1 · أبيض', 'BREADED NUGGETS DOUX 10 × 1 · WHITE'),
           (13, 'فنجر بقسماط دو', '12 × 500 · أبيض', 'BREADED FINGERS DOUX 12 × 500 · WHITE'), (14, 'ستيك بقسماط دو', '12 × 500 · أبيض', 'BREADED STEAK DOUX 12 × 500 · WHITE'),
           (15, 'ستربس دو عادي', '700 GM · أبيض', 'REGULAR STRIPS DOUX 700 GM · WHITE'), (16, 'ستربس دو سبايسي', '700 GM · أبيض', 'SPICY STRIPS DOUX 700 GM · WHITE'),
           (17, 'صدور دجاج دو', '1 KG · أبيض', 'CHICKEN BREAST DOUX 1 KG · WHITE'), (18, 'صدور دجاج دو', '2 KG · أبيض', 'CHICKEN BREAST DOUX 2 KG · WHITE')],
    'DR': [(1, 'صدور دجاج داري', '10 × 1 · ملون', 'CHICKEN BREAST DARI 10 × 1 · COLORED'), (3, 'صدور دجاج داري', '5 × 2 · ملون', 'CHICKEN BREAST DARI 5 × 2 · COLORED'),
           (19, 'صدور دجاج داري', '1 KG · أبيض', 'CHICKEN BREAST DARI 1 KG · WHITE'), (20, 'صدور دجاج داري', '2 KG · أبيض', 'CHICKEN BREAST DARI 2 KG · WHITE'),
           (24, 'ضأن مفروم داري', '20 × 400 · فرم', 'MUTTON MINCE DARI 20 × 400 · MINCE')],
    'HB': [(8, 'برجر بقسماط الهبرة', '8 × 885 · ملون', 'BREADED BURGER AL HABRA 8 × 885 · COLORED'), (9, 'برجر بقسماط الهبرة', '8 × 885 · أبيض', 'BREADED BURGER AL HABRA 8 × 885 · WHITE'),
           (22, 'هبرة ضأن مفروم أنعام سعودي', '20 × 400 · فرم', 'MUTTON MINCE ANAM SAUDI AL HABRA 20 × 400 · MINCE')],
    'SA': [(21, 'لحم بقري مفروم أنعام سعودي', '20 × 400 · فرم', 'BEEF MINCE ANAM SAUDI 20 × 400 · MINCE'),
           (23, 'ضأن مفروم أنعام سعودي', '20 × 400 · فرم', 'MUTTON MINCE ANAM SAUDI 20 × 400 · MINCE'), (25, 'دجاج مفروم داري', '20 × 400 · فرم', 'CHICKEN MINCE DARI 20 × 400 · MINCE')],
    'GN': [(26, 'فيلم بلاستيك غير مطبوع', '510 MM', 'UNPRINTED PLASTIC FILM ROLL 510 MM'), (27, 'رول فيلم شرينك', '', 'SHRINK FILM ROLL')],
}
BOXES = {'DX': [(1, 'علبة تعبئة فنجر دجاج دو', '500 G', 'PACKAGING BOX DOUX CHICKEN FINGERS'), (2, 'علبة تعبئة ناجتس دجاج دو', '500 G', 'PACKAGING BOX DOUX CHICKEN NUGGETS'),
                 (3, 'علبة تعبئة ستيك دجاج دو', '600 G', 'PACKAGING BOX DOUX CHICKEN STEAK'), (4, 'علبة تعبئة برجر دجاج بقسماط دو', '660 G', 'PACKAGING BOX DOUX CHICKEN BREADED BURGER'),
                 (5, 'علبة تعبئة برجر دو', '660 G', 'PACKAGING BOX DOUX BURGER')]}


def head(title_ar, title_en):
    return ('<div style="display:flex;justify-content:space-between;align-items:center;direction:ltr">'
            '<div style="font-weight:900;font-size:5.2mm;letter-spacing:.5mm;color:%s">%s</div>'
            '<div dir="rtl" style="font-weight:900;font-size:9mm;color:%s">%s</div></div>' % (INK, title_en, INK, title_ar))


def crumb(n_ar, n_en, code, count, zone_color):
    box = lambda bg, col, ar, en, sub, w: (
        '<div style="background:%s;color:%s;border-radius:4mm;padding:4mm 6mm;width:%dmm;box-sizing:border-box;text-align:right">'
        '<div dir="rtl" style="font-weight:900;font-size:13mm;line-height:1.1">%s</div>'
        '<div style="font-weight:700;font-size:4.2mm;letter-spacing:.7mm;opacity:.9;direction:ltr;text-align:right">%s</div></div>' % (bg, col, w, ar, sub))
    return ('<div style="display:flex;align-items:center;gap:6mm;direction:ltr;margin:6mm 0 4mm 0;flex-direction:row-reverse">'
            + box('#6B4226', '#fff', 'القسم الجاف<br><span style="font-size:6.5mm;font-weight:700">DRY STORAGE</span>', '', 'A · DRY STORAGE · القسم الجاف', 110)
            + '<div style="font-size:7mm;color:%s">◂</div>' % INK
            + box(zone_color, '#fff', n_ar + '<br><span style="font-size:6.5mm;font-weight:700">%s</span>' % n_en, '', '%s · %s · %d' % (code, n_en, count), 110)
            + '<div style="font-size:7mm;color:%s">◂</div>' % INK
            + '<div style="flex:1;border:.5mm dashed #8A6A3F;border-radius:4mm;height:34mm;display:flex;align-items:center;justify-content:space-between;'
              'padding:0 8mm;font-weight:900;font-size:5mm;color:%s"><span>A3 · A4 · …</span><span dir="rtl">أدوات أخرى · قادم</span>'
              '<span style="direction:ltr">OTHER TOOLS · COMING SOON</span></div></div>' % INK)


def szh(size):
    parts = size.split(' · ')
    out = '<span dir="ltr" style="unicode-bidi:isolate">%s</span>' % esc(parts[0])
    return out + (' · ' + esc(parts[1]) if len(parts) > 1 else '')


def card(code, br, items, width):
    col, ar, en = BR[br]
    two = len(items) > 6
    rows = ''
    for no, a, size, e in items:
        rows += ('<div style="display:flex;align-items:center;gap:2.4mm;padding:2mm 0;border-top:.3mm solid rgba(255,255,255,.28);direction:rtl">'
                 '<div style="min-width:7.2mm;height:7.2mm;border-radius:50%%;background:#E4EDFF;color:%s;display:flex;align-items:center;'
                 'justify-content:center;font-weight:900;font-size:3.6mm">%d</div>'
                 '<div style="flex:1;min-width:0;line-height:1.2"><div style="font-weight:700;font-size:4.2mm">%s %s</div>'
                 '<div dir="ltr" style="font-weight:600;font-size:3mm;opacity:.9;text-align:right">%s</div></div></div>'
                 % (col, no, esc(a), szh(size), esc(e)))
    body = ('<div style="display:grid;grid-template-columns:%s;column-gap:5mm">%s</div>' % ('1fr 1fr' if two else '1fr', rows))
    plural = ('صنفان' if len(items) == 2 else 'أصناف')
    return ('<div style="background:%s;color:#fff;border-radius:4mm;padding:4mm 5mm;box-sizing:border-box;width:%.1fmm;flex:none">'
            '<div style="display:flex;justify-content:space-between;align-items:center;direction:rtl">'
            '<div style="font-weight:900;font-size:8mm;line-height:1">%s<div dir="ltr" style="font-size:3.6mm;font-weight:700;letter-spacing:.6mm;text-align:right;margin-top:1mm">%s</div></div>'
            '<div style="background:#E4EDFF;color:%s;border-radius:5mm;padding:.6mm 3.2mm;font-weight:900;font-size:3.8mm;direction:ltr">%s</div></div>'
            '<div style="display:flex;justify-content:space-between;font-weight:900;font-size:3.5mm;margin:3mm 0 2mm 0;opacity:.95;direction:ltr">'
            '<span>%s · %d ITEMS</span><span dir="rtl">%d %s</span></div>%s</div>'
            % (col, width, ar, en, col, code, en, len(items), len(items), plural, body))


def map_page(zk, n_ar, n_en, code, data, order_ar, order_en):
    total = sum(len(v) for v in data.values())
    brs = list(data.keys())
    weights = [2.8 if len(data[b]) > 6 else 1 for b in brs]
    avail = W - 36 - 5 * (len(brs) - 1)
    sw = sum(weights)
    cards = ''.join(card('%s.%d' % (code, i + 1), b, data[b], (avail if len(brs) == 1 else avail * w / sw)) for i, (b, w) in enumerate(zip(brs, weights)))
    sub = ('<div style="font-weight:900;font-size:6mm;color:%s;margin:2mm 0 4mm 0;display:flex;justify-content:space-between;direction:rtl">'
           '<span>%s — %s ← الماركات ← الأصناف</span><span dir="ltr">%s — %s → BRANDS → ITEMS</span></div>' % (INK, code, n_ar, code, n_en))
    foot = ('<div style="margin-top:5mm;font-size:3.6mm;color:%s;display:flex;justify-content:space-between;gap:10mm">'
            '<span dir="rtl">ترتيب الطباعة داخل الملف: الدليل ← A ← A1 والماركات والأصناف ← A2 والماركات والأصناف ← A3 والماركات والأصناف.</span>'
            '<span dir="ltr" style="text-align:left">Print order in the file: Guide → A → A1 with brands and items → A2 with brands and items → A3 with brands and items.</span></div>' % MUTE)
    return ('<div class="pg" style="width:%.1fmm;height:%.1fmm;background:%s;font-family:Cairo,sans-serif;padding:14mm 18mm;box-sizing:border-box">'
            '%s%s%s<div style="display:flex;gap:5mm;flex-direction:row-reverse;align-items:flex-start">%s</div>%s</div>'
            % (W, H, BG, head('دليل لافتات القسم الجاف · المنجم للأغذية', 'DRY STORAGE SIGNAGE MAP · AL-MUNAJEM FOODS'),
               crumb(n_ar, n_en, code, total, ZC[zk]), sub, cards, foot))


def locator():
    def racks(x, y, n, w, color, rh=5.2, gap=1.1):
        return ''.join('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx=".8" fill="%s"/>' % (x, y + i * (rh + gap), w, rh, color) for i in range(n))
    svg = ['<rect x="2" y="2" width="146" height="236" rx="6" fill="#FFFDF8" stroke="#9A8467" stroke-width="1"/>']
    zones = [(8, 'SPIC · ZONE 3 · المنطقة 3', 'c'), (86, 'FORM · ZONE 2 · المنطقة 2', None), (164, 'PKG · ZONE 1 · المنطقة 1', 'p')]
    for (y0, lab, kind), zi in zip(zones, (3, 2, 1)):
        for side, x in (('L', 12), ('R', 84)):
            col = '#D9D3C8'
            n = 11
            if zi == 3 and side == 'L':
                col = ZC['c']
            if zi == 1 and side == 'R':
                col = ZC['p']
            svg.append(racks(x, y0, n, 54, col))
        if zi == 1:   # boxes: lowest 6 racks of the left side
            svg.append(racks(12, y0 + 5 * 6.3, 6, 54, ZC['b']))
            svg.append('<rect x="12" y="%.1f" width="54" height="%.1f" fill="#D9D3C8"/>' % (y0 + 5 * 6.3 + 6 * 6.3 - .9 - 0.0, 0))
        svg.append('<text transform="translate(75,%d) rotate(-90)" font-size="5" font-weight="900" fill="%s" text-anchor="middle">%s</text>' % (y0 + 34, MUTE, lab))
    for y, en, ar in ((75, 'EMERGENCY DOOR · BETWEEN ZONES 2 & 3', 'باب الطوارئ · فاصل بين المنطقة 2 و 3'),
                      (153, 'EMERGENCY DOOR · BETWEEN ZONES 1 & 2', 'باب الطوارئ · فاصل بين المنطقة 1 و 2')):
        svg.append('<rect x="4" y="%d" width="142" height="9" fill="#EFC9C9"/>'
                   '<text x="75" y="%.1f" font-size="3.3" font-weight="900" fill="#8A1F1F" text-anchor="middle">%s</text>'
                   '<text x="75" y="%.1f" font-size="3.3" font-weight="900" fill="#8A1F1F" text-anchor="middle">%s</text>' % (y - 1, y + 3, en, y + 7, ar))
    svg.append('<rect x="52" y="233" width="46" height="9" rx="2" fill="%s"/><text x="75" y="239" font-size="3.6" font-weight="900" fill="#fff" text-anchor="middle">MAIN DOOR ▲ الباب الرئيسي</text>' % INK)
    svg.append('<text x="-2" y="207" font-size="4" font-weight="900" fill="%s" text-anchor="end">A3 · RACK 1 · الراك 1</text>' % ZC['b'])
    svg.append('<text x="-2" y="26" font-size="4" font-weight="900" fill="%s" text-anchor="end">A1 · RACK 1 · الراك 1</text>' % ZC['c'])
    svg.append('<text x="152" y="224" font-size="4" font-weight="900" fill="%s">A2 · RACK 1 · الراك 1</text>' % ZC['p'])
    svgs = '<svg viewBox="-42 0 232 244" width="240mm" height="252mm">%s</svg>' % ''.join(svg)

    def blk(color, tag, ar, en, rows):
        r = ''.join('<div style="display:flex;justify-content:space-between;gap:6mm;font-size:3.7mm;line-height:1.5"><span dir="ltr">%s</span><span dir="rtl">%s</span></div>' % (e, a) for a, e in rows)
        return ('<div style="background:%s;color:#fff;border-radius:4mm;padding:4mm 6mm;margin-bottom:4mm">'
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2mm;direction:ltr">'
                '<span style="font-weight:900;font-size:7mm">%s · %s</span><span style="display:flex;align-items:center;gap:3mm;font-weight:900;font-size:7mm" dir="rtl">%s'
                '<span style="background:#fff;color:%s;border-radius:5mm;padding:0 3mm;font-size:5mm">%s</span></span></div>%s</div>' % (color, tag, en, ar, color, tag, r))
    right = (blk(ZC['c'], 'A1', 'الكراتين', 'CARTONS', [
        ('المنطقة 3 (SPIC) · الجهة اليسرى', 'Zone 3 (SPIC) · left side'), ('الرف العالي 246 سم · 4 أدوار · 5 بالت', 'Top shelf 246 cm · 4 levels · 5 pallets'),
        ('الراك 1 عند ركن باب الطوارئ', 'Rack 1 at the emergency-door corner'), ('الترتيب: دو ← داري ← الهبرة ← السعودي', 'Order: Doux → Dari → Al Habra → Saudi'),
        ('الراك 15 احتياطي عند جدار نهاية الغرفة', 'Rack 15 is spare, at the room-end wall')])
        + blk(ZC['p'], 'A2', 'البلاستيك', 'PLASTIC', [
        ('المنطقة 1 (PKG) · الجهة اليمنى', 'Zone 1 (PKG) · right side'), ('رف 175 سم · 5 أدوار · 5 بالت', 'Shelf 175 cm · 5 levels · 5 pallets'),
        ('الراك 1 عند ركن الباب الرئيسي', 'Rack 1 at the main-door corner'), ('الترتيب: دو ← داري ← الهبرة ← السعودي ← عام', 'Order: Doux → Dari → Al Habra → Saudi → General')])
        + blk(ZC['b'], 'A3', 'علب التعبئة', 'PACKAGING BOXES', [
        ('المنطقة 1 (PKG) · الجهة اليسرى', 'Zone 1 (PKG) · left side'), ('رف 175 سم · 5 أدوار · 5 بالت', 'Shelf 175 cm · 5 levels · 5 pallets'),
        ('الراك 1 عند ركن الباب الرئيسي', 'Rack 1 at the main-door corner'), ('أصناف دو الخمسة: 1 ← 5 ← 2 ← 4 ← 3 (البرجر متباعد)', 'Five Doux items: 1 → 5 → 2 → 4 → 3 (burgers kept apart)')]))
    note = ('<div style="font-size:3.5mm;color:%s;line-height:1.5"><div dir="rtl">اليمين واليسار بالنسبة لمن يدخل من الباب الرئيسي ويواجه نهاية الغرفة. الراك 1 هو الأقرب لبداية المنطقة، والترقيم يزيد باتجاه جدار نهاية الغرفة.</div>'
            '<div dir="ltr">Right and left are relative to someone entering through the main door and facing the room end. Rack 1 is the nearest to the start of the zone, and numbering increases toward the room-end wall.</div></div>' % MUTE)
    return ('<div class="pg" style="width:%.1fmm;height:%.1fmm;background:%s;font-family:Cairo,sans-serif;padding:12mm 16mm;box-sizing:border-box;display:flex;gap:10mm;direction:ltr">'
            '<div style="flex:none">%s</div><div style="flex:1;min-width:0">'
            '<div dir="rtl" style="font-weight:900;font-size:10mm;line-height:1.15;color:%s">أين تقع الكراتين والبلاستيك وعلب التعبئة؟</div>'
            '<div style="font-weight:900;font-size:8mm;line-height:1.15;color:%s;margin-top:1mm">Where are the cartons, plastic and packaging boxes?</div>'
            '<div style="display:flex;justify-content:space-between;font-weight:900;font-size:3.6mm;letter-spacing:.4mm;color:%s;margin:3mm 0 4mm 0">'
            '<span>DRY ROOM LOCATOR · ZONE · SIDE · START CORNER</span><span dir="rtl">دليل الغرفة الجافة · المنطقة · الجهة · ركن البداية</span></div>%s%s</div></div>'
            % (W, H, BG, svgs, INK, INK, MUTE, right, note))


def build(out):
    pages = [locator(),
             map_page('c', 'الكراتين', 'CARTONS', 'A1', CART, '', ''),
             map_page('p', 'البلاستيك', 'PLASTIC', 'A2', PLAS, '', ''),
             map_page('b', 'علب التعبئة', 'PACKAGING BOXES', 'A3', BOXES, '', '')]
    doc = ('<!doctype html><html lang="ar"><head><meta charset="utf-8"><title>Dry signage book p1-4 bilingual</title><style>%s</style></head><body>%s%s</body></html>'
           % (m.page_css(W, H), ''.join(pages), m.FIT_JS))
    open(out, 'w', encoding='utf-8').write(doc)


if __name__ == '__main__':
    build(sys.argv[1])
    print('ok')
