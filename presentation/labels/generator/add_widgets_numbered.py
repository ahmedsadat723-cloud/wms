#!/usr/bin/env python3
"""fillable fields + bookmarks for the numbered pallet-label PDF.  usage: add_widgets_numbered.py in.pdf meta.json out.pdf"""
import sys, json, pymupdf
import make_zone1_system as z
src, meta_p, dst = sys.argv[1:4]
meta = json.load(open(meta_p, encoding='utf-8'))
d = pymupdf.open(src)
assert len(d) == len(meta), (len(d), len(meta))
BN = {'DX': 'DOUX', 'DR': 'DARI', 'HB': 'ALHABRA', 'SA': 'SAUDI', 'GN': 'GENERAL', 'SP': 'SPARE'}
empty = [(k, r, False) for k, _, _, _, _, _, r in z.FIELDS if k not in ('PRODUCT', 'SIZE')] + \
        [('RECEIVING_OFFICER', z.BIG[2][1], False), ('WAREHOUSE_SUPERVISOR', z.BIG[3][1], False)]
sized = [m for m in meta]
toc, last = [], {}
for i, m in enumerate(meta):
    pg = d[i]
    todo = list(empty)
    for key, (x0, y0, x1, y1), multi in todo:
        w = pymupdf.Widget()
        w.field_name = '%s_%s%d%s_P%d_%s' % (BN[m['brand']], m['tag'], m['rack'], m['half'][0].upper(), m['n'], key)
        w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        w.rect = pymupdf.Rect(x0 * z.SC, y0 * z.SC, x1 * z.SC, y1 * z.SC)
        w.text_fontsize = 12; w.text_font = 'Helv'; w.border_width = 0; w.fill_color = None
        pg.add_widget(w)
    k1 = (m['tag'])
    if k1 not in last:
        toc.append([1, '%s %s · %s' % (m['tag'], m['en'], m['name_ar']), i + 1]); last[k1] = 1
    k2 = (m['tag'], m['brand'], m['rack'], m['half'])
    if k2 not in last:
        sfx = '' if m['half'] == 'full' else (' ↓ lower' if m['half'] == 'lower' else ' ↑ upper')
        toc.append([2, '%s · rack %d%s · %s' % (BN[m['brand']], m['rack'], sfx, m['item'][:48]), i + 1]); last[k2] = 1
d.set_toc(toc)
d.save(dst, garbage=3, deflate=True)
print('pages', len(d), 'widgets', sum(len(list(p.widgets())) for p in d), 'bookmarks', len(toc))
