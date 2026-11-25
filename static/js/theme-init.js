/* Exécuté dans <head>, avant l'affichage : applique le thème choisi
   et évite l'écran de chargement si le visiteur l'a déjà vu. */
(function () {
  var d = document.documentElement;
  d.classList.add("js");
  try {
    var t = localStorage.getItem("theme");
    if (t === "light" || t === "dark") d.setAttribute("data-theme", t);
    if (sessionStorage.getItem("pf-intro") === "1") d.classList.add("no-preload");
  } catch (e) {}
})();
