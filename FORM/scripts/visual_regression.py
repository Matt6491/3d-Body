
#!/usr/bin/env python3
"""Static layout regression harness for FORM's responsive shell.

This does NOT replace a real Next/R3F browser test. It exists so layout/palette/mobile
regressions can be caught even when WebGL/npm dependencies are unavailable.
Run: xvfb-run -a python scripts/visual_regression.py
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
from playwright.sync_api import sync_playwright
import re,sys

ROOT=Path(__file__).resolve().parents[1]
preview=ROOT/"verification"/"ui-preview.html"
html=preview.read_text()
css=(ROOT/"frontend"/"app"/"globals.css").read_text().replace('@import "tailwindcss";','')
a=html.index("<style>"); b=html.index("</style>",a)
custom='svg text{font-family:system-ui,sans-serif}.svgbody{filter:drop-shadow(0 20px 30px #0008)}'
html=html[:a]+"<style>"+css+custom+"</style>"+html[b+8:]

def compare(actual:Path,baseline:Path,tolerance=1.4):
    a=Image.open(actual).convert("RGB"); b=Image.open(baseline).convert("RGB")
    if a.size!=b.size: raise AssertionError(f"size changed: {a.size} vs {b.size}")
    diff=ImageChops.difference(a,b)
    rms=sum(v*v for v in ImageStat.Stat(diff).rms)**0.5/(3**0.5)
    print(actual.name,"RMS",round(rms,3))
    if rms>tolerance: raise AssertionError(f"visual difference {rms:.3f} > {tolerance}")

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path="/usr/bin/chromium",headless=False,args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":1440,"height":900}); page.set_content(html)
    d=page.evaluate("() => [document.documentElement.scrollWidth,innerWidth]")
    assert d[0]<=d[1],f"desktop horizontal overflow {d}"
    page.screenshot(path=str(ROOT/"verification"/"current-desktop.png"),full_page=True)
    page.set_viewport_size({"width":390,"height":844});page.set_content(html)
    m=page.evaluate("() => [document.documentElement.scrollWidth,innerWidth,getComputedStyle(document.querySelector('.panel.right')).display]")
    assert m[0]<=m[1],f"mobile horizontal overflow {m}"
    assert m[2]=="none"
    page.screenshot(path=str(ROOT/"verification"/"current-mobile.png"),full_page=True)
    browser.close()

compare(ROOT/"verification"/"current-desktop.png",ROOT/"verification"/"baseline-desktop.png")
compare(ROOT/"verification"/"current-mobile.png",ROOT/"verification"/"baseline-mobile.png")
print("VISUAL REGRESSION PASS")
