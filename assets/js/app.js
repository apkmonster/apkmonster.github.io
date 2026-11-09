(function () {
  const q = document.getElementById("q");
  const cards = Array.from(document.querySelectorAll(".app"));
  const empty = document.querySelector(".empty");
  const chips = Array.from(document.querySelectorAll(".chip"));
  const hasCatalog = cards.length > 0;
  let cat = "all";

  function apply() {
    const term = (q && q.value || "").trim().toLowerCase();
    let shown = 0;
    cards.forEach((card) => {
      const okCat = cat === "all" || card.dataset.cat === cat;
      const okText = !term || (card.dataset.name || "").includes(term);
      const on = okCat && okText;
      card.style.display = on ? "" : "none";
      if (on) shown += 1;
    });
    if (empty) empty.classList.toggle("show", shown === 0);
  }

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      cat = chip.dataset.cat || "all";
      chips.forEach((c) => c.classList.toggle("on", c === chip));
      apply();
    });
  });
  if (q) q.addEventListener("input", apply);

  // On pages without a catalog, the header search sends the query to the home page.
  if (q) {
    q.addEventListener("keydown", (e) => {
      if (e.key !== "Enter" || hasCatalog) return;
      const term = q.value.trim();
      window.location.href = "index.html" + (term ? "?q=" + encodeURIComponent(term) : "#catalog");
    });
  }

  // Restore a query passed from another page.
  if (q && hasCatalog) {
    const term = new URLSearchParams(window.location.search).get("q");
    if (term) {
      q.value = term;
      apply();
    }
  }

  const navSearch = document.getElementById("nav-search");
  if (navSearch && q) {
    navSearch.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
      q.focus();
    });
  }

  const sheet = document.getElementById("sheet");
  const sheetTitle = document.getElementById("sheet-title");
  const sheetGo = document.getElementById("sheet-go");
  const sheetMissing = document.getElementById("sheet-missing");
  let sheetAdsMounted = false;

  // Ad code in the modal lives in <template> elements. Activate it only when
  // the sheet opens, one unit at a time, so hidden impressions are not counted
  // and the global atOptions of each Adsterra unit is not overwritten.
  function mountOne(tpl, box, done) {
    if (!tpl || !box) { done(); return; }
    const scripts = Array.from(tpl.content.querySelectorAll("script"));
    let i = 0;
    function next() {
      if (i >= scripts.length) { done(); return; }
      const old = scripts[i++];
      const s = document.createElement("script");
      Array.from(old.attributes).forEach((a) => s.setAttribute(a.name, a.value));
      if (old.src) {
        s.onload = next;
        s.onerror = next;
        s.src = old.src;
        box.appendChild(s);
      } else {
        s.textContent = old.textContent;
        box.appendChild(s);
        next();
      }
    }
    next();
  }

  function mountSheetAds() {
    if (sheetAdsMounted) return;
    sheetAdsMounted = true;
    const box250 = document.getElementById("sheet-ad-250");
    const box50 = document.getElementById("sheet-ad-50");
    mountOne(document.getElementById("sheet-ad-250-tpl"), box250, () => {
      mountOne(document.getElementById("sheet-ad-50-tpl"), box50, () => {});
    });
  }

  // Floating ad units (PropellerAds In-Page Push and similar) are injected as
  // fixed, max-z-index elements and can cover the top of the download sheet,
  // hiding the "Continue to download" button. Hide them while the sheet is open.
  const hiddenWhileOpen = [];
  let adWatcher = null;

  function floatingAdUnits() {
    const roots = [document.documentElement, document.body];
    const found = [];
    roots.forEach((root) => {
      Array.from(root.children).forEach((node) => {
        if (node === sheet || node.tagName === "HEAD" || node.contains(sheet)) return;
        if (node.tagName !== "IFRAME" && node.tagName !== "DIV") return;
        const cs = getComputedStyle(node);
        if (cs.position !== "fixed") return;
        const z = parseInt(cs.zIndex, 10);
        if (!(z > 1000)) return;
        found.push(node);
      });
    });
    return found;
  }

  function hideFloatingAds() {
    floatingAdUnits().forEach((node) => {
      if (node.dataset.sheetHidden) return;
      node.dataset.sheetHidden = "1";
      node.dataset.sheetDisplay = node.style.display;
      node.style.setProperty("display", "none", "important");
      hiddenWhileOpen.push(node);
    });
  }

  function restoreFloatingAds() {
    while (hiddenWhileOpen.length) {
      const node = hiddenWhileOpen.pop();
      node.style.display = node.dataset.sheetDisplay || "";
      delete node.dataset.sheetHidden;
      delete node.dataset.sheetDisplay;
    }
  }

  function watchFloatingAds() {
    if (adWatcher) return;
    adWatcher = new MutationObserver(() => {
      if (sheet.classList.contains("open")) hideFloatingAds();
    });
    adWatcher.observe(document.documentElement, { childList: true });
    adWatcher.observe(document.body, { childList: true });
  }

  function closeSheet() {
    if (!sheet) return;
    sheet.classList.remove("open");
    document.body.classList.remove("no-scroll");
    if (adWatcher) { adWatcher.disconnect(); adWatcher = null; }
    restoreFloatingAds();
  }

  document.querySelectorAll("[data-dl]").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (!sheet) return;
      if (sheetTitle) sheetTitle.textContent = btn.dataset.dl || "Download";
      const url = btn.dataset.url || "";
      if (sheetGo) {
        sheetGo.removeAttribute("hidden");
        if (url) {
          sheetGo.href = url;
        } else {
          sheetGo.href = "#";
        }
      }
      if (sheetMissing) sheetMissing.removeAttribute("hidden");
      mountSheetAds();
      sheet.classList.add("open");
      document.body.classList.add("no-scroll");
      hideFloatingAds();
      watchFloatingAds();
    });
  });

  document.querySelectorAll("[data-close]").forEach((btn) => {
    btn.addEventListener("click", closeSheet);
  });
  if (sheet) {
    sheet.addEventListener("click", (e) => {
      if (e.target === sheet) closeSheet();
    });
  }
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeSheet();
  });

  // The PropellerAds OnClick tag leaves a transparent, full-screen iframe on
  // top of the page and keeps re-adding it. It swallows every click, so links
  // and buttons stop working. Remove it once it has stayed invisible for a few
  // seconds, then keep removing it on sight. Visible ads are left alone; the
  // popunder still fires from the tag's own click listener.
  (function dropClickTraps() {
    const MIN_AGE = 3500;
    const seen = new WeakMap();
    let trapMode = false;

    function isFullScreen(el) {
      const r = el.getBoundingClientRect();
      return r.width >= window.innerWidth * 0.8 && r.height >= window.innerHeight * 0.8;
    }

    function sweep() {
      const now = Date.now();
      [document.documentElement, document.body].forEach((root) => {
        if (!root) return;
        Array.from(root.children).forEach((el) => {
          if (el.tagName !== "IFRAME" || !el.isConnected) return;
          if (!seen.has(el)) seen.set(el, now);
          if (!isFullScreen(el)) return;
          if (parseFloat(getComputedStyle(el).opacity) > 0.05) return;
          if (trapMode || now - seen.get(el) >= MIN_AGE) {
            trapMode = true;
            el.remove();
          }
        });
      });
    }

    setInterval(sweep, 1000);
    new MutationObserver(sweep).observe(document.documentElement, { childList: true });
    new MutationObserver(sweep).observe(document.body, { childList: true });
  })();
})();
