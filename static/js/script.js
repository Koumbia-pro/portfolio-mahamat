/* =========================================================
   PORTFOLIO — MAHAMAT HASSAN OUMAR
   JavaScript principal — Version corrigée
   ========================================================= */


/* =========================================================
   1. MENU MOBILE
   ========================================================= */
const sidebar    = document.getElementById("sidebar");
const mobileMenu = document.getElementById("mobileMenu");

if (mobileMenu && sidebar) {
    mobileMenu.addEventListener("click", () => {
        sidebar.classList.toggle("open");
        mobileMenu.innerHTML = sidebar.classList.contains("open")
            ? '<i class="fa-solid fa-xmark"></i>'
            : '<i class="fa-solid fa-bars"></i>';
    });
}


/* =========================================================
   2. FERMER LE MENU APRÈS UN CLIC
   ========================================================= */
const navLinks = document.querySelectorAll(".nav-link");

navLinks.forEach((link) => {
    link.addEventListener("click", () => {
        if (sidebar)    sidebar.classList.remove("open");
        if (mobileMenu) mobileMenu.innerHTML = '<i class="fa-solid fa-bars"></i>';
    });
});


/* =========================================================
   3. NAVIGATION ACTIVE AU SCROLL
   ========================================================= */

// Exclure les sections sr-only
const sections = document.querySelectorAll(
    "section[id]:not(.sr-only)"
);

function updateActiveLink() {
    let currentSection = "accueil";

    sections.forEach((section) => {
        if (section.getBoundingClientRect().top <= 180) {
            currentSection = section.id;
        }
    });

    navLinks.forEach((link) => {
        link.classList.remove("active");
        if (link.getAttribute("href") === `#${currentSection}`) {
            link.classList.add("active");
        }
    });
}

window.addEventListener("scroll", updateActiveLink, { passive: true });
updateActiveLink();


/* =========================================================
   4. BOUTON MODE SOMBRE
   ========================================================= */
const themeSwitch = document.getElementById("themeSwitch");

if (themeSwitch) {
    themeSwitch.addEventListener("click", () => {
        themeSwitch.classList.toggle("active");
    });
}


/* =========================================================
   5. ANIMATION DES BARRES DE COMPÉTENCES — VERSION CORRIGÉE
   ========================================================= */
const skillBars     = document.querySelectorAll(".skill em");
let skillsAnimated  = false;

function animateSkills() {
    const skillsSection = document.getElementById("competences");
    if (!skillsSection) return;

    const position = skillsSection.getBoundingClientRect().top;

    if (position < window.innerHeight - 100 && !skillsAnimated) {
        skillsAnimated = true;

        skillBars.forEach((bar) => {

            // Lire la valeur depuis l'attribut style HTML
            const styleAttr = bar.getAttribute("style") || "";
            const match     = styleAttr.match(/width:\s*([\d.]+)%/);
            const finalWidth = match ? match[1] + "%" : "0%";

            // Mettre à 0 sans transition
            bar.style.transition = "none";
            bar.style.width      = "0%";

            // Animer après un court délai
            setTimeout(() => {
                bar.style.transition = "width 1.2s cubic-bezier(0.4, 0, 0.2, 1)";
                bar.style.width      = finalWidth;
            }, 150);
        });
    }
}

window.addEventListener("scroll", animateSkills, { passive: true });
animateSkills();


/* =========================================================
   6. ANIMATION D'APPARITION DES ÉLÉMENTS
   ========================================================= */
const animatedElements = document.querySelectorAll(
    ".skill-card, .project-card, .service-card, " +
    ".timeline-item, .stats > div"
);

const observer = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show-element");
                observer.unobserve(entry.target);
            }
        });
    },
    { threshold: 0.12 }
);

animatedElements.forEach((element) => {
    element.classList.add("hidden-element");
    observer.observe(element);
});


/* =========================================================
   7. FORMULAIRE DE CONTACT — ENVOI AJAX VERS DJANGO
   ========================================================= */
const contactForm = document.getElementById("contactForm");

if (contactForm) {
    contactForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const submitBtn  = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        // Afficher le chargement
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Envoi...';
        submitBtn.disabled  = true;

        try {
            // Récupérer le token CSRF Django
            const csrfToken = document.querySelector(
                '[name=csrfmiddlewaretoken]'
            ).value;

            // Envoyer les données via fetch
            const response = await fetch("/contact/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams(new FormData(contactForm)),
            });

            const data = await response.json();

            if (data.status === "success") {
                showNotification(data.message, "success");
                contactForm.reset();
            } else {
                showNotification(data.message, "error");
            }

        } catch (error) {
            showNotification(
                "Une erreur réseau est survenue. Veuillez réessayer.",
                "error"
            );
        } finally {
            // Remettre le bouton
            submitBtn.innerHTML = originalText;
            submitBtn.disabled  = false;
        }
    });
}


