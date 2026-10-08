#!/usr/bin/env python3
"""Render a sticker HTML to PDF with Chromium (Playwright).  usage: render_pdf.py in.html out.pdf"""
import sys, asyncio, os
from playwright.sync_api import sync_playwright
src, dst = os.path.abspath(sys.argv[1]), sys.argv[2]
exe = os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe if os.path.exists(exe) else None, args=['--no-sandbox'])
    pg = b.new_page()
    pg.goto('file://' + src, wait_until='load', timeout=300000)
    pg.evaluate('document.fonts.ready.then(()=>{fit();return 1})')
    pg.wait_for_timeout(1500)
    pg.evaluate('fit()')
    pg.pdf(path=dst, prefer_css_page_size=True, print_background=True)
    b.close()
print('ok', dst)
