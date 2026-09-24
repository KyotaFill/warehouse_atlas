(async function crawlEverything() {
  console.log("=== STARTING EXHAUSTIVE CRAWLER ===");

  async function postSnapshot(category, name, html) {
    try {
      const res = await fetch("http://127.0.0.1:28080/api/save_snapshot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category, name, html }),
      });
      const data = await res.json();
      console.log(`[OK] Saved ${category}/${name}:`, data.status);
    } catch (e) {
      console.error(`[FAIL] ${name}:`, e);
    }
  }

  // 1. CRAWL TOÀN BỘ 17 POPUP SƠ ĐỒ QUY TRÌNH (FLOWCHART POPOVERS NHƯ ẢNH #6)
  const flowchartElements = Array.from(document.querySelectorAll("[data-type='flowchart_item']"));
  console.log(`Found ${flowchartElements.length} flowchart items.`);

  for (const item of flowchartElements) {
    const id = item.id;
    const title = item.querySelector(".label")?.textContent.trim() || id;
    console.log(`Clicking flowchart item: ${id} (${title})...`);

    // Click to open popover
    item.click();
    await new Promise(r => setTimeout(r, 600));

    // Tìm container popup có class open
    const popup = document.querySelector(`.wrapper-flowchart .panel.open, [class*='flowchart-${id}'].open, .wrapper-flowchart [class*='flowchart-'].open`);
    if (popup) {
      console.log(`-> Captured popup for ${id}:`, popup.className);
      await postSnapshot("flowchart_popups", id, popup.outerHTML);
      // Close
      const closeBtn = popup.querySelector(".close");
      if (closeBtn) closeBtn.click();
    } else {
      console.log(`-> No open popup for ${id}, capturing item itself`);
      await postSnapshot("flowchart_popups", id, item.outerHTML);
    }
    await new Promise(r => setTimeout(r, 400));
  }

  // 2. CRAWL TOÀN BỘ 15 TIỆN ÍCH THANH BÊN PHẢI (RIGHT SIDEBAR APPS)
  const rightApps = Array.from(document.querySelectorAll(".wrapper-apps .apps > li")).slice(0, 16);
  console.log(`Found ${rightApps.length} right toolbar apps.`);

  for (const app of rightApps) {
    const title = (app.querySelector(".apps-title")?.textContent || app.className).trim();
    const safeName = title.replace(/[\s\/\\]+/g, "_") || app.className;
    console.log(`Clicking right app: ${title}...`);

    app.click();
    await new Promise(r => setTimeout(r, 800));

    const popups = Array.from(document.querySelectorAll(".ui-dialog, .wrapper-layer-box, .layer-box, .modal, [data-own-layer-box-id]"));
    const visiblePopup = popups.filter(p => p.offsetParent !== null).pop();

    if (visiblePopup) {
      console.log(`-> Captured dialog for ${title}`);
      await postSnapshot("right_sidebar_apps", safeName, visiblePopup.outerHTML);
      const closeBtn = visiblePopup.querySelector(".close, [data-value=close], .btn-close, .ui-dialog-titlebar-close, .ep-icon-close");
      if (closeBtn) closeBtn.click();
    } else {
      await postSnapshot("right_sidebar_apps", safeName, app.outerHTML);
    }
    await new Promise(r => setTimeout(r, 500));
  }

  console.log("=== EXHAUSTIVE CRAWL COMPLETED 100%! ===");
  alert("Hoàn thành cào và lưu trữ toàn bộ 100% các popup sơ đồ và ứng dụng thanh bên phải!");
})();
