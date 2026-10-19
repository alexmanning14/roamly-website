(function () {
  "use strict";
  var trip = window.ROAMLY_TRIP;
  var maps = [];
  var bigMap = null;

  function isDark() {
    var t = document.documentElement.getAttribute("data-theme");
    return t ? t === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function token() {
    // MapKit JS tokens are locked to one origin each.
    var o = location.origin, t = window.MAPKIT_TOKENS;
    if (o === "https://roamly.us") return t.apex;
    if (o === "https://www.roamly.us") return t.prod;
    return t.local;
  }

  // Tapping a pin opens its entry, like the app's tappedBlockId handshake.
  function showBlock(id) {
    var row = document.querySelector('.row[data-block="' + id + '"]');
    if (!row) return;
    row.scrollIntoView({ behavior: "smooth", block: "center" });
    row.classList.add("hot");
    setTimeout(function () { row.classList.remove("hot"); }, 1600);
  }

  // Which day the reader is on: the last day whose top has passed 42% of the viewport.
  var days = Array.prototype.slice.call(document.querySelectorAll(".day"));
  var shown = null;
  function sync() {
    var cur = null, line = window.innerHeight * 0.42;
    days.forEach(function (d) { if (d.getBoundingClientRect().top < line) cur = d; });
    var key = cur ? cur.getAttribute("data-day") : "overview";
    if (key === shown) return;
    shown = key;
    document.querySelectorAll(".dc").forEach(function (c) { c.classList.toggle("on", c.getAttribute("data-day") === key); });
    if (!bigMap) return;
    if (cur) bigMap.focus(+key); else bigMap.overview();
  }

  function init() {
    if (init.done || !window.mapkit) return;
    init.done = true;
    mapkit.init({ authorizationCallback: function (done) { done(token()); } });

    var side = document.querySelector(".side");
    if (side && getComputedStyle(side).display !== "none") {
      bigMap = new RoamlyTripMap.TripMap(document.getElementById("bigmap"), trip, { dark: isDark(), onSelectBlock: showBlock });
      maps.push(bigMap);
      bigMap.overview();
    }
    // Phones: a map at each day, created as it comes into view.
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting || e.target.__map) return;
        var m = new RoamlyTripMap.TripMap(e.target, trip, { dark: isDark(), onSelectBlock: showBlock, padding: { top: 44, right: 28, bottom: 28, left: 28 } });
        e.target.__map = m; maps.push(m);
        m.focus(+e.target.getAttribute("data-day"), false);
        io.unobserve(e.target);
      });
    }, { rootMargin: "400px 0px" });
    document.querySelectorAll(".daymap").forEach(function (el) { if (getComputedStyle(el).display !== "none") io.observe(el); });

    // Reading an entry lifts its pin (applyHighlight).
    document.querySelectorAll(".row[data-pinned]").forEach(function (row) {
      var id = row.getAttribute("data-block");
      row.addEventListener("mouseenter", function () { maps.forEach(function (m) { m.highlight(id); }); });
      row.addEventListener("mouseleave", function () { maps.forEach(function (m) { m.highlight(null); }); });
    });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
      maps.forEach(function (m) { m.setDark(isDark()); });
    });
    shown = null; sync();
  }

  var raf = 0;
  window.addEventListener("scroll", function () {
    if (!raf) raf = requestAnimationFrame(function () { raf = 0; sync(); });
  }, { passive: true });
  sync();

  // QR handoff only on computers, the same rule as roamly.us.
  var isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  if (!isIOS && window.matchMedia("(min-width: 769px)").matches) {
    document.querySelectorAll(".handoff").forEach(function (el) { el.hidden = false; });

    // Header "Get the app": on a computer, show the QR instead of opening the App Store.
    var get = document.querySelector(".site .get"), pop = document.getElementById("get-pop");
    if (get && pop) {
      var open = function (on) {
        if (on) { pop.hidden = false; requestAnimationFrame(function () { pop.classList.add("on"); }); }
        else { pop.classList.remove("on"); setTimeout(function () { if (!pop.classList.contains("on")) pop.hidden = true; }, 180); }
        get.setAttribute("aria-expanded", on ? "true" : "false");
      };
      get.addEventListener("click", function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey) return; // let modified clicks open the App Store
        e.preventDefault();
        open(pop.hidden);
      });
      document.addEventListener("click", function (e) {
        if (!pop.hidden && !pop.contains(e.target) && e.target !== get) open(false);
      });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !pop.hidden) { open(false); get.focus(); } });
    }
  }

  window.__mk = init;
  if (window.mapkit && window.mapkit.init) init();
})();
