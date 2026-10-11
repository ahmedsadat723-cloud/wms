#!/usr/bin/env python3
"""add fillable form fields to the pallet-label PDF (5 brands). usage: add_widgets.py in.pdf out.pdf"""
import sys, pymupdf
import make_zone1_system as z
src, dst = sys.argv[1], sys.argv[2]
d = pymupdf.open(src)
BRS = ['DX', 'DR', 'HB', 'SA', 'GN']
names = {'DX': 'DOUX', 'DR': 'DARI', 'HB': 'ALHABRA', 'SA': 'SAUDI', 'GN': 'GENERAL'}
rects = [(k, r, False) for k, _, _, _, _, _, r in z.FIELDS] + [('PALLET_NO', z.BIG[0][1], True), ('LOCATION', z.BIG[1][1], True),
         ('RECEIVING_OFFICER', z.BIG[2][1], False), ('WAREHOUSE_SUPERVISOR', z.BIG[3][1], False)]
for i, br in enumerate(BRS):
    pg = d[i]
    for key, (x0, y0, x1, y1), multi in rects:
        w = pymupdf.Widget()
        w.field_name = '%s_%s' % (names[br], key)
        w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        w.rect = pymupdf.Rect(x0 * z.SC, y0 * z.SC, x1 * z.SC, y1 * z.SC)
        w.text_fontsize = 12
        w.text_font = 'Helv'
        w.border_width = 0
        w.fill_color = None
        w.field_flags = pymupdf.PDF_TX_FIELD_IS_MULTILINE if multi else 0
        pg.add_widget(w)
d.save(dst, garbage=3, deflate=True)
print('widgets', sum(len(list(p.widgets())) for p in d), 'pages', len(d))
