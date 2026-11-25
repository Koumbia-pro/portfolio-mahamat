/* =========================================================
   DASHBOARD — interactions
   ========================================================= */
(() => {
  "use strict";

  const root = document.documentElement;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ─────────── Thème (partagé avec le site) ─────────── */
  const themeBtn = $("#themeToggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }

  /* ─────────── Menu mobile ─────────── */
  const sidebar = $("#sidebar"), scrim = $("#scrim"), menuBtn = $("#menuToggle");
  const setMenu = (open) => {
    if (!sidebar) return;
    sidebar.classList.toggle("open", open);
    if (scrim) scrim.classList.toggle("on", open);
    if (menuBtn) menuBtn.setAttribute("aria-expanded", String(open));
  };
  if (menuBtn) menuBtn.addEventListener("click", () => setMenu(!sidebar.classList.contains("open")));
  if (scrim) scrim.addEventListener("click", () => setMenu(false));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });

  /* ─────────── Notifications ─────────── */
  const closeToast = (t) => { t.classList.add("out"); setTimeout(() => t.remove(), 400); };
  $$(".toast").forEach((t, i) => {
    const btn = t.querySelector("button");
    if (btn) btn.addEventListener("click", () => closeToast(t));
    setTimeout(() => t.isConnected && closeToast(t), 4500 + i * 400);
  });

  /* ─────────── Confirmation avant suppression ─────────── */
  const dialog = $("#confirmDialog");
  let pending = null;
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-confirm]");
    if (!btn || !dialog || typeof dialog.showModal !== "function") return;
    e.preventDefault();
    pending = btn;
    $("#confirmText").textContent = btn.dataset.confirm;
    dialog.showModal();
  });
  if (dialog) {
    $("#confirmCancel").addEventListener("click", () => { pending = null; dialog.close(); });
    $("#confirmOk").addEventListener("click", () => {
      const btn = pending;
      dialog.close();
      if (!btn || !btn.form) return;
      allowLeave = true;
      if (btn.form.requestSubmit) btn.form.requestSubmit(btn);
      else btn.form.submit();
    });
  }

  /* ─────────── Champs : niveau, icône, image, interrupteur ─────────── */
  $$("input[data-range]").forEach((input) => {
    const out = input.parentElement.querySelector(".range-value");
    const sync = () => { if (out) out.textContent = input.value + "%"; };
    input.addEventListener("input", sync);
    sync();
  });

  $$("input[data-icon-input]").forEach((input) => {
    const icon = input.parentElement.querySelector(".icon-preview i");
    input.addEventListener("input", () => {
      if (icon) icon.className = input.value.trim() || "fa-solid fa-code";
    });
  });

  $$('.upload input[type="file"]').forEach((input) => {
    const preview = $(`[data-preview-for="${input.id}"]`);
    input.addEventListener("change", () => {
      const file = input.files && input.files[0];
      if (!file || !preview || !file.type.startsWith("image/")) return;
      const img = document.createElement("img");
      img.alt = "";
      img.src = URL.createObjectURL(file);
      preview.replaceChildren(img);
    });
  });

  $$(".switch-input").forEach((input) => {
    const label = input.parentElement.querySelector(".switch-track + span");
    input.addEventListener("change", () => { if (label) label.textContent = input.checked ? "Oui" : "Non"; });
  });

  /* ─────────── Avertir si on quitte sans enregistrer ─────────── */
  let dirty = false, allowLeave = false;
  $$("form[data-unsaved]").forEach((form) => {
    form.addEventListener("input", () => { dirty = true; });
    form.addEventListener("change", () => { dirty = true; });
    form.addEventListener("submit", () => { allowLeave = true; });
  });
  window.addEventListener("beforeunload", (e) => {
    if (dirty && !allowLeave) { e.preventDefault(); e.returnValue = ""; }
  });

  /* ─────────── Compteurs animés ─────────── */
  if (!reduceMotion) {
    $$("[data-count]").forEach((el) => {
      const target = parseInt(el.dataset.count, 10);
      if (!target) return;
      const start = performance.now();
      const tick = (now) => {
        const t = Math.min(1, (now - start) / 1100);
        el.textContent = Math.round(target * (1 - Math.pow(1 - t, 4)));
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }

  /* ─────────── Mot de passe visible ─────────── */
  const pwBtn = $("#pwToggle");
  if (pwBtn) {
    const pw = pwBtn.parentElement.querySelector("input");
    pwBtn.addEventListener("click", () => {
      const show = pw.type === "password";
      pw.type = show ? "text" : "password";
      pwBtn.setAttribute("aria-label", show ? "Masquer le mot de passe" : "Afficher le mot de passe");
      pwBtn.innerHTML = show ? '<i class="fa-regular fa-eye-slash"></i>' : '<i class="fa-regular fa-eye"></i>';
    });
  }

  /* ─────────── Réseau de neurones (page de connexion) ─────────── */
  // Version légère : peu de points, liens tracés par lots, 30 images/s,
  // pause quand l'onglet est caché.
  const canvas = $("#loginCanvas");
  if (canvas && !reduceMotion) {
    const ctx = canvas.getContext("2d");
    const LINK = 130, LINK2 = LINK * LINK, LEVELS = 3;
    const colors = ["124,92,255", "34,211,238"];
    let w, h, nodes = [], running = false, last = 0;
    const mouse = { x: -999, y: -999 };
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.min(55, Math.round((w * h) / 20000));
      nodes = Array.from({ length: n }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.5, vy: (Math.random() - 0.5) * 0.5,
        c: Math.random() < 0.5 ? 0 : 1,
      }));
    };
    let resizeTimer;
    window.addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(resize, 150); }, { passive: true });
    window.addEventListener("pointermove", (e) => { mouse.x = e.clientX; mouse.y = e.clientY; }, { passive: true });
    resize();
    const buckets = [0, 1].map(() => Array.from({ length: LEVELS }, () => []));
    const frame = () => {
      ctx.clearRect(0, 0, w, h);
      for (const c of buckets) for (const b of c) b.length = 0;
      for (const n of nodes) {
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > w) n.vx *= -1;
        if (n.y < 0 || n.y > h) n.vy *= -1;
      }
      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy;
          if (d2 < LINK2) buckets[a.c][Math.min(LEVELS - 1, ((1 - d2 / LINK2) * LEVELS) | 0)].push(a.x, a.y, b.x, b.y);
        }
      }
      for (let c = 0; c < 2; c++) {
        for (let l = 0; l < LEVELS; l++) {
          const seg = buckets[c][l];
          if (!seg.length) continue;
          ctx.strokeStyle = `rgba(${colors[c]},${((l + 1) / LEVELS) * 0.3})`;
          ctx.beginPath();
          for (let s = 0; s < seg.length; s += 4) { ctx.moveTo(seg[s], seg[s + 1]); ctx.lineTo(seg[s + 2], seg[s + 3]); }
          ctx.stroke();
        }
      }
      ctx.strokeStyle = "rgba(34,211,238,.35)";
      ctx.beginPath();
      for (const n of nodes) {
        const dx = n.x - mouse.x, dy = n.y - mouse.y;
        if (dx * dx + dy * dy < 32400) { ctx.moveTo(n.x, n.y); ctx.lineTo(mouse.x, mouse.y); }
      }
      ctx.stroke();
      for (let c = 0; c < 2; c++) {
        ctx.fillStyle = `rgba(${colors[c]},.8)`;
        ctx.beginPath();
        for (const n of nodes) if (n.c === c) { ctx.moveTo(n.x + 1.8, n.y); ctx.arc(n.x, n.y, 1.8, 0, Math.PI * 2); }
        ctx.fill();
      }
    };
    const loop = (t) => {
      if (!running) return;
      requestAnimationFrame(loop);
      if (t - last < 31) return;
      last = t;
      frame();
    };
    const start = () => { if (!running && !document.hidden) { running = true; requestAnimationFrame(loop); } };
    document.addEventListener("visibilitychange", () => { if (document.hidden) running = false; else start(); });
    start();
  }
})();
