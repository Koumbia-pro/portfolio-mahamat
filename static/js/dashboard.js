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
  const canvas = $("#loginCanvas");
  if (canvas && !reduceMotion) {
    const ctx = canvas.getContext("2d");
    let w, h, nodes = [];
    const mouse = { x: -999, y: -999 };
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.min(90, Math.round((w * h) / 14000));
      nodes = Array.from({ length: n }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.35, vy: (Math.random() - 0.5) * 0.35,
        c: Math.random() < 0.5 ? "124,92,255" : "34,211,238",
      }));
    };
    window.addEventListener("resize", resize, { passive: true });
    window.addEventListener("pointermove", (e) => { mouse.x = e.clientX; mouse.y = e.clientY; }, { passive: true });
    resize();
    const loop = () => {
      ctx.clearRect(0, 0, w, h);
      for (const n of nodes) {
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > w) n.vx *= -1;
        if (n.y < 0 || n.y > h) n.vy *= -1;
      }
      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < 140) {
            ctx.strokeStyle = `rgba(${a.c},${(1 - d / 140) * 0.3})`;
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
          }
        }
        const dm = Math.hypot(a.x - mouse.x, a.y - mouse.y);
        if (dm < 180) {
          ctx.strokeStyle = `rgba(34,211,238,${(1 - dm / 180) * 0.5})`;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
        }
        ctx.fillStyle = `rgba(${a.c},.8)`;
        ctx.beginPath(); ctx.arc(a.x, a.y, 1.8, 0, Math.PI * 2); ctx.fill();
      }
      if (!document.hidden) requestAnimationFrame(loop);
    };
    document.addEventListener("visibilitychange", () => { if (!document.hidden) requestAnimationFrame(loop); });
    loop();
  }
})();
