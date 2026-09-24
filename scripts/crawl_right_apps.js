(async function crawlRightApps() {
  const apps = [
    { selector: ".apps-ecount-ai", name: "AI_ho_tro_cong_viec" },
    { selector: ".apps-ecount-search", name: "Tim_kiem_tong_hop" },
    { selector: ".apps-customer-center", name: "Ho_tro_thong_minh" },
    { selector: ".apps-enote", name: "E_Note" },
    { selector: ".apps-notification", name: "Thong_bao" },
    { selector: ".apps-msg", name: "Tin_nhan" },
    { selector: ".apps-messenger", name: "Messenger" },
    { selector: ".apps-email", name: "Email" },
    { selector: ".apps-timeline", name: "Dong_thoi_gian" },
    { selector: ".apps-favourite", name: "Bookmark" },
    { selector: ".apps-userpay", name: "UserPay" },
  ];

  for (const item of apps) {
    const el = document.querySelector(item.selector);
    if (!el) continue;
    console.log(`Clicking ${item.name}...`);
    el.click();
    await new Promise(r => setTimeout(r, 1200));

    // Tìm tất cả dialog hoặc layer box
    const popups = Array.from(document.querySelectorAll(".ui-dialog, .wrapper-layer-box, .layer-box, .modal, .react-draggable"));
    const latest = popups.filter(p => p.offsetParent !== null).pop();

    if (latest) {
      console.log(`-> Found dialog for ${item.name}`);
      await fetch("http://127.0.0.1:28080/api/save_snapshot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category: "right_sidebar_apps",
          name: item.name,
          html: latest.outerHTML
        })
      });
      const closeBtn = latest.querySelector(".close, [data-value=close], .btn-close, .ui-dialog-titlebar-close, .ep-icon-close");
      if (closeBtn) closeBtn.click();
    } else {
      console.log(`-> No open dialog for ${item.name}`);
    }
    await new Promise(r => setTimeout(r, 600));
  }
  console.log("Right apps crawling done!");
})();
