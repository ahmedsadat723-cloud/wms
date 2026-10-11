#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Al-Munajem DRY PART 1 — PLAN B (backup) for the CARTON zone: every rack split in halves = 30 item slots (bilingual).
usage: python3 make_plan_b.py <out_dir>"""
import os, sys, json, copy
import make_stickers as m
import make_zone1_system as z
from make_zone1_system import esc, BR, LETTERS, TYPES

VER, DATE = 'v1', '2026-10-11'
RES = dict(ar='محجوز لصنف جديد', size='', en='RESERVED · NEW ITEM', reserved=True)

def stats(racks):
    n_items = sum(1 for r in racks['c'] for h in r['halves'] if h['item'] and not h['item'].get('reserved'))
    n_res = sum(1 for r in racks['c'] for h in r['halves'] if h['item'] and h['item'].get('reserved'))
    return n_items, n_res

# ---- strips
def cell_a(r, col):
    sp = len(r['halves']) == 2
    bg = 'linear-gradient(180deg,%s 0 50%%,%sCC 50%% 100%%)' % (col, col) if sp else col
    return bg

def strips(ra, rb):
    UNIT = 18.0
    def abbr(b): return {'DX': 'DOUX', 'DR': 'DARI', 'HB': 'HABRA', 'SA': 'SAUDI'}[b]
    # Plan A
    ca = ''
    for r in ra['c']:
        col = BR[r['brand']][2]
        sp = len(r['halves']) == 2
        bg = ('linear-gradient(180deg,%s 0 50%%,%sCC 50%% 100%%)' % (col, col)) if sp else col
        ca += ('<div style="width:%smm;height:19mm;background:%s;color:#fff;border:.3mm solid #fff;display:flex;flex-direction:column;align-items:center;'
               'justify-content:center;font-weight:900;line-height:1.05;flex:none"><span dir="ltr" style="font-size:5mm">%d</span>'
               '<span dir="ltr" style="font-size:2.6mm">%s</span><span dir="ltr" style="font-size:2.4mm;opacity:.9">%s</span></div>'
               % (UNIT, bg, r['gno'], abbr(r['brand']), '½ + ½' if sp else '× 1'))
    # Plan B : upper half on top, lower half below; reserved = hatched
    cb = ''
    for r in rb['c']:
        col = BR[r['brand']][2]
        halves = {h['name']: h for h in r['halves']}
        def box(h, lab):
            res = h['item'].get('reserved')
            st = ('background:repeating-linear-gradient(135deg,#fff 0 1.4mm,#D9D9D9 1.4mm 2mm);color:#666;border:.3mm dashed %s' % col) if res else ('background:%s;color:#fff;border:.3mm solid #fff' % col)
            return ('<div style="flex:1;%s;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:2.7mm;line-height:1" dir="ltr">%s</div>'
                    % (st, ('FREE' if res else lab)))
        # item number inside the half
        def num(h): return '#%d' % h['no'] if not h['item'].get('reserved') else ''
        up, lo = halves['upper'], halves['lower']
        cb += ('<div style="width:%smm;height:30mm;display:flex;flex-direction:column;flex:none;border:.3mm solid #fff;background:#fff">'
               '<div style="height:6mm;background:#222;color:#fff;font-weight:900;font-size:3mm;display:flex;align-items:center;justify-content:center" dir="ltr">%d · %s</div>%s%s</div>'
               % (UNIT, r['gno'], abbr(r['brand']), box(up, '↑ ' + num(up)), box(lo, '↓ ' + num(lo))))
    return ca, cb, UNIT

def number_items(rb):
    k = 0
    for r in rb['c']:
        for h in sorted(r['halves'], key=lambda h: h['levels'][0]):
            if not h['item'].get('reserved'):
                k += 1
                h['no'] = k
            else:
                h['no'] = 0

def lvl_txt(h):
    return LETTERS[h['levels'][0] - 1] + '–' + LETTERS[h['levels'][-1] - 1]

def head(en, ar):
    return ('<div style="margin-bottom:3mm"><div dir="ltr" style="font-weight:900;font-size:5.6mm">%s</div>'
            '<div dir="rtl" style="font-weight:900;font-size:6.4mm">%s</div></div>' % (en, ar))

def compare_page(ra, rb):
    ca, cb, UNIT = strips(ra, rb)
    na, nra = stats(ra)
    nb, nrb = stats(rb)
    def kv(en, ar, a, b, hl=False):
        s = 'background:#FFF3B0;' if hl else ''
        return ('<tr style="%s"><td dir="ltr" style="font-weight:800">%s</td><td dir="rtl" style="font-weight:800">%s</td>'
                '<td style="text-align:center;font-weight:900">%s</td><td style="text-align:center;font-weight:900">%s</td></tr>' % (s, en, ar, a, b))
    shared_a = sum(1 for r in ra['c'] if len(r['halves']) == 2)
    tb = ('<table class="tb" style="border-collapse:collapse;width:100%%;font-size:3.5mm">'
          '<tr style="background:#14181F;color:#fff"><th dir="ltr">ITEM</th><th dir="rtl">البند</th><th>PLAN A · الخطة الأساسية</th><th>PLAN B · الخطة الاحتياطية</th></tr>'
          + kv('Racks', 'عدد الراكات', 15, 15) + kv('Levels per rack', 'مستويات الراك', 4, 4)
          + kv('Pallets per level (depth)', 'بالت في المستوى (بالعمق)', 5, 5)
          + kv('Pallets per rack', 'بالت في الراك', '4 × 5 = 20', '4 × 5 = 20')
          + kv('Total pallets', 'إجمالي البالتات', 300, 300)
          + kv('Item slots', 'عدد خانات الأصناف', '%d  (%d racks full + %d shared)' % (na, 15 - shared_a, shared_a), '30  (15 × 2 halves)', True)
          + kv('Items placed now', 'الأصناف المركّبة حالياً', na, nb)
          + kv('Free (reserved) halves', 'أنصاف فارغة محجوزة', '—', nrb, True)
          + kv('Pallets per item', 'بالتات الصنف', '20 (full rack) / 10 (half)', '10 (a half = 2 levels)')
          + '</table>')
    return ('<section class="pg l" id="compare"><div style="position:absolute;left:12mm;right:12mm;top:8mm">%s'
            '<div style="display:flex;gap:7mm;align-items:flex-start"><div style="flex:1.05">%s</div><div style="flex:1;font-size:3.3mm;line-height:1.35;font-weight:700">'
            '<div dir="ltr" style="margin-bottom:2mm">Use Plan B only if the carton range grows beyond the 18 items: no rack changes, no new racks — '
            'every single-item rack simply becomes two halves and its free upper half takes a new item.</div>'
            '<div dir="rtl" style="font-weight:800;font-size:3.7mm">استخدم الخطة الاحتياطية فقط إذا زادت أصناف الكراتين عن 18 صنفاً: لا تغيير في الراكات ولا راكات جديدة — '
            'كل راك بصنف واحد ينقسم نصفين ويستقبل النصف العلوي الفارغ صنفاً جديداً.</div></div></div>'
            '<div style="margin-top:4mm"><div style="display:flex;justify-content:space-between;font-weight:900;font-size:4.3mm;margin-bottom:1mm"><span dir="ltr">PLAN A — CURRENT · %d items · 3 shared racks</span><span dir="rtl">الخطة الأساسية — الحالية · %d صنفاً · 3 راكات مشتركة</span></div>'
            '<div style="display:flex;direction:ltr;width:fit-content">%s</div>'
            '<div style="display:flex;justify-content:space-between;font-weight:900;font-size:4.3mm;margin:4mm 0 1mm"><span dir="ltr">PLAN B — BACKUP · 30 slots · %d placed · %d free</span><span dir="rtl">الخطة الاحتياطية · 30 خانة · %d مركّبة · %d فارغة</span></div>'
            '<div style="display:flex;direction:ltr;width:fit-content">%s</div>'
            '<div dir="ltr" style="font-size:3mm;font-weight:700;color:#555;margin-top:1.5mm">Top box = upper half ↑ (levels C–D) · bottom box = lower half ↓ (levels A–B) · FREE = reserved for a new item · #n = item number in the table</div>'
            '<div dir="rtl" style="font-size:3.2mm;font-weight:700;color:#555">المربع العلوي = النصف العلوي ↑ (المستويان C–D) · السفلي = النصف السفلي ↓ (A–B) · FREE = محجوز لصنف جديد · #ن = رقم الصنف في الجدول</div></div>'
            '<style>.tb td,.tb th{border:.25mm solid #888;padding:.9mm 2mm}</style></div></section>'
            % (head('CARTON ZONE (A1) — PLAN A vs PLAN B', 'منطقة الكراتين (A1) — الخطة الأساسية مقابل الاحتياطية'), tb,
               na, na, ca, nb, nrb, nb, nrb, cb))

def method_page():
    paras = [
        ('كل راك كراتين = 4 مستويات (A–D) × 5 بالت بالعمق = 20 بالت؛ الإجمالي 15 راك × 20 = 300 بالت.',
         'Every carton rack = 4 levels (A–D) × 5 pallets deep = 20 pallets; total 15 racks × 20 = 300 pallets.'),
        ('في الخطة الاحتياطية ينقسم كل راك نصفين: النصف السفلي ↓ (A–B) والنصف العلوي ↑ (C–D)، لكل نصف 10 بالتات.',
         'In Plan B every rack is split in two halves: lower half ↓ (A–B) and upper half ↑ (C–D), 10 pallets each.'),
        ('الراكات والماركات والألوان كما هي (دو 7 · داري 3 · الهبرة 2 · السعودي 3)، فلا يتغير شيء على أرض المستودع.',
         'Racks, brands and colours stay exactly as they are (Doux 7 · Dari 3 · Al Habra 2 · Saudi 3), so nothing changes on the floor.'),
        ('الأصناف الحالية (18) تبقى في أماكنها؛ كل راك بصنف واحد يحتفظ بالنصف السفلي، ويصبح نصفه العلوي «محجوزاً» لصنف جديد (12 نصفاً فارغاً).',
         'The 18 current items stay where they are; every single-item rack keeps its lower half and its upper half becomes “RESERVED” for a new item (12 free halves).'),
        ('لكل نصف ملصق مستوى خاص به (حرف المستوى + السهم + اسم الصنف + نصفه)، وأوراق البالت P1–P10 لكل صنف مركّب.',
         'Each half has its own level sticker (level letter + arrow + item name + its half) and pallet papers P1–P10 for every placed item.'),
        ('عند وصول صنف جديد: اكتب اسمه على ملصقات النصف المحجوز واطبع له أوراق بالت P1–P10 (من القوالب الفارغة).',
         'When a new item arrives: write its name on the reserved half’s stickers and print P1–P10 pallet papers for it (from the blank templates).'),
    ]
    rows = ''.join('<div style="display:flex;gap:6mm;margin-bottom:5mm;align-items:flex-start">'
                   '<div dir="ltr" style="flex:1;font-size:4.2mm;line-height:1.35;font-weight:600">%d. %s</div>'
                   '<div dir="rtl" style="flex:1;font-size:4.8mm;line-height:1.4;font-weight:800">%d. %s</div></div>' % (i, esc(e), i, esc(a))
                   for i, (a, e) in enumerate(paras, 1))
    return ('<section class="pg l" id="method"><div style="position:absolute;left:16mm;right:16mm;top:12mm">%s%s</div></section>'
            % (head('PLAN B — HOW IT WORKS', 'الخطة الاحتياطية — طريقة العمل'), rows))

def table_page(rb):
    rows = ''
    for r in rb['c']:
        be, bar, col = BR[r['brand']]
        for k, h in enumerate(sorted(r['halves'], key=lambda h: -h['levels'][0])):
            it = h['item']
            res = it.get('reserved')
            nm_ar = esc(it['ar']) + (' <bdi dir="ltr">%s</bdi>' % esc(it['size']) if it['size'] else '')
            st = ('background:repeating-linear-gradient(135deg,#fff 0 1.6mm,#E6E6E6 1.6mm 2.2mm);color:#666' if res else '')
            rows += ('<tr style="%s">%s<td dir="ltr" style="font-weight:900;text-align:center">%s %s</td>'
                     '<td dir="ltr" style="font-weight:900;color:#fff;background:%s;text-align:center">%s · %s</td>'
                     '<td dir="ltr" style="font-weight:900;text-align:center">%s</td><td dir="ltr" style="font-weight:700">%s</td>'
                     '<td dir="rtl" style="font-weight:800">%s</td><td dir="ltr" style="text-align:center;font-weight:800">%s</td></tr>'
                     % (st, ('<td rowspan="2" dir="ltr" style="font-weight:900;text-align:center">%d</td>' % r['gno']) if k == 0 else '',
                        lvl_txt(h), '↑' if h['name'] == 'upper' else '↓', col, be, bar,
                        '—' if res else '#%d' % h['no'], esc(it['en'].strip()), nm_ar, '—' if res else 'P1–P10'))
    hd = ('<tr style="background:#14181F;color:#fff"><th>RACK<br>راك</th><th dir="ltr">LEVELS · المستويات</th><th dir="ltr">BRAND · الماركة</th><th>ITEM #<br>رقم</th>'
          '<th dir="ltr">ITEM (EN)</th><th dir="rtl">الصنف (عربي)</th><th>PALLETS<br>البالتات</th></tr>')
    return ('<section class="pg l" id="tbl"><div style="position:absolute;left:12mm;right:12mm;top:7mm">%s'
            '<table class="tb" style="border-collapse:collapse;width:100%%;font-size:2.75mm;line-height:1.1">%s%s</table>'
            '<style>.tb td,.tb th{border:.25mm solid #888;padding:.25mm 1.4mm}.tb th{font-size:2.5mm}</style></div></section>'
            % (head('PLAN B — 30 SLOTS · CARTON RACKS A1', 'الخطة الاحتياطية — 30 خانة · راكات الكراتين A1'), hd, rows))

def sticker_pages(rb):
    pages = m.level_a4_pages(rb)
    return [x.replace('<section class="pg"', '<section class="pg p"', 1).replace('RACK-LEVEL STICKERS', 'PLAN B · RACK-LEVEL STICKERS', 1) for x in pages]

_ORIG = z.build_racks

def plan_a():
    return {k: (v if k == 'c' else []) for k, v in _ORIG().items()}

def plan_b():
    racks = _ORIG()
    for r in racks['c']:
        if len(r['halves']) == 1:           # single-item rack -> lower half keeps the item, upper half reserved
            it = r['halves'][0]['item']
            r['halves'] = [dict(name='lower', levels=[1, 2], item=it), dict(name='upper', levels=[3, 4], item=dict(RES))]
    out = {k: (v if k == 'c' else []) for k, v in racks.items()}
    number_items(out)
    return out

def build(out):
    os.makedirs(out, exist_ok=True)
    ra, rb = plan_a(), plan_b()
    z.build_racks = plan_b                  # numbered_sheets() reads this
    z.TYPES = {'c': TYPES['c']}
    npages, meta = z.numbered_sheets()
    stk = sticker_pages(rb)
    stk[0] = stk[0].replace('<section class="pg p"', '<section id="stickers" class="pg p"', 1)
    nav = ('<div class="nav"><b>AL-MUNAJEM · CARTONS · PLAN B (BACKUP) · الخطة الاحتياطية للكراتين · %s</b><a href="#compare">Plan A vs B · المقارنة</a>'
           '<a href="#method">How · الطريقة</a><a href="#tbl">30 slots · الجدول</a><a href="#stickers">Rack labels · ليبل الراك</a>'
           '<a href="#%s">Pallet labels P1–P10 · أوراق البالت</a></div>' % (VER, npages[0].split('id="')[1].split('"')[0]))
    body = nav + compare_page(ra, rb) + method_page() + table_page(rb) + ''.join(stk) + ''.join(npages)
    doc = ('<!-- VERSION: %s | %s -->\n<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><title>Al-Munajem Cartons Plan B %s</title>'
           '<style>%s</style></head><body>%s%s</body></html>' % (VER, DATE, VER, z.css(), body, m.FIT_JS))
    base = 'almunajem_PLAN_B_cartons_halves_%s_%s' % (VER, DATE)
    open(os.path.join(out, base + '.html'), 'w', encoding='utf-8').write(doc)
    # separate files: stickers + numbered pallet papers
    open(os.path.join(out, 'almunajem_PLAN_B_rack_level_stickers_%s_A4_%s.html' % (VER, DATE)), 'w', encoding='utf-8').write(
        '<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><style>%s</style></head><body>%s%s</body></html>' % (z.css(), ''.join(stk), m.FIT_JS))
    open(os.path.join(out, 'almunajem_PLAN_B_pallet_labels_numbered_%s_%s.html' % (VER, DATE)), 'w', encoding='utf-8').write(
        '<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (z.css(), ''.join(npages)))
    json.dump(meta, open(os.path.join(out, 'planb_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(stk), 'sticker pages;', len(npages), 'pallet sheets;', stats(rb))

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '.')
