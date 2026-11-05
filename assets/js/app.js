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

  function closeSheet() {
    if (!sheet) return;
    sheet.classList.remove("open");
    document.body.classList.remove("no-scroll");
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
      sheet.classList.add("open");
      document.body.classList.add("no-scroll");
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
})();
