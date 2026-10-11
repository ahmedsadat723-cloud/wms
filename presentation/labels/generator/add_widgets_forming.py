#!/usr/bin/env python3
"""fillable fields + bookmarks for the forming master PDF.  usage: add_widgets_forming.py flat.pdf forming_pages.json forming_pallet_meta.json out.pdf"""
import sys, json, pymupdf
src, pages_p, meta_p, dst = sys.argv[1:5]
P = json.load(open(pages_p, encoding='utf-8')); M = json.load(open(meta_p))
d = pymupdf.open(src); assert len(d) == len(P) + 1
MM = 72 / 25.4; LH = M['laby']; cnt = 0
for i, p in enumerate(P, 1):
    if p['grp'] != 'F3':
        continue
    pg = d[i]; rack, n = p['id'].split('-')[2], p['id'].split('-')[3]
    for key, x, y, w, h in M['fields']:
        wd = pymupdf.Widget(); wd.field_name = 'F_%s_P%s_%s' % (rack, n, key); wd.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        wd.rect = pymupdf.Rect(x * MM + 1, (y + LH - 1.4) * MM, (x + w) * MM - 1, (y + h) * MM - 1)
        wd.text_fontsize = 14; wd.text_font = 'HeBo'; wd.border_width = 0; wd.fill_color = None
        pg.add_widget(wd); cnt += 1
G = {'F0': 'التشكيل — الخطة / Forming plan', 'F1': 'ليبل راكات التشكيل / Forming rack labels', 'F2': 'ليبل الأصناف الكبير / Big item labels', 'F3': 'أوراق البالت P1–P30 / Pallet papers'}
toc = [[1, 'الفهرس / Index', 1]]; seen = set(); sub = set()
for i, p in enumerate(P, 2):
    g = p['grp']
    if g not in seen:
        toc.append([1, G[g], i]); seen.add(g)
    if g == 'F3':
        r = p['id'].split('-')[2]
        if r not in sub:
            sub.add(r); toc.append([2, 'Rack ' + r, i])
    else:
        toc.append([2, p['en'][:60], i])
d.set_toc(toc); d.save(dst, garbage=3, deflate=True)
print('pages', len(d), 'widgets', cnt)