/* =========================================================
   8. NOTIFICATION
   ========================================================= */
function showNotification(message, type = "success") {

    // Supprimer l'ancienne notification
    const old = document.querySelector(".portfolio-notification");
    if (old) old.remove();

    // Créer la notification
    const notification    = document.createElement("div");
    notification.className = `portfolio-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            ${type === "success"
                ? '<i class="fa-solid fa-check"></i>'
                : '<i class="fa-solid fa-exclamation"></i>'
            }
        </div>
        <span>${message}</span>
        <button class="notification-close" aria-label="Fermer">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;

    document.body.appendChild(notification);

    // Afficher
    setTimeout(() => notification.classList.add("visible"), 50);

    // Fermer au clic
    notification.querySelector(".notification-close")
        .addEventListener("click", () => {
            notification.classList.remove("visible");
            setTimeout(() => notification.remove(), 300);
        });

    // Fermer automatiquement après 4 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove("visible");
            setTimeout(() => {
                if (notification.parentNode) notification.remove();
            }, 300);
        }
    }, 4000);
}


/* =========================================================
   9. COMPTEUR DES STATISTIQUES — VERSION CORRIGÉE
   ========================================================= */
const statNumbers    = document.querySelectorAll(".stats strong");
let countersStarted  = false;

function animateCounters() {
    const statsSection = document.querySelector(".stats");
    if (!statsSection) return;

    const position = statsSection.getBoundingClientRect().top;

    if (position < window.innerHeight - 100 && !countersStarted) {
        countersStarted = true;

        statNumbers.forEach((element) => {
            const original = element.textContent.trim();

            // Ne pas animer les valeurs avec "/" (ex: 24/7)
            if (original.includes("/")) return;

            const number = parseInt(original.replace(/\D/g, ""), 10);
            if (isNaN(number)) return;

            // Déterminer le suffixe
            const suffix = original.includes("+") ? "+"
                         : original.includes("%") ? "%"
                         : "";

            let current   = 0;
            const increment = Math.max(1, Math.ceil(number / 40));

            const timer = setInterval(() => {
                current += increment;
                if (current >= number) {
                    current = number;
                    clearInterval(timer);
                }
                element.textContent = current + suffix;
            }, 30);
        });
    }
}

window.addEventListener("scroll", animateCounters, { passive: true });
animateCounters();


/* =========================================================
   10. BOUTON RETOUR EN HAUT
   ========================================================= */
const backToTop       = document.createElement("button");
backToTop.className   = "back-to-top";
backToTop.innerHTML   = '<i class="fa-solid fa-arrow-up"></i>';
backToTop.setAttribute("aria-label", "Retour en haut");
document.body.appendChild(backToTop);

window.addEventListener("scroll", () => {
    backToTop.classList.toggle("visible", window.scrollY > 500);
}, { passive: true });

backToTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
});


/* =========================================================
   11. FERMER LA SIDEBAR EN CLIQUANT À L'EXTÉRIEUR
   ========================================================= */
document.addEventListener("click", (event) => {
    if (
        window.innerWidth <= 800 &&
        sidebar &&
        mobileMenu &&
        sidebar.classList.contains("open") &&
        !sidebar.contains(event.target) &&
        !mobileMenu.contains(event.target)
    ) {
        sidebar.classList.remove("open");
        mobileMenu.innerHTML = '<i class="fa-solid fa-bars"></i>';
    }
});


/* =========================================================
   12. ANNÉE AUTOMATIQUE DU FOOTER — NOM CORRIGÉ
   ========================================================= */
const copyright = document.querySelector(".copyright");
if (copyright) {
    const year = new Date().getFullYear();
    copyright.textContent =
        `© ${year} Mahamat Hassan Oumar. Tous droits réservés.`;
}


/* =========================================================
   13. MESSAGE DANS LA CONSOLE
   ========================================================= */
console.log(
    "%c Portfolio Mahamat Hassan Oumar ",
    "background:#8b3dff;color:#fff;padding:4px 8px;border-radius:4px;font-weight:bold;",
    "— JavaScript chargé avec succès ✅"
);