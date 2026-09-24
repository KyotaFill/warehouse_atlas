(async function runEcountCrawler() {
  console.log("=== STARTING AUTOMATED ECOUNT ERP MULTI-AGENT CRAWLER ===");

  async function sendSnapshot(category, name, html) {
    try {
      await fetch("http://127.0.0.1:28080/api/save_snapshot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category, name, html }),
      });
      console.log(`[SAVED] ${category} -> ${name}`);
    } catch (e) {
      console.error(`[SAVE ERROR] ${name}:`, e);
    }
  }

  // 1. CRAWL GROUP A: FLOWCHART POPUPS (Sơ đồ quy trình như ảnh #6)
  const flowchartIds = [
    "customer",
    "item",
    "store",
    "surtax",
    "registration",
    "estimate",
    "order",
    "sale",
    "collect",
    "joborder",
    "dispatch",
    "production",
    "purchaseorder",
    "buy",
    "pay",
    "invenreport",
    "acctreport",
  ];

  console.log(`--- Crawling ${flowchartIds.length} Flowchart Popups ---`);
  for (const id of flowchartIds) {
    const el = document.getElementById(id);
    if (!el) continue;
    try {
      el.click();
      await new Promise((r) => setTimeout(r, 600));

      // Tìm popup/popover xuất hiện
      const popups = Array.from(
        document.querySelectorAll(
          ".popover, .wrapper-layer-box, .layer-box, .ui-dialog, [class*='flowchart-popup'], [class*='popover-content']",
        ),
      );
      const visiblePopup = popups.filter((p) => p.offsetParent !== null).pop();

      if (visiblePopup) {
        await sendSnapshot(
          "flowchart_popups",
          id,
          visiblePopup.outerHTML || visiblePopup.innerHTML,
        );
        // Đóng popup
        const closeBtn = visiblePopup.querySelector(
          ".close, [data-value=close], .btn-close, .ui-dialog-titlebar-close, .ep-icon-close",
        );
        if (closeBtn) closeBtn.click();
      } else {
        // Lưu HTML của chính thẻ nếu không có popup rời
        await sendSnapshot("flowchart_popups", id, el.outerHTML);
      }
      await new Promise((r) => setTimeout(r, 300));
    } catch (err) {
      console.error(`Error on flowchart ${id}:`, err);
    }
  }

  // 2. CRAWL GROUP B: RIGHT SIDEBAR APPS & POPUPS
  const appItems = Array.from(
    document.querySelectorAll(".wrapper-apps .apps > li"),
  ).slice(0, 16);
  console.log(`--- Crawling ${appItems.length} Right Sidebar Apps ---`);

  for (const app of appItems) {
    const title = (
      app.querySelector(".apps-title")?.textContent || app.className
    ).trim();
    const safeName = title.replace(/\s+/g, "_") || app.className;
    try {
      app.click();
      await new Promise((r) => setTimeout(r, 700));

      const dialogs = Array.from(
        document.querySelectorAll(
          ".ui-dialog, .wrapper-layer-box, .layer-box, .modal, [data-layer-box-id]",
        ),
      );
      const visibleDialog = dialogs.filter((d) => d.offsetParent !== null).pop();

      if (visibleDialog) {
        await sendSnapshot(
          "right_sidebar_apps",
          safeName,
          visibleDialog.outerHTML,
        );
        const closeBtn = visibleDialog.querySelector(
          ".close, [data-value=close], .btn-close, .ui-dialog-titlebar-close, .ep-icon-close",
        );
        if (closeBtn) closeBtn.click();
      } else {
        await sendSnapshot("right_sidebar_apps", safeName, app.outerHTML);
      }
      await new Promise((r) => setTimeout(r, 400));
    } catch (err) {
      console.error(`Error on app ${title}:`, err);
    }
  }

  // 3. CRAWL GROUP C: TOP NAVIGATION LEVEL 1 & LEVEL 2 MODULES
  const navModules = Array.from(
    document.querySelectorAll(".wrapper-global-nav > ul > li"),
  );
  console.log(`--- Crawling ${navModules.length} Navigation Modules ---`);

  for (const mod of navModules) {
    const modTitle = (
      mod.querySelector(".wrapper-depth1 a")?.textContent || "module"
    ).trim();
    const safeModName = modTitle.replace(/\s+/g, "_");
    await sendSnapshot("navigation_modules", safeModName, mod.outerHTML);
  }

  console.log("=== CRAWLER COMPLETED ALL SNAPSHOTS! ===");
  alert("Crawler đã hoàn thành tải về toàn bộ HTML & CSS của tất cả các popup và ứng dụng!");
})();
