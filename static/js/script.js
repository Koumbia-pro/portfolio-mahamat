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
    // Affiché une seule fois par visite : inutile de faire attendre à chaque page vue.
    if (!preloader || reduceMotion || root.classList.contains("no-preload")) {
      if (preloader) preloader.remove();
      onDone();
      return;
    }
    try { sessionStorage.setItem("pf-intro", "1"); } catch (e) {}
    const duration = 900;
    const start = performance.now();
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      preloader.classList.add("done");
      setTimeout(onDone, 250);
      setTimeout(() => preloader.remove(), 1100);
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
    setTimeout(finish, 2500); // filet de sécurité (onglet en arrière-plan…)
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
  // Optimisé : moins de neurones sur mobile, liens regroupés par opacité
  // (quelques tracés par image au lieu de centaines), 30 images/s sur mobile,
  // arrêt complet quand l'accueil n'est plus visible.
  function initNeuralNetwork() {
    const canvas = $("#neuralCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d", { alpha: true });
    const hero = canvas.parentElement;
    const coarse = !finePointer;

    let w = 0, h = 0;
    let nodes = [];
    let pulses = [];
    let colorA = "124,92,255", colorB = "34,211,238";
    const mouse = { x: -9999, y: -9999, active: false };
    const LINK = coarse ? 120 : 140;
    const LINK2 = LINK * LINK;
    const LEVELS = 4; // niveaux d'opacité des liens
    const frameGap = coarse ? 1000 / 30 : 1000 / 60;
    let running = false;
    let visible = true;
    let lastPulse = 0;
    let lastFrame = 0;

    function readColors() {
      const cs = getComputedStyle(root);
      colorA = cs.getPropertyValue("--node").trim() || colorA;
      colorB = cs.getPropertyValue("--node-2").trim() || colorB;
    }

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, coarse ? 1.5 : 1.75);
      w = hero.clientWidth;
      h = hero.clientHeight;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const target = Math.min(coarse ? 38 : 75, Math.round((w * h) / (coarse ? 9000 : 15000)));
      while (nodes.length < target) nodes.push(makeNode());
      nodes.length = target;
      pulses = pulses.filter((p) => nodes.includes(p.a) && nodes.includes(p.b));
      if (!running) draw(performance.now());
    }

    function makeNode() {
      return {
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
        r: Math.random() * 1.6 + 1,
        hue: Math.random() < 0.5 ? 0 : 1,
        phase: Math.random() * Math.PI * 2,
      };
    }

    function step(time, k) {
      for (const n of nodes) {
        if (mouse.active) {
          const dx = mouse.x - n.x, dy = mouse.y - n.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < 48400 && d2 > 1) {
            const f = 0.012 / Math.sqrt(d2);
            n.vx += dx * f; n.vy += dy * f;
          }
        }
        n.vx *= 0.985; n.vy *= 0.985;
        if (Math.abs(n.vx) + Math.abs(n.vy) < 0.15) { n.vx += (Math.random() - 0.5) * 0.05; n.vy += (Math.random() - 0.5) * 0.05; }
        n.x += n.vx * k; n.y += n.vy * k;
        if (n.x < -20) n.x = w + 20; else if (n.x > w + 20) n.x = -20;
        if (n.y < -20) n.y = h + 20; else if (n.y > h + 20) n.y = -20;
      }

      if (time - lastPulse > 160 && pulses.length < 14 && nodes.length > 1) {
        lastPulse = time;
        const a = nodes[(Math.random() * nodes.length) | 0];
        let best = null, bestD = LINK2;
        for (const b of nodes) {
          if (b === a) continue;
          const dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy;
          if (d2 < bestD && Math.random() < 0.6) { best = b; bestD = d2; }
        }
        if (best) pulses.push({ a, b: best, t: 0, speed: 0.012 + Math.random() * 0.018 });
      }
    }

    // Un chemin par (couleur, niveau d'opacité) : 8 tracés au lieu de centaines
    const buckets = [[], []].map(() => Array.from({ length: LEVELS }, () => []));

    function draw(time) {
      ctx.clearRect(0, 0, w, h);
      for (const c of buckets) for (const b of c) b.length = 0;

      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx * dx + dy * dy;
          if (d2 > LINK2) continue;
          const lvl = Math.min(LEVELS - 1, ((1 - d2 / LINK2) * LEVELS) | 0);
          buckets[a.hue][lvl].push(a.x, a.y, b.x, b.y);
        }
      }
      ctx.lineWidth = 1;
      for (let hue = 0; hue < 2; hue++) {
        for (let lvl = 0; lvl < LEVELS; lvl++) {
          const seg = buckets[hue][lvl];
          if (!seg.length) continue;
          ctx.strokeStyle = `rgba(${hue ? colorB : colorA},${((lvl + 1) / LEVELS) * 0.26})`;
          ctx.beginPath();
          for (let s = 0; s < seg.length; s += 4) { ctx.moveTo(seg[s], seg[s + 1]); ctx.lineTo(seg[s + 2], seg[s + 3]); }
          ctx.stroke();
        }
      }

      // liens vers la souris (un seul tracé)
      if (mouse.active) {
        ctx.strokeStyle = `rgba(${colorB},.35)`;
        ctx.beginPath();
        for (const n of nodes) {
          const dx = n.x - mouse.x, dy = n.y - mouse.y;
          if (dx * dx + dy * dy < 32400) { ctx.moveTo(n.x, n.y); ctx.lineTo(mouse.x, mouse.y); }
        }
        ctx.stroke();
      }

      // neurones
      for (let hue = 0; hue < 2; hue++) {
        ctx.fillStyle = `rgb(${hue ? colorB : colorA})`;
        for (const n of nodes) {
          if (n.hue !== hue) continue;
          ctx.globalAlpha = 0.55 + Math.sin(time * 0.002 + n.phase) * 0.35;
          ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2); ctx.fill();
        }
      }

      // impulsions lumineuses (deux cercles, sans dégradé recalculé)
      pulses = pulses.filter((p) => p.t <= 1);
      for (const p of pulses) {
        p.t += p.speed;
        const x = p.a.x + (p.b.x - p.a.x) * p.t;
        const y = p.a.y + (p.b.y - p.a.y) * p.t;
        ctx.fillStyle = `rgb(${colorB})`;
        ctx.globalAlpha = 0.25;
        ctx.beginPath(); ctx.arc(x, y, 6, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#fff";
        ctx.globalAlpha = 0.9;
        ctx.beginPath(); ctx.arc(x, y, 1.8, 0, Math.PI * 2); ctx.fill();
      }
      ctx.globalAlpha = 1;
    }

    function loop(time) {
      if (!running) return;
      requestAnimationFrame(loop);
      const delta = time - lastFrame;
      if (delta < frameGap - 2) return; // limite d'images par seconde
      lastFrame = time;
      step(time, Math.min(3, delta / 16.7));
      draw(time);
    }
    function start() {
      if (running || reduceMotion || !visible || document.hidden) return;
      running = true;
      lastFrame = performance.now();
      requestAnimationFrame(loop);
    }
    function stop() { running = false; }

    readColors();
    resize();
    let resizeTimer;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resize, 150);
    }, { passive: true });
    document.addEventListener("themechange", () => { readColors(); if (!running) draw(performance.now()); });

    if (finePointer) {
      hero.addEventListener("pointermove", (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
        mouse.active = true;
      }, { passive: true });
      hero.addEventListener("pointerleave", () => { mouse.active = false; });
    }

    new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      visible ? start() : stop();
    }, { rootMargin: "-80px 0px 0px 0px" }).observe(hero);
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
    let following = false;
    const follow = () => {
      rx += (x - rx) * 0.2; ry += (y - ry) * 0.2;
      ring.style.transform = `translate3d(${rx}px, ${ry}px, 0)`;
      if (Math.abs(x - rx) + Math.abs(y - ry) > 0.3) requestAnimationFrame(follow);
      else following = false;
    };
    window.addEventListener("pointermove", (e) => {
      x = e.clientX; y = e.clientY;
      dot.style.transform = `translate3d(${x}px, ${y}px, 0)`;
      if (dot.classList.contains("hidden")) { dot.classList.remove("hidden"); ring.classList.remove("hidden"); }
      if (!following) { following = true; requestAnimationFrame(follow); }
    }, { passive: true });
    document.addEventListener("pointerleave", () => { dot.classList.add("hidden"); ring.classList.add("hidden"); });
    let hovering = false;
    document.addEventListener("pointerover", (e) => {
      const h = !!e.target.closest("a, button, input, textarea, .tilt");
      if (h !== hovering) { hovering = h; ring.classList.toggle("hover", h); }
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
    const ringCircle = backToTop ? $("circle", backToTop) : null;
    const state = { scrolled: null, top: null, current: undefined };

    function moveIndicator(link) {
      if (!indicator) return;
      if (!link) { indicator.style.opacity = "0"; return; }
      indicator.style.opacity = "1";
      indicator.style.width = link.offsetWidth + "px";
      indicator.style.transform = `translateX(${link.offsetLeft}px)`;
    }

    let maxScroll = 0;
    let offsets = [];
    function measure() {
      maxScroll = document.documentElement.scrollHeight - innerHeight;
      offsets = sections.map((s) => s.getBoundingClientRect().top + scrollY);
    }

    function onScroll() {
      const y = scrollY;
      const ratio = maxScroll > 0 ? Math.min(1, y / maxScroll) : 0;

      // La barre reste fixe en haut ; elle prend un fond dès qu'on défile.
      const scrolled = y > 30;
      if (wrap && scrolled !== state.scrolled) { state.scrolled = scrolled; wrap.classList.toggle("scrolled", scrolled); }

      if (progress) progress.style.transform = `scaleX(${ratio})`;
      const top = y > 600;
      if (backToTop && top !== state.top) { state.top = top; backToTop.classList.toggle("visible", top); }
      if (ringCircle && top) ringCircle.style.strokeDashoffset = 100 - ratio * 100;

      let current = null;
      const line = y + innerHeight * 0.35;
      offsets.forEach((o, i) => { if (o <= line) current = sections[i]; });
      if (current !== state.current) {
        state.current = current;
        links.forEach((l) => l.classList.toggle("active", !!current && l.getAttribute("href") === "#" + current.id));
        moveIndicator(links.find((l) => l.classList.contains("active")));
      }
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
    const refresh = () => { measure(); state.current = undefined; onScroll(); };
    window.addEventListener("resize", refresh, { passive: true });
    window.addEventListener("load", refresh);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);
    // les filtres de projets changent la hauteur de la page
    document.addEventListener("layoutchange", refresh);
    refresh();
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
    // Après l'animation d'entrée, remplacer les lettres animées par du texte
    // simple : moins d'éléments à dessiner et un dégradé continu sur le mot.
    const chars = $$(".hero-name .char");
    const delay = chars.length * 35 + 1300;
    setTimeout(() => {
      $$(".hero-name .word").forEach((word) => {
        word.textContent = word.textContent;
        word.classList.add("settled");
      });
    }, reduceMotion ? 0 : delay);
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
    if (reduceMotion) { timelines.forEach((tl) => tl.style.setProperty("--p", 1)); return; }
    const visible = new Set();
    const last = new Map();
    let ticking = false;
    const update = () => {
      ticking = false;
      visible.forEach((tl) => {
        const r = tl.getBoundingClientRect();
        const p = Math.round(Math.min(1, Math.max(0, (innerHeight * 0.75 - r.top) / r.height)) * 200) / 200;
        if (last.get(tl) !== p) { last.set(tl, p); tl.style.setProperty("--p", p); }
      });
    };
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => (e.isIntersecting ? visible.add(e.target) : visible.delete(e.target)));
      update();
    });
    timelines.forEach((tl) => io.observe(tl));
    window.addEventListener("scroll", () => {
      if (!ticking && visible.size) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
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
      indicator.style.height = btn.offsetHeight + "px";
      indicator.style.top = btn.offsetTop + "px";
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
        // Sur mobile, la barre de filtres défile : garder le bouton choisi visible
        btn.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "nearest", inline: "center" });
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
        document.dispatchEvent(new Event("layoutchange"));
      });
    });

    const place = () => moveIndicator(group.querySelector(".filter-btn.active"));
    window.addEventListener("resize", place, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(place);
    place();
  }

  /* ─────────── 11 ter. PAUSE DES ANIMATIONS HORS ÉCRAN ─────────── */
  // Les animations en boucle (portrait, orbite, bandeau, halo du contact…)
  // ne tournent que lorsque leur zone est visible : le navigateur ne
  // travaille plus pour des éléments que personne ne regarde.
  function initOffscreenPause() {
    if (!("IntersectionObserver" in window)) return;
    const zones = $$(".hero, .marquee, .contact-card, .skills-grid, .back-to-top");
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => e.target.classList.toggle("anim-paused", !e.isIntersecting));
    }, { rootMargin: "100px 0px" });
    zones.forEach((z) => io.observe(z));
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
    const tooShort = (input) => input.minLength > 0 && input.value.trim().length < input.minLength;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      let valid = true;
      $$("[required]", form).forEach((input) => {
        const bad = !input.value.trim() || tooShort(input) || (input.type === "email" && !emailOk(input.value.trim()));
        input.closest(".field").classList.toggle("invalid", bad);
        if (bad) valid = false;
      });
      if (!valid) {
        toast("Merci de remplir correctement les champs obligatoires.", "error");
        const first = form.querySelector(".field.invalid input, .field.invalid textarea");
        if (first) first.focus();
        return;
      }

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
        let data = {};
        if ((response.headers.get("content-type") || "").includes("application/json")) {
          data = await response.json();
        } else if (response.status === 403) {
          data = { message: "Votre session a expiré : rechargez la page puis réessayez." };
        }
        if (response.ok && data.status === "success") {
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
  initOffscreenPause();
  initProjectFilters();
  initCopy();
  initContactForm();

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
