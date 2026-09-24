(async function crawlPages() {
  console.log("=== CRAWLING MAIN MODULE PAGES ===");

  async function savePage(name, html) {
    await fetch("http://127.0.0.1:28080/api/save_snapshot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: "module_pages",
        name: name,
        html: html
      })
    });
    console.log(`[SAVED PAGE] ${name}`);
  }

  // 1. Click Kế toán II
  const navKt2 = document.getElementById("link_depth1_MENUTREE_000005");
  if (navKt2) {
    console.log("Clicking Kế toán II...");
    navKt2.click();
    await new Promise(r => setTimeout(r, 1500));
    await savePage("ke_toan_2_main_page", document.getElementById("app-root").outerHTML);
  }

  // 2. Click Kiểm kê I
  const navKk1 = document.getElementById("link_depth1_MENUTREE_000004");
  if (navKk1) {
    console.log("Clicking Kiểm kê I...");
    navKk1.click();
    await new Promise(r => setTimeout(r, 1500));
    await savePage("kiem_ke_1_main_page", document.getElementById("app-root").outerHTML);
  }

  // 3. Click Kiểm kê II
  const navKk2 = document.getElementById("link_depth1_MENUTREE_000783");
  if (navKk2) {
    console.log("Clicking Kiểm kê II...");
    navKk2.click();
    await new Promise(r => setTimeout(r, 1500));
    await savePage("kiem_ke_2_main_page", document.getElementById("app-root").outerHTML);
  }

  // Click back to Trang cá nhân
  const navHome = document.getElementById("link_depth1_MPGU_RT00000003");
  if (navHome) {
    navHome.click();
    await new Promise(r => setTimeout(r, 1000));
  }

  console.log("Module pages crawl completed!");
})();
