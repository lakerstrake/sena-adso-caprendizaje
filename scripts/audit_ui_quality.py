# -*- coding: utf-8 -*-
import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8899/index.html"
OUT = r"C:/Users/USERPC~1/AppData/Local/Temp/claude/c--Users-USER-PC--gemini-antigravity-ide-scratch-sena-caprendizaje-output/e4b91793-dfe8-4c57-aa6a-efba368ac512/scratchpad"

report = {"console": [], "pageerrors": [], "reqfail": []}

def log(tag, msg):
    print("[" + tag + "] " + str(msg))

JS_DUPID = """() => {
    const ids = {}; const dups = [];
    document.querySelectorAll('[id]').forEach(e => { ids[e.id]=(ids[e.id]||0)+1; });
    for (const k in ids) if (ids[k]>1) dups.push(k+' x'+ids[k]);
    return dups;
}"""

JS_DUPARIA = """() => {
    const out=[];
    document.querySelectorAll('*').forEach(e=>{
       const h=e.outerHTML.split('>')[0];
       const m=h.match(/aria-label=/g);
       if(m && m.length>1) out.push(String(e.id||e.className||e.tagName).slice(0,40));
    });
    return out;
}"""

JS_NONAME = """() => {
    return [...document.querySelectorAll('button,a')].filter(b=>{
        const t=(b.innerText||'').trim();
        return !t && !b.getAttribute('aria-label') && !b.getAttribute('title');
    }).map(b=>b.tagName+'#'+String(b.id||b.className).slice(0,40));
}"""

JS_OVERFLOW = """() => {
    const de=document.documentElement;
    const bad=[];
    document.querySelectorAll('body *').forEach(e=>{
        const r=e.getBoundingClientRect();
        if(r.width>0 && (r.right > de.clientWidth+2 || r.left < -2)){
           const st=getComputedStyle(e);
           if(st.position!=='fixed' && st.overflowX!=='auto' && st.overflowX!=='scroll'){
               let anc=e.parentElement, scroll=false;
               while(anc){const s=getComputedStyle(anc);
                 if(s.overflowX==='auto'||s.overflowX==='scroll'||s.overflow==='auto'||s.overflow==='hidden'){scroll=true;break;}
                 anc=anc.parentElement;}
               if(!scroll) bad.push(e.tagName+'.'+String(e.className).slice(0,40)+' r='+Math.round(r.right));
           }
        }
    });
    return {scrollW: de.scrollWidth, clientW: de.clientWidth, bad: bad.slice(0,6)};
}"""

JS_TAP = """() => {
    const bad=[];
    document.querySelectorAll('button,a,select,input').forEach(e=>{
        const r=e.getBoundingClientRect();
        if(r.width===0||r.height===0) return;
        if(r.height<32||r.width<32) bad.push(String(e.id||e.className||e.tagName).slice(0,42)+' '+Math.round(r.width)+'x'+Math.round(r.height));
    });
    return bad;
}"""

JS_CONTRAST = """() => {
    function lum(c){
      const p=c.match(/[\\d.]+/g); if(!p) return null;
      const [r,g,b]=p.slice(0,3).map(Number).map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);});
      return 0.2126*r+0.7152*g+0.0722*b;
    }
    const out=[];
    const sels=['.candidate-pill','#lblPagination','.stack-row span','.filter-select-wrap label','.data-table td','.tier-seg-btn','.chip-btn','.table-footer'];
    sels.forEach(s=>{const e=document.querySelector(s); if(!e) return;
      const st=getComputedStyle(e); let bg=st.backgroundColor, n=e;
      while(bg==='rgba(0, 0, 0, 0)'&&n.parentElement){n=n.parentElement;bg=getComputedStyle(n).backgroundColor;}
      const l1=lum(st.color), l2=lum(bg);
      if(l1===null||l2===null) return;
      const cr=(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);
      out.push(s+' = '+cr.toFixed(2)+':1 @'+st.fontSize);
    });
    return out;
}"""

