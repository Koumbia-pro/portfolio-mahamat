/* =========================================================
   PORTFOLIO — MAHAMAT HASSAN OUMAR
   Animations et interactions
   ========================================================= */
(() => {
  "use strict";

  const root = document.documentElement;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* ─────────── 1. PRÉCHARGEMENT ─────────── */
  function runPreloader(onDone) {
    const preloader = $("#preloader");
    const bar = $("#preloaderBar");
    const count = $("#preloaderCount");
    if (!preloader || reduceMotion) {
      if (preloader) preloader.classList.add("done");
      onDone();
      return;
    }
    const duration = 1300;
    const start = performance.now();
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      preloader.classList.add("done");
      setTimeout(onDone, 250);
    };
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      const value = Math.round(eased * 100);
      if (bar) bar.style.width = value + "%";
      if (count) count.textContent = value;
      if (t < 1) requestAnimationFrame(tick);
      else setTimeout(finish, 150);
    };
    requestAnimationFrame(tick);
    setTimeout(finish, 4000); // filet de sécurité
  }

  /* ─────────── 2. TITRE LETTRE PAR LETTRE ─────────── */
  function splitText() {
    $$(".split-text").forEach((el) => {
      const words = el.textContent.trim().split(/\s+/);
      el.setAttribute("aria-label", words.join(" "));
      el.textContent = "";
      let ci = 0;
      words.forEach((word, wi) => {
        const w = document.createElement("span");
        w.className = "word";
        w.setAttribute("aria-hidden", "true");
        for (const ch of word) {
          const c = document.createElement("span");
          c.className = "char";
          c.textContent = ch;
          c.style.setProperty("--ci", ci++);
          w.appendChild(c);
        }
        el.appendChild(w);
        if (wi < words.length - 1) el.appendChild(document.createTextNode(" "));
      });
    });
  }

  /* ─────────── 3. THÈME CLAIR / SOMBRE ─────────── */
  function initTheme() {
    const btn = $("#themeToggle");
    if (!btn) return;
    btn.addEventListener("click", (e) => {
      const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      const apply = () => {
        root.setAttribute("data-theme", next);
        try { localStorage.setItem("theme", next); } catch (err) {}
        document.dispatchEvent(new Event("themechange"));
      };
      if (!document.startViewTransition || reduceMotion) { apply(); return; }
      // Révélation circulaire depuis le bouton
      const x = e.clientX || window.innerWidth - 60;
      const y = e.clientY || 40;
      const r = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
      const transition = document.startViewTransition(apply);
      transition.ready.then(() => {
        root.animate(
          { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${r}px at ${x}px ${y}px)`] },
          { duration: 700, easing: "cubic-bezier(.22,1,.36,1)", pseudoElement: "::view-transition-new(root)" }
        );
      }).catch(() => {});
    });
  }

  /* ─────────── 4. RÉSEAU DE NEURONES ANIMÉ ─────────── */
  function initNeuralNetwork() {
    const canvas = $("#neuralCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const hero = canvas.parentElement;

    let w = 0, h = 0, dpr = 1;
    let nodes = [];
    let pulses = [];
    let colorA = "124,92,255", colorB = "34,211,238";
    const mouse = { x: -9999, y: -9999, active: false };
    const LINK = 150;
    let running = false;
    let visible = true;
    let lastPulse = 0;

    function readColors() {
      const cs = getComputedStyle(root);
      colorA = cs.getPropertyValue("--node").trim() || colorA;
      colorB = cs.getPropertyValue("--node-2").trim() || colorB;
    }

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = hero.clientWidth;
      h = hero.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const target = Math.min(120, Math.round((w * h) / 11000));
      while (nodes.length < target) nodes.push(makeNode());
      nodes.length = target;
      if (!running) draw(0);
    }

    function makeNode() {
      const speed = 0.25;
      return {
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * speed,
        vy: (Math.random() - 0.5) * speed,
        r: Math.random() * 1.6 + 1,
        hue: Math.random() < 0.5 ? 0 : 1,
        phase: Math.random() * Math.PI * 2,
      };
    }

    function step(time) {
      for (const n of nodes) {
        // attraction douce vers la souris
        if (mouse.active) {
          const dx = mouse.x - n.x, dy = mouse.y - n.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < 220 * 220 && d2 > 1) {
            const f = 0.012 / Math.sqrt(d2);
            n.vx += dx * f;
            n.vy += dy * f;
          }
        }
        n.vx *= 0.985; n.vy *= 0.985;
        // vitesse minimale pour que le réseau reste vivant
        const sp = Math.hypot(n.vx, n.vy);
        if (sp < 0.12) { n.vx += (Math.random() - 0.5) * 0.05; n.vy += (Math.random() - 0.5) * 0.05; }
        n.x += n.vx; n.y += n.vy;
        if (n.x < -20) n.x = w + 20; else if (n.x > w + 20) n.x = -20;
        if (n.y < -20) n.y = h + 20; else if (n.y > h + 20) n.y = -20;
      }

      // nouvelles impulsions (signaux qui voyagent entre neurones)
      if (time - lastPulse > 90 && pulses.length < 40) {
        lastPulse = time;
        const a = nodes[(Math.random() * nodes.length) | 0];
        let best = null, bestD = LINK;
        for (const b of nodes) {
          if (b === a) continue;
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < bestD && Math.random() < 0.6) { best = b; bestD = d; }
        }
        if (best) pulses.push({ a, b: best, t: 0, speed: 0.012 + Math.random() * 0.018 });
      }
    }

    function draw(time) {
      ctx.clearRect(0, 0, w, h);

      // liens
      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx * dx + dy * dy;
          if (d2 > LINK * LINK) continue;
          const alpha = (1 - Math.sqrt(d2) / LINK) * 0.28;
          ctx.strokeStyle = `rgba(${a.hue ? colorB : colorA},${alpha})`;
          ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
        // liens vers la souris
        if (mouse.active) {
          const d = Math.hypot(a.x - mouse.x, a.y - mouse.y);
          if (d < 200) {
            ctx.strokeStyle = `rgba(${colorB},${(1 - d / 200) * 0.55})`;
            ctx.lineWidth = 1.2;
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
          }
        }
      }

      // neurones
      for (const n of nodes) {
        const glow = 0.55 + Math.sin(time * 0.002 + n.phase) * 0.35;
        ctx.fillStyle = `rgba(${n.hue ? colorB : colorA},${glow})`;
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2); ctx.fill();
      }

      // impulsions lumineuses
      pulses = pulses.filter((p) => p.t <= 1);
      for (const p of pulses) {
        p.t += p.speed;
        const x = p.a.x + (p.b.x - p.a.x) * p.t;
        const y = p.a.y + (p.b.y - p.a.y) * p.t;
        const g = ctx.createRadialGradient(x, y, 0, x, y, 10);
        g.addColorStop(0, `rgba(255,255,255,.95)`);
        g.addColorStop(0.3, `rgba(${colorB},.7)`);
        g.addColorStop(1, `rgba(${colorB},0)`);
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(x, y, 10, 0, Math.PI * 2); ctx.fill();
      }

      // halo autour de la souris
      if (mouse.active) {
        const g = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 160);
        g.addColorStop(0, `rgba(${colorA},.16)`);
        g.addColorStop(1, `rgba(${colorA},0)`);
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(mouse.x, mouse.y, 160, 0, Math.PI * 2); ctx.fill();
      }
    }

    function loop(time) {
      if (!running) return;
      step(time);
      draw(time);
      requestAnimationFrame(loop);
    }
    function start() {
      if (running || reduceMotion || !visible || document.hidden) return;
      running = true;
      requestAnimationFrame(loop);
    }
    function stop() { running = false; }

    readColors();
    resize();
    window.addEventListener("resize", () => { resize(); }, { passive: true });
    document.addEventListener("themechange", () => { readColors(); if (!running) draw(0); });

    hero.addEventListener("pointermove", (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
      mouse.active = true;
    }, { passive: true });
    hero.addEventListener("pointerleave", () => { mouse.active = false; });

    new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      visible ? start() : stop();
    }).observe(hero);
    document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
    start();
  }

  /* ─────────── 5. TEXTE QUI S'ÉCRIT ─────────── */
  function initTypewriter() {
    const el = $("#typewriter");
    if (!el || reduceMotion) return;
    const words = (el.dataset.words || "").split("|").filter(Boolean);
    if (words.length < 2) return;
    let wi = 0, ci = words[0].length, deleting = true;
    const tick = () => {
      const word = words[wi];
      ci += deleting ? -1 : 1;
      el.textContent = word.slice(0, ci);
      let delay = deleting ? 40 : 85;
      if (!deleting && ci === word.length) { deleting = true; delay = 2200; }
      else if (deleting && ci === 0) { deleting = false; wi = (wi + 1) % words.length; delay = 350; }
      setTimeout(tick, delay);
    };
    setTimeout(tick, 2600);
  }

  /* ─────────── 6. CURSEUR PERSONNALISÉ ─────────── */
  function initCursor() {
    if (!finePointer || reduceMotion) return;
    const dot = $("#cursorDot"), ring = $("#cursorRing");
    if (!dot || !ring) return;
    root.classList.add("has-cursor");
    let x = innerWidth / 2, y = innerHeight / 2, rx = x, ry = y;
    window.addEventListener("pointermove", (e) => {
      x = e.clientX; y = e.clientY;
      dot.style.transform = `translate(${x}px, ${y}px)`;
      dot.classList.remove("hidden"); ring.classList.remove("hidden");
    }, { passive: true });
    document.addEventListener("pointerleave", () => { dot.classList.add("hidden"); ring.classList.add("hidden"); });
    const follow = () => {
      rx += (x - rx) * 0.18; ry += (y - ry) * 0.18;
      ring.style.transform = `translate(${rx}px, ${ry}px)`;
      requestAnimationFrame(follow);
    };
    follow();
    document.addEventListener("pointerover", (e) => {
      ring.classList.toggle("hover", !!e.target.closest("a, button, input, textarea, .tilt"));
    });
  }

  /* ─────────── 7. NAVIGATION ─────────── */
  function initNav() {
    const wrap = $("#navWrap");
    const links = $$(".nav-link");
    const indicator = $("#navIndicator");
    const menuBtn = $("#menuBtn");
    const navLinks = $("#navLinks");
    const progress = $("#scrollProgress");
    const backToTop = $("#backToTop");
    const sections = links.map((l) => $(l.getAttribute("href"))).filter(Boolean);
    let lastY = scrollY;

    function moveIndicator(link) {
      if (!indicator) return;
      if (!link) { indicator.style.opacity = "0"; return; }
      indicator.style.opacity = "1";
      indicator.style.width = link.offsetWidth + "px";
      indicator.style.transform = `translateX(${link.offsetLeft}px)`;
    }

    function onScroll() {
      const y = scrollY;
      const max = document.documentElement.scrollHeight - innerHeight;
      const ratio = max > 0 ? y / max : 0;

      if (wrap) {
        wrap.classList.toggle("scrolled", y > 30);
        const menuOpen = navLinks && navLinks.classList.contains("open");
        wrap.classList.toggle("hide", y > lastY && y > 400 && !menuOpen);
      }
      lastY = y;

      if (progress) progress.style.transform = `scaleX(${ratio})`;
      if (backToTop) {
        backToTop.classList.toggle("visible", y > 600);
        backToTop.style.setProperty("--off", 100 - ratio * 100);
      }

      let current = null;
      for (const s of sections) if (s.getBoundingClientRect().top <= innerHeight * 0.35) current = s;
      links.forEach((l) => l.classList.toggle("active", current && l.getAttribute("href") === "#" + current.id));
      moveIndicator(links.find((l) => l.classList.contains("active")));
    }

    function closeMenu() {
      if (!navLinks || !menuBtn) return;
      navLinks.classList.remove("open");
      menuBtn.setAttribute("aria-expanded", "false");
    }

    if (menuBtn && navLinks) {
      menuBtn.addEventListener("click", () => {
        const open = navLinks.classList.toggle("open");
        menuBtn.setAttribute("aria-expanded", String(open));
      });
      links.forEach((l) => l.addEventListener("click", closeMenu));
      document.addEventListener("click", (e) => {
        if (!navLinks.contains(e.target) && !menuBtn.contains(e.target)) closeMenu();
      });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });
    }

    if (backToTop) backToTop.addEventListener("click", () => scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" }));

    let ticking = false;
    window.addEventListener("scroll", () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => { onScroll(); ticking = false; });
    }, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    onScroll();
  }

  /* ─────────── 8. APPARITION AU SCROLL ─────────── */
  function initReveal() {
    // délais en cascade pour le hero
    $$(".hero .reveal").forEach((el, i) => el.style.setProperty("--hd", 500 + i * 120));

    const els = $$(".reveal:not(.hero .reveal)");
    if (!("IntersectionObserver" in window)) { els.forEach((el) => el.classList.add("in")); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("in");
        io.unobserve(entry.target);
        if (entry.target.querySelector(".counter")) animateCounter(entry.target.querySelector(".counter"));
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
    els.forEach((el) => io.observe(el));
  }

  function revealHero() {
    root.classList.add("loaded");
    $$(".hero .reveal").forEach((el) => el.classList.add("in"));
  }

  /* ─────────── 9. COMPTEURS ─────────── */
  function animateCounter(el) {
    const raw = el.dataset.value || el.textContent;
    const match = raw.match(/^(\D*)(\d+)(.*)$/);
    if (!match || reduceMotion) return;
    const [, prefix, num, suffix] = match;
    const target = parseInt(num, 10);
    const duration = 1600;
    const start = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 4);
      el.textContent = prefix + Math.round(target * eased) + suffix;
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  /* ─────────── 10. CARTES 3D, PROJECTEUR, BOUTONS MAGNÉTIQUES ─────────── */
  function initPointerEffects() {
    if (!finePointer || reduceMotion) return;

    $$(".spotlight").forEach((el) => {
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        el.style.setProperty("--mx", e.clientX - r.left + "px");
        el.style.setProperty("--my", e.clientY - r.top + "px");
      });
    });

    $$(".tilt").forEach((el) => {
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `rotateY(${px * 8}deg) rotateX(${-py * 8}deg) translateY(-6px)`;
      });
      el.addEventListener("pointerleave", () => { el.style.transform = ""; });
    });

    $$(".magnetic").forEach((el) => {
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        el.style.transform = `translate(${x * 0.25}px, ${y * 0.35}px)`;
      });
      el.addEventListener("pointerleave", () => { el.style.transform = ""; });
    });

    // léger effet de profondeur sur le portrait
    const portrait = $(".portrait");
    const hero = $(".hero");
    if (portrait && hero) {
      hero.addEventListener("pointermove", (e) => {
        const px = e.clientX / innerWidth - 0.5;
        const py = e.clientY / innerHeight - 0.5;
        portrait.style.transform = `translate(${px * -18}px, ${py * -18}px)`;
      }, { passive: true });
    }
  }

  /* ─────────── 11. LIGNE DU PARCOURS QUI SE DESSINE ─────────── */
  function initTimeline() {
    const timelines = $$(".timeline");
    if (!timelines.length) return;
    const update = () => {
      timelines.forEach((tl) => {
        const r = tl.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, (innerHeight * 0.75 - r.top) / r.height));
        tl.style.setProperty("--p", reduceMotion ? 1 : p);
      });
    };
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  /* ─────────── 11 bis. FILTRE DES PROJETS ─────────── */
  function initProjectFilters() {
    const group = $(".filters");
    if (!group) return;
    const buttons = $$(".filter-btn", group);
    const indicator = $(".filter-indicator", group);
    const cards = $$(".project-card");

    const moveIndicator = (btn) => {
      if (!indicator || !btn) return;
      indicator.style.width = btn.offsetWidth + "px";
      indicator.style.transform = `translateX(${btn.offsetLeft}px)`;
    };

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const filter = btn.dataset.filter;
        buttons.forEach((b) => {
          b.classList.toggle("active", b === btn);
          b.setAttribute("aria-pressed", String(b === btn));
        });
        moveIndicator(btn);
        let shown = 0;
        cards.forEach((card) => {
          const show = filter === "*" || card.dataset.category === filter;
          card.classList.remove("is-entering");
          card.classList.toggle("is-hidden", !show);
          if (show && !reduceMotion) {
            void card.offsetWidth; // relancer l'animation
            card.style.animationDelay = shown++ * 70 + "ms";
            card.classList.add("is-entering", "in");
          }
        });
      });
    });

    const place = () => moveIndicator(group.querySelector(".filter-btn.active"));
    window.addEventListener("resize", place, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(place);
    place();
  }

  /* ─────────── 12. NOTIFICATION ─────────── */
  let toastTimer;
  function toast(message, type = "success") {
    const el = $("#toast");
    if (!el) return;
    const icon = type === "success" ? "fa-circle-check" : "fa-circle-exclamation";
    el.className = `toast ${type}`;
    el.innerHTML = `<i class="fa-solid ${icon}"></i><span></span>`;
    el.querySelector("span").textContent = message;
    requestAnimationFrame(() => el.classList.add("visible"));
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("visible"), 4200);
  }

  /* ─────────── 13. COPIER L'EMAIL ─────────── */
  function initCopy() {
    $$("[data-copy]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(btn.dataset.copy);
          toast("Adresse email copiée !");
        } catch (e) {
          window.location.href = "mailto:" + btn.dataset.copy;
        }
      });
    });
  }

  /* ─────────── 14. FORMULAIRE DE CONTACT ─────────── */
  function initContactForm() {
    const form = $("#contactForm");
    if (!form) return;
    const emailOk = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      let valid = true;
      $$("[required]", form).forEach((input) => {
        const bad = !input.value.trim() || (input.type === "email" && !emailOk(input.value.trim()));
        input.closest(".field").classList.toggle("invalid", bad);
        if (bad) valid = false;
      });
      if (!valid) { toast("Merci de remplir correctement les champs obligatoires.", "error"); return; }

      const btn = form.querySelector('button[type="submit"]');
      const label = btn.querySelector(".btn-text");
      const original = label.textContent;
      btn.disabled = true;
      label.textContent = "Envoi en cours…";

      try {
        const response = await fetch(form.action, {
          method: "POST",
          headers: { "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value },
          body: new FormData(form),
        });
        const data = await response.json();
        if (data.status === "success") {
          toast(data.message || "Message envoyé !");
          form.reset();
        } else {
          toast(data.message || "Une erreur est survenue.", "error");
        }
      } catch (err) {
        toast("Erreur réseau. Veuillez réessayer.", "error");
      } finally {
        btn.disabled = false;
        label.textContent = original;
      }
    });

    form.addEventListener("input", (e) => {
      const field = e.target.closest(".field");
      if (field) field.classList.remove("invalid");
    });
  }

  /* ─────────── DÉMARRAGE ─────────── */
  splitText();
  initTheme();
  initNav();
  initReveal();
  initNeuralNetwork();
  initCursor();
  initPointerEffects();
  initTimeline();
  initProjectFilters();
  initCopy();
  initContactForm();

  const year = $("#year");
  if (year) year.textContent = new Date().getFullYear();

  runPreloader(() => {
    revealHero();
    initTypewriter();
  });

  console.log(
    "%c Mahamat Hassan Oumar %c Data Science & Machine Learning ",
    "background:linear-gradient(90deg,#7c5cff,#22d3ee);color:#fff;padding:6px 10px;border-radius:6px 0 0 6px;font-weight:700",
    "background:#0a0c1b;color:#9aa1bf;padding:6px 10px;border-radius:0 6px 6px 0"
  );
})();
