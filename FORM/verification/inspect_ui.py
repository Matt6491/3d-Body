
from playwright.sync_api import sync_playwright
from pathlib import Path
html=Path("/mnt/data/FORM/verification/ui-preview.html").read_text()
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path="/usr/bin/chromium",headless=False,args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":1440,"height":900})
    page.set_content(html,wait_until="load")
    print("desktop",page.evaluate("() => ({w:document.documentElement.scrollWidth,h:document.documentElement.scrollHeight,vw:innerWidth,vh:innerHeight,panels:document.querySelectorAll('.panel').length})"))
    page.screenshot(path="/mnt/data/FORM/verification/desktop.png",full_page=True)
    page.set_viewport_size({"width":390,"height":844}); page.set_content(html,wait_until="load")
    print("mobile",page.evaluate("() => ({w:document.documentElement.scrollWidth,h:document.documentElement.scrollHeight,vw:innerWidth,vh:innerHeight,rightDisplay:getComputedStyle(document.querySelector('.panel.right')).display})"))
    page.screenshot(path="/mnt/data/FORM/verification/mobile.png",full_page=True)
    browser.close()