JS_FONTS = """() => {
    const c={}; document.querySelectorAll('body *').forEach(e=>{
        if(!e.innerText||!e.innerText.trim()) return;
        const fs=getComputedStyle(e).fontSize; c[fs]=(c[fs]||0)+1;});
    return Object.entries(c).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0]));
}"""

JS_PERF = """() => {
    const n=performance.getEntriesByType('navigation')[0]||{};
    const res=performance.getEntriesByType('resource').map(r=>({n:r.name.split('/').pop().slice(0,34),d:Math.round(r.duration),s:Math.round((r.transferSize||0)/1024)}));
    return {dom: Math.round(n.domContentLoadedEventEnd||0), load: Math.round(n.loadEventEnd||0),
            res: res.sort((a,b)=>b.s-a.s).slice(0,8), nres: res.length};
}"""

JS_REAL = """() => {
    const c={}; (window.RAW_DATA||[]).forEach(d=>{c[d.cat_id]=(c[d.cat_id]||0)+1;});
    return c;
}"""

with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    pg.on("console", lambda m: report["console"].append((m.type, m.text[:300])))
    pg.on("pageerror", lambda e: report["pageerrors"].append(str(e)[:400]))
    pg.on("requestfailed", lambda r: report["reqfail"].append(r.url[:120] + " :: " + str(r.failure)))

    pg.goto(URL, wait_until="networkidle")
    time.sleep(1.5)

    log("DUP-ID", pg.evaluate(JS_DUPID) or "sin IDs duplicados")
    log("DUP-ARIA", pg.evaluate(JS_DUPARIA) or "sin aria-label duplicados")
    log("H1", pg.evaluate("() => [...document.querySelectorAll('h1')].map(e=>e.textContent.trim().slice(0,50))"))
    log("BTN-NONAME", pg.evaluate(JS_NONAME) or "todos los controles nombrados")

    log("ROWS", pg.eval_on_selector_all("#tableBody tr", "e=>e.length"))
    log("COUNTS", pg.inner_text("#lblVisibleCount") + " / " + pg.inner_text("#lblTotalCount"))
    log("TIER-SEGMENTS", pg.evaluate("() => [...document.querySelectorAll('.tier-seg-btn')].map(b=>b.innerText.replace(/\\n/g,' '))"))
    log("TIER-REAL", pg.evaluate(JS_REAL))

    for w, h, label in [(360,740,"mobile-s"),(390,844,"iphone"),(414,896,"mobile-l"),(768,1024,"tablet"),
                        (1024,768,"tablet-l"),(1280,800,"laptop13"),(1366,768,"laptop14"),
                        (1440,900,"laptop15"),(1920,1080,"fhd"),(2560,1440,"qhd")]:
        pg.set_viewport_size({"width": w, "height": h})
        time.sleep(0.45)
        ov = pg.evaluate(JS_OVERFLOW)
        flag = "OVERFLOW!" if ov["scrollW"] > ov["clientW"] + 1 else "ok"
        log("VP-" + label, str(w) + "x" + str(h) + " scrollW=" + str(ov["scrollW"]) + " clientW=" + str(ov["clientW"]) + " -> " + flag + " " + str(ov["bad"]))

    pg.set_viewport_size({"width": 390, "height": 844}); time.sleep(0.6)
    small = pg.evaluate(JS_TAP)
    log("TAP-SMALL", str(len(small)) + " controles <32px :: " + str(small[:14]))

    pg.set_viewport_size({"width": 1440, "height": 900}); time.sleep(0.5)

    def click(sel, name):
        try:
            pg.click(sel, timeout=4000); time.sleep(0.5); log("CLICK-OK", name); return True
        except Exception as e:
            log("CLICK-FAIL", name + " :: " + str(e)[:110]); return False

    click("#pillStrategy", "tab Estrategia")
    log("STRATEGY-VIS", pg.is_visible("#sectionStrategy"))
    click("#pillFavs", "tab Favoritas")
    click("#pillDirectory", "tab Directorio")

    pg.fill("#mainSearch", "bogota"); time.sleep(0.8)
    log("SEARCH-bogota", pg.inner_text("#lblVisibleCount"))
    pg.fill("#mainSearch", "zzzznoexiste"); time.sleep(0.8)
    log("SEARCH-EMPTY", "filas=" + str(pg.eval_on_selector_all("#tableBody tr", "e=>e.length")) + " txt=" + repr(pg.inner_text("#tableBody")[:100]))
    pg.fill("#mainSearch", ""); time.sleep(0.7)

    click(".tier-seg-btn.seg-1", "filtro Tier 1")
    log("TIER1-COUNT", pg.inner_text("#lblVisibleCount"))
    click(".tier-seg-btn[data-tier='']", "filtro Todos")

    click("#toggleFiltersBtn", "toggle filtros avanzados")
    log("SECFILTERS-VIS", pg.is_visible("#secondaryFiltersRow"))
    try:
        pg.select_option("#filterSort", "escalabilidad_desc"); time.sleep(0.7); log("SORT-OK", "escalabilidad")
    except Exception as e:
        log("SORT-FAIL", str(e)[:110])

    click("#btnLayoutCards", "vista tarjetas")
    log("CARDS", pg.eval_on_selector_all("#cardsGridWrap > *", "e=>e.length"))
    click("#btnLayoutTable", "vista tabla")

    try:
        pg.click("#tableBody tr:nth-child(1) button:has-text('Detalle')", timeout=4000)
        time.sleep(0.9)
        log("MODAL-DETAIL", "abierto=" + str(pg.is_visible("#detailModal")) + " titulo=" + repr(pg.inner_text("#mTitle")[:40]))
        pg.keyboard.press("Escape"); time.sleep(0.5)
        log("MODAL-ESC", "cerrado=" + str(not pg.is_visible("#detailModal")))
    except Exception as e:
        log("MODAL-DETAIL-FAIL", str(e)[:150])

    t0 = pg.get_attribute("html", "data-theme")
    click("#themeBtn", "toggle tema")
    log("THEME", str(t0) + " -> " + str(pg.get_attribute("html", "data-theme")))
    time.sleep(0.4)
    log("CONTRAST-LIGHT", pg.evaluate(JS_CONTRAST))
    click("#themeBtn", "volver tema")
    time.sleep(0.4)
    log("CONTRAST-DARK", pg.evaluate(JS_CONTRAST))

    try:
        pg.click("#tableBody tr:nth-child(1) [data-action='toggleFavorite']", timeout=3000); time.sleep(0.5)
        log("FAV", pg.inner_text("#pillFavCount"))
    except Exception as e:
        log("FAV-FAIL", str(e)[:110])
    try:
        for i in (1, 2):
            pg.click("#tableBody tr:nth-child(" + str(i) + ") [data-action='toggleCompare']", timeout=3000); time.sleep(0.35)
        log("COMPARE", "dock=" + pg.inner_text("#dockCount") + " visible=" + str(pg.is_visible("#comparisonDock")))
        pg.click("[data-action='openCompareModal']"); time.sleep(0.8)
        log("COMPARE-MODAL", pg.is_visible("#compareModal"))
        pg.keyboard.press("Escape"); time.sleep(0.4)
    except Exception as e:
        log("COMPARE-FAIL", str(e)[:150])

    log("FONT-SIZES", pg.evaluate(JS_FONTS))
    log("PERF", json.dumps(pg.evaluate(JS_PERF)))

    pg.set_viewport_size({"width": 1440, "height": 900}); time.sleep(0.6)
    pg.screenshot(path=OUT + "/before_desktop.png")
    pg.set_viewport_size({"width": 390, "height": 844}); time.sleep(0.7)
    pg.screenshot(path=OUT + "/before_mobile.png")

    br.close()

print("\n===== CONSOLE =====")
for t, m in report["console"][:30]:
    print("  " + t + ": " + m)
print("\n===== PAGE ERRORS =====")
for e in report["pageerrors"][:20]:
    print("   " + e)
print("\n===== FAILED REQUESTS =====")
for r in report["reqfail"][:20]:
    print("   " + r)
