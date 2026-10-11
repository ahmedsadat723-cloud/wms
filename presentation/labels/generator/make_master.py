#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Al-Munajem DRY SECTION — ONE MASTER FILE: main plan + Plan B + every label / pallet paper / load plate / side sign.
Every page gets a square PRINT button, a SHARE button and its print dimensions (screen only; hidden when printing).
usage: python3 make_master.py <out_dir>"""
import os, re, sys, json, html
import make_stickers as m
import make_zone1_system as z
import make_plan_b as pb
import make_big_labels as bl
from make_zone1_system import esc, TYPES, BR

VER, DATE = 'v2', '2026-10-11'
HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = os.path.dirname(HERE)
SECT = re.compile(r'<section.*?</section>', re.S)

def sections(s):
    return SECT.findall(s)

def sec_id(h):
    mm = re.match(r'<section[^>]*?\sid="([^"]+)"', h)
    return mm.group(1) if mm else None

def prefix_id(h, pfx):
    return re.sub(r'^(<section[^>]*?\sid=")', r'\1' + pfx, h, count=1)

def ext_pages(fname):
    s = open(os.path.join(LABELS, fname), encoding='utf-8').read()
    body = s[s.index('<body>') + 6:]
    body = body[:body.index('<script>')] if '<script>' in body else body
    parts = body.split('<div class="pg"')[1:]
    out = []
    for p in parts:
        p = p.rstrip()
        if p.endswith('</body>'):
            p = p[:-7].rstrip()
        wm = re.search(r'style="width:(\d+)mm;height:(\d+)mm', p)
        w, h = int(wm.group(1)), int(wm.group(2))
        out.append('<div class="pg %s"' % ('l' if w > h else 'p') + p)
    return out

# ---------------------------------------------------------------- print specs (bilingual)
SPEC = {
    'info': dict(orient=('Landscape', 'أفقي'), mm='297 × 210', note=('Plan / reference page', 'صفحة خطة / مرجع'), fmt='l'),
    'stk': dict(orient=('Portrait', 'عمودي'), mm='210 × 297', note=('10 stickers · 78 × 50 mm each (2 × 5) · cut on the pink marks', '10 ملصقات · 78 × 50 مم للملصق (2 × 5) · قص على العلامات الوردية'), fmt='p'),
    'pal': dict(orient=('Portrait', 'عمودي'), mm='210 × 297', note=('One pallet paper · full page', 'ورقة بالت واحدة · صفحة كاملة'), fmt='p'),
    'load': dict(orient=('Landscape', 'أفقي'), mm='297 × 210', note=('Rack load plate · full page', 'لوحة حمولة الراك · صفحة كاملة'), fmt='l'),
    'big': dict(orient=('Landscape', 'أفقي'), mm='297 × 210', note=('ONE big yellow label · 277 × 178 mm · stick on the rack beam', 'ليبل أصفر كبير واحد · 277 × 178 مم · يُلصق على عارضة الراك'), fmt='l'),
    'side': dict(orient=('Portrait', 'عمودي'), mm='210 × 297', note=('Rack side sign · full page', 'لوحة جانب الراك · صفحة كاملة'), fmt='p'),
}
COMMON = ('A4 · Scale 100 % · Margins: None · Background graphics: ON · Single-sided', 'A4 · القياس 100% · الهوامش: بدون · الخلفيات: تشغيل · وجه واحد')

def toolbar(pid, n, total, name_en, name_ar, kind, pn):
    sp = SPEC[kind]
    w = '297mm' if sp['fmt'] == 'l' else '210mm'
    return ('<div class="tbar" style="width:%s"><div class="tinfo"><div class="t1"><b>%d / %d</b> · <span dir="ltr">%s</span> · <span dir="rtl">%s</span></div>'
            '<div class="t2" dir="ltr">%s · %s mm · %s</div><div class="t2" dir="rtl">%s · %s مم · %s</div><div class="t3" dir="ltr">%s</div><div class="t3" dir="rtl">%s</div></div>'
            '<button class="sq" onclick="PR(\'%s\')" title="Print this page · طباعة هذه الورقة"><i>🖨</i><span>PRINT<br>طباعة</span></button>'
            '<button class="sq" onclick="SH(\'%s\',\'%s\')" title="Share · مشاركة"><i>↗</i><span>SHARE<br>مشاركة</span></button></div>'
            % (w, n, total, esc(name_en), esc(name_ar), sp['orient'][0] + ' · A4', sp['mm'], 'scale 100%', sp['orient'][1] + ' · A4', sp['mm'], 'القياس 100%',
               esc(sp['note'][0]) + ' — ' + COMMON[0], esc(sp['note'][1]) + ' — ' + COMMON[1], pid, pid, esc(name_en + ' / ' + name_ar).replace("'", '')))

def wrap(h, pid, grp, n, total, name_en, name_ar, kind):
    return ('<div class="pgw" id="w-%s" data-g="%s">%s%s</div>' % (pid, grp, toolbar(pid, n, total, name_en, name_ar, kind, n), h))

# ---------------------------------------------------------------- assemble page list
def collect():
    P = []   # dict(h, id, grp, en, ar, kind)
    racks = z.build_racks()
    def add(h, pid, grp, en, ar, kind):
        P.append(dict(h=h, id=pid, grp=grp, en=en, ar=ar, kind=kind))
    # ---- PLAN A
    g = sections(z.guide_page(racks))
    add(g[0], 'guide', 'A0', 'A · Colour scale of the racks', 'أ · المقياس الخطي بالألوان', 'info')
    add(g[1], 'method', 'A0', 'A · Distribution method', 'أ · طريقة التوزيع', 'info')
    add(sections(z.capacity_page(racks))[0], 'capacity', 'A0', 'A · Rack capacity', 'أ · سعة الراكات', 'info')
    add(sections(z.key_page())[0], 'suppkey', 'A0', 'A · Supplies colour key', 'أ · مفتاح ألوان المستلزمات', 'info')
    for zt in TYPES:
        T = TYPES[zt]
        add(sections(z.table_page(zt, racks))[0], 'tbl-' + zt, 'A0', 'A · Distribution table ' + T['tag'] + ' ' + T['en'], 'أ · جدول توزيع ' + T['tag'] + ' ' + T['name_ar'], 'info')
    for h in z.old_sticker_pages():
        pid = sec_id(h)
        _, zt, br, no = pid.split('-')[:4]
        T = TYPES[zt]
        add(h, 'A-' + pid, 'A1', 'A · Rack labels %s · %s rack %s' % (T['tag'], BR[br][0], no), 'أ · ليبل الراك %s · %s راك %s' % (T['tag'], BR[br][1], no), 'stk')
    npages, meta = z.numbered_sheets()
    for h, mt in zip(npages, meta):
        pid = sec_id(h)
        add(h, 'A-' + pid, 'A2', 'A · Pallet P%d · %s · %s' % (mt['n'], mt['loc'], mt['item'][:40]), 'أ · ورقة بالت P%d · %s' % (mt['n'], mt['loc']), 'pal')
    for b in ('DX', 'DR', 'HB', 'SA', 'GN'):
        h = z.pallet_page(b)
        add(h, 'A-' + sec_id(h), 'A3', 'A · Blank pallet paper · ' + BR[b][0], 'أ · ورقة بالت فارغة · ' + BR[b][1], 'pal')
    for h, pid, en, ar in bl.big_pages():
        add(h, pid, 'C1', en, ar, 'big')
    # ---- PLAN B (cartons, every rack in halves)
    ra, rb = pb.plan_a(), pb.plan_b()
    z.build_racks, saved_t = pb.plan_b, z.TYPES
    z.TYPES = {'c': TYPES['c']}
    try:
        bn, bm = z.numbered_sheets()
    finally:
        z.build_racks, z.TYPES = pb._ORIG, saved_t
    for h, pid, en, ar in ((pb.compare_page(ra, rb), 'compare', 'B · Plan A vs Plan B', 'ب · الأساسية مقابل الاحتياطية'),
                           (pb.method_page(), 'method', 'B · How Plan B works', 'ب · طريقة عمل الخطة الاحتياطية'),
                           (pb.table_page(rb), 'tbl', 'B · 30 slots table', 'ب · جدول الـ30 خانة')):
        add(prefix_id(sections(h)[0], 'B-'), 'B-' + pid, 'B0', en, ar, 'info')
    for h in pb.sticker_pages(rb):
        pid = sec_id(h)
        _, zt, br, no = pid.split('-')[:4]
        add(prefix_id(h, 'B-'), 'B-' + pid, 'B1', 'B · Rack labels A1 · %s rack %s' % (BR[br][0], no), 'ب · ليبل الراك A1 · %s راك %s' % (BR[br][1], no), 'stk')
    for h, mt in zip(bn, bm):
        pid = sec_id(h)
        add(prefix_id(h, 'B-'), 'B-' + pid, 'B2', 'B · Pallet P%d · %s · %s' % (mt['n'], mt['loc'], mt['item'][:40]), 'ب · ورقة بالت P%d · %s' % (mt['n'], mt['loc']), 'pal')
    # ---- other designs
    for i, h in enumerate(ext_pages('almunajem_rack_load_plates_v2_2026-10-11.html'), 1):
        add(h, 'load-%d' % i, 'X1', 'Rack load plate %d' % i, 'لوحة حمولة الراك %d' % i, 'load')
    for i, h in enumerate(ext_pages('almunajem_rack_side_signs_v2_2026-10-11.html'), 1):
        add(h, 'side-%d' % i, 'X2', 'Rack side sign %d' % i, 'لوحة جانب الراك %d' % i, 'side')
    return P

GROUPS = [
    ('A0', 'A · Plan A — scale, method, capacity, tables', 'أ · الخطة الأساسية — المقياس والطريقة والسعة والجداول'),
    ('A1', 'A · Plan A — rack labels', 'أ · الخطة الأساسية — ليبل الراكات'),
    ('A2', 'A · Plan A — numbered pallet papers', 'أ · الخطة الأساسية — أوراق البالت المرقمة'),
    ('A3', 'A · Plan A — blank pallet papers (5 brands)', 'أ · الخطة الأساسية — أوراق البالت الفارغة (5 ماركات)'),
    ('C1', 'Big yellow rack labels A4 (cartons 4 · plastic 5 · boxes 5 · supplies 1 per item)', 'ليبل الراك الأصفر الكبير A4 (كراتين 4 · بلاستيك 5 · علب 5 · مستلزمات واحد لكل صنف)'),
    ('B0', 'B · Plan B — comparison, method, table', 'ب · الخطة الاحتياطية — المقارنة والطريقة والجدول'),
    ('B1', 'B · Plan B — rack labels (cartons)', 'ب · الخطة الاحتياطية — ليبل راكات الكراتين'),
    ('B2', 'B · Plan B — numbered pallet papers (cartons)', 'ب · الخطة الاحتياطية — أوراق بالت الكراتين المرقمة'),
    ('X1', 'Rack load plates', 'لوحات حمولة الراكات'),
    ('X2', 'Rack side signs', 'لوحات جانب الراكات'),
]
GKIND = {'A0': 'info', 'A1': 'stk', 'A2': 'pal', 'A3': 'pal', 'C1': 'big', 'B0': 'info', 'B1': 'stk', 'B2': 'pal', 'X1': 'load', 'X2': 'side'}

def index_page(P, first_ids):
    cnt = {g: sum(1 for p in P if p['grp'] == g) for g, _, _ in GROUPS}
    rows = ''
    for g, en, ar in GROUPS:
        sp = SPEC[GKIND[g]]
        rows += ('<tr><td dir="ltr" style="font-weight:800"><a href="#w-%s">%s</a></td><td dir="rtl" style="font-weight:800">%s</td><td style="text-align:center;font-weight:900">%d</td>'
                 '<td dir="ltr" style="text-align:center">A4 %s<br>%s mm</td><td dir="rtl" style="text-align:center">A4 %s<br>%s مم</td>'
                 '<td dir="ltr" style="font-size:2.7mm">%s</td><td dir="rtl" style="font-size:2.9mm">%s</td></tr>'
                 % (first_ids[g], esc(en), esc(ar), cnt[g], sp['orient'][0], sp['mm'], sp['orient'][1], sp['mm'], esc(sp['note'][0]), esc(sp['note'][1])))
    th = ('<tr style="background:#14181F;color:#fff"><th dir="ltr">SECTION</th><th dir="rtl">القسم</th><th>PAGES<br>الصفحات</th><th colspan="2">PAPER · الورق</th><th dir="ltr">NOTES</th><th dir="rtl">ملاحظات</th></tr>')
    return ('<section class="pg l" id="index"><div style="position:absolute;left:12mm;right:12mm;top:9mm">'
            '<div style="margin-bottom:3mm"><div dir="ltr" style="font-weight:900;font-size:6mm">AL-MUNAJEM · DRY SECTION PART 1 — MASTER PRINT FILE</div>'
            '<div dir="rtl" style="font-weight:900;font-size:7mm">المنجم · القسم الجاف الجزء 1 — الملف الشامل للطباعة</div>'
            '<div dir="ltr" style="font-size:3.2mm;font-weight:700;color:#555">%s · every design in one file · Plan A (current) + Plan B (backup) · %d pages</div>'
            '<div dir="rtl" style="font-size:3.4mm;font-weight:700;color:#555">%s · كل التصاميم في ملف واحد · الخطة الأساسية + الاحتياطية · %d صفحة</div></div>'
            '<table class="tb" style="border-collapse:collapse;width:100%%;font-size:3.3mm">%s%s</table>'
            '<div style="display:flex;gap:8mm;margin-top:4mm;font-size:3.2mm;line-height:1.4;font-weight:700">'
            '<div dir="ltr" style="flex:1"><b>HOW TO PRINT</b><br>• Square 🖨 button on every page = print that page only. Top bar = print a whole section or the whole file.<br>'
            '• In the print dialog: Paper A4 · Scale 100%% (not “fit”) · Margins None · Background graphics ON · Single-sided.<br>'
            '• The orientation (portrait / landscape) is set automatically for each page.<br>• ↗ Share = share this page’s link (or copies it).</div>'
            '<div dir="rtl" style="flex:1;font-size:3.5mm"><b>طريقة الطباعة</b><br>• زر 🖨 المربع على كل ورقة = طباعة هذه الورقة فقط. الشريط العلوي = طباعة قسم كامل أو الملف كله.<br>'
            '• في نافذة الطباعة: الورق A4 · القياس 100%% (وليس «ملاءمة») · الهوامش بدون · تفعيل رسومات الخلفية · وجه واحد.<br>'
            '• اتجاه الورقة (عمودي / أفقي) يتحدد تلقائياً لكل صفحة.<br>• زر ↗ مشاركة = مشاركة رابط هذه الصفحة (أو نسخه).</div></div>'
            '<style>.tb td,.tb th{border:.25mm solid #888;padding:1.2mm 2mm}.tb a{color:#111}</style></div></section>'
            % (VER, len(P) + 1, VER, len(P) + 1, th, rows))

CSS_X = """
.pgw{display:block}
.pgw>.pg.pg{break-after:page;page-break-after:always}
.tbar{margin:14px auto 0;background:#14181F;color:#fff;border-radius:8px 8px 0 0;display:flex;gap:8px;align-items:stretch;padding:6px 8px;box-sizing:border-box;font-family:'Cairo',sans-serif}
.tinfo{flex:1;min-width:0;line-height:1.25}.t1{font-size:13px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.t2{font-size:11px;font-weight:800;color:#FFD400}.t3{font-size:10px;font-weight:600;color:#c8ccd4}
.sq{width:64px;height:64px;flex:none;border:2px solid #FFD400;background:#FFD400;color:#111;border-radius:6px;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:inherit;padding:0}
.sq i{font-style:normal;font-size:22px;line-height:1}.sq span{font-size:9px;font-weight:900;line-height:1.1;margin-top:2px}
.sq:hover{background:#fff}.tbar .sq{order:-1}
.pgw>.pg.pg{margin-top:0}
.topbtn{background:#FFD400;color:#111;border:0;border-radius:6px;font-weight:900;font-family:inherit;padding:4px 10px;cursor:pointer;font-size:12px}
.nav select{font-family:inherit;font-weight:700;font-size:12px;padding:3px;border-radius:5px;max-width:300px}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:#14181F;color:#FFD400;padding:10px 18px;border-radius:8px;font-weight:800;z-index:99;display:none}
@media print{
 .nav,.tbar,.toast{display:none!important}
 body.one .pgw:not(.tgt){display:none!important}
 .pgw.lastt>.pg.pg{break-after:auto!important;page-break-after:auto!important}
}
"""

JS = """<script>
function PR(id){var w=document.getElementById('w-'+id);if(!w)return;go([w]);}
function PG(g){var l=[].slice.call(document.querySelectorAll(g==='ALL'?'.pgw':'.pgw[data-g="'+g+'"]'));if(l.length>40&&!confirm(l.length+' pages — print? · '+l.length+' صفحة — طباعة؟'))return;go(l);}
function go(l){document.body.classList.add('one');l.forEach(function(w){w.classList.add('tgt')});l[l.length-1].classList.add('lastt');
 var done=function(){document.body.classList.remove('one');document.querySelectorAll('.tgt,.lastt').forEach(function(w){w.classList.remove('tgt','lastt')});window.removeEventListener('afterprint',done)};
 window.addEventListener('afterprint',done);setTimeout(function(){window.print()},60);}
function toast(t){var e=document.getElementById('toast');e.textContent=t;e.style.display='block';setTimeout(function(){e.style.display='none'},2400)}
function SH(id,title){var base=(location.protocol==='file:'&&window.SHARE_BASE)?window.SHARE_BASE:location.href.split('#')[0];var url=base+'#w-'+id;
 if(navigator.share){navigator.share({title:title,text:'Al-Munajem · '+title,url:url}).catch(function(){})}
 else if(navigator.clipboard){navigator.clipboard.writeText(title+' '+url).then(function(){toast('Link copied · تم نسخ الرابط')},function(){prompt('Copy · انسخ',url)})}
 else{prompt('Copy · انسخ',url)}}
</script>"""

def build(out):
    os.makedirs(out, exist_ok=True)
    P = collect()
    total = len(P) + 1
    first = {}
    for p in P:
        first.setdefault(p['grp'], p['id'])
    parts = [wrap(index_page(P, first), 'index', 'IDX', 1, total, 'Index & print specifications', 'الفهرس ومواصفات الطباعة', 'info')]
    for i, p in enumerate(P, 2):
        parts.append(wrap(p['h'], p['id'], p['grp'], i, total, p['en'], p['ar'], p['kind']))
    opts = '<option value="ALL">🖨 ALL · الملف كله (%d)</option>' % total + ''.join(
        '<option value="%s">%s · %s</option>' % (g, esc(en), esc(ar)) for g, en, ar in GROUPS)
    links = ''.join('<a href="#w-%s">%s</a>' % (first[g], esc(t)) for g, t in (
        ('A0', 'Plan A · الأساسية'), ('A1', 'Rack labels · ليبل الراك'), ('A2', 'Pallet papers · أوراق البالت'), ('C1', 'Big labels · الليبل الكبير'), ('B0', 'Plan B · الاحتياطية'),
        ('X1', 'Load plates · الحمولة'), ('X2', 'Side signs · جانب الراك')))
    nav = ('<div class="nav"><b>AL-MUNAJEM · DRY PART 1 · MASTER %s</b><a href="#w-index">Index · الفهرس</a>%s'
           '<select id="gsel">%s</select><button class="topbtn" onclick="PG(document.getElementById(\'gsel\').value)">🖨 Print · طباعة</button></div>' % (VER, links, opts))
    doc = ('<!-- VERSION: %s | %s -->\n<!doctype html><html lang="ar" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>Al-Munajem Dry Part 1 — Master %s</title><style>%s%s</style></head><body>%s%s<div class="toast" id="toast"></div>%s%s</body></html>'
           % (VER, DATE, VER, z.css(), CSS_X, nav, ''.join(parts), JS, m.FIT_JS))
    name = 'almunajem_DRY_PART1_MASTER_print_%s_%s' % (VER, DATE)
    open(os.path.join(out, name + '.html'), 'w', encoding='utf-8').write(doc)
    json.dump([dict(id=p['id'], grp=p['grp'], en=p['en'], ar=p['ar']) for p in P], open(os.path.join(out, 'master_pages.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(name, total, 'pages')

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '.')
