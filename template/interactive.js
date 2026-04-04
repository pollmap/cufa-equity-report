/* ============================================================
   CUFA Equity Report v2 — Interactive Components
   Float TOC, progress bar, expand toggle, back to top
   ============================================================ */

(function () {
  "use strict";

  /* ----------------------------------------------------------
     1. Reading Progress Bar
     ---------------------------------------------------------- */
  function initProgressBar() {
    var bar = document.querySelector(".reading-progress");
    if (!bar) return;

    function update() {
      var scrollTop = window.scrollY || document.documentElement.scrollTop;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width = Math.min(pct, 100) + "%";
    }

    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  /* ----------------------------------------------------------
     2. Float TOC — IntersectionObserver active highlight
     ---------------------------------------------------------- */
  function initFloatToc() {
    var toc = document.querySelector(".float-toc");
    if (!toc) return;

    var links = Array.from(toc.querySelectorAll("a[href^='#']"));
    if (links.length === 0) return;

    var sectionIds = links.map(function (a) {
      return a.getAttribute("href").slice(1);
    });

    var targets = sectionIds
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);

    if (targets.length === 0) return;

    var current = null;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            current = entry.target.id;
          }
        });
        links.forEach(function (a) {
          var href = a.getAttribute("href").slice(1);
          if (href === current) {
            a.classList.add("active");
          } else {
            a.classList.remove("active");
          }
        });
      },
      {
        rootMargin: "-10% 0px -80% 0px",
        threshold: 0,
      }
    );

    targets.forEach(function (el) { observer.observe(el); });
  }

  /* ----------------------------------------------------------
     3. Expand Card Toggle (<details> 기반, CSS만으로 동작)
        JS는 접근성 보완 + 애니메이션 보조
     ---------------------------------------------------------- */
  function initExpandCards() {
    var cards = document.querySelectorAll(".expand-card");

    cards.forEach(function (card) {
      var summary = card.querySelector("summary");
      if (!summary) return;

      summary.setAttribute("role", "button");
      summary.setAttribute("aria-expanded", card.open ? "true" : "false");

      card.addEventListener("toggle", function () {
        summary.setAttribute("aria-expanded", card.open ? "true" : "false");
      });
    });
  }

  /* ----------------------------------------------------------
     4. Back to Top Button (scroll > 400)
     ---------------------------------------------------------- */
  function initBackToTop() {
    var btn = document.querySelector(".back-to-top");
    if (!btn) return;

    function toggle() {
      var scrollTop = window.scrollY || document.documentElement.scrollTop;
      if (scrollTop > 400) {
        btn.classList.add("visible");
      } else {
        btn.classList.remove("visible");
      }
    }

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", toggle, { passive: true });
    toggle();
  }

  /* ----------------------------------------------------------
     5. Smooth Scroll for Anchor Links
     ---------------------------------------------------------- */
  function initSmoothScroll() {
    document.addEventListener("click", function (e) {
      var link = e.target.closest("a[href^='#']");
      if (!link) return;

      var id = link.getAttribute("href").slice(1);
      if (!id) return;

      var target = document.getElementById(id);
      if (!target) return;

      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });

      // URL hash 업데이트 (히스토리 기록)
      if (history.pushState) {
        history.pushState(null, "", "#" + id);
      }
    });
  }

  /* ----------------------------------------------------------
     Boot
     ---------------------------------------------------------- */
  function init() {
    initProgressBar();
    initFloatToc();
    initExpandCards();
    initBackToTop();
    initSmoothScroll();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
