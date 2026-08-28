/* ==========================================================================
   Reading aids for the research paper. Everything here is progressive
   enhancement: with JavaScript disabled the page still reads top to bottom.
   ========================================================================== */
(function () {
  "use strict";

  var doc = document;

  /* ------------------------------------------------------ reading progress */

  var progress = doc.getElementById("progress");
  var totop = doc.getElementById("totop");
  var ticking = false;

  function onScroll() {
    var top = window.pageYOffset || doc.documentElement.scrollTop;
    var height = doc.documentElement.scrollHeight - window.innerHeight;

    if (progress) {
      progress.style.width = (height > 0 ? (top / height) * 100 : 0) + "%";
    }
    if (totop) {
      totop.classList.toggle("is-shown", top > 700);
    }
    ticking = false;
  }

  window.addEventListener("scroll", function () {
    if (!ticking) {
      window.requestAnimationFrame(onScroll);
      ticking = true;
    }
  }, { passive: true });

  onScroll();

  if (totop) {
    totop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ------------------------------------------------- table-of-contents nav */

  var toc = doc.getElementById("toc");
  var navToggle = doc.getElementById("nav-toggle");
  var links = toc ? Array.prototype.slice.call(toc.querySelectorAll("a[href^='#']")) : [];

  if (navToggle && toc) {
    navToggle.addEventListener("click", function () {
      var open = toc.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    // On narrow screens the drawer should close once a destination is chosen.
    toc.addEventListener("click", function (event) {
      if (event.target.closest("a") && window.matchMedia("(max-width: 62rem)").matches) {
        toc.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ------------------------------------------------------------ scroll spy */

  var targets = links
    .map(function (link) {
      var el = doc.querySelector(link.getAttribute("href"));
      return el ? { link: link, el: el } : null;
    })
    .filter(Boolean);

  if (targets.length && "IntersectionObserver" in window) {
    var visible = Object.create(null);

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting;
      });

      var active = null;
      for (var i = 0; i < targets.length; i++) {
        if (visible[targets[i].el.id]) { active = targets[i]; break; }
      }

      // Nothing intersecting (a long section fills the viewport): keep the last
      // heading that has already scrolled past the top of the window.
      if (!active) {
        var top = window.pageYOffset || doc.documentElement.scrollTop;
        for (var j = 0; j < targets.length; j++) {
          if (targets[j].el.offsetTop <= top + 120) { active = targets[j]; }
        }
      }

      links.forEach(function (link) {
        link.classList.toggle("is-active", !!active && link === active.link);
      });
    }, { rootMargin: "-88px 0px -55% 0px", threshold: 0 });

    targets.forEach(function (target) { observer.observe(target.el); });
  }

  /* -------------------------------------------------------- figure zooming */

  var lightbox = doc.getElementById("lightbox");
  var lightboxImg = lightbox ? lightbox.querySelector("img") : null;

  function closeLightbox() {
    if (!lightbox) { return; }
    lightbox.classList.remove("is-open");
    if (lightboxImg) { lightboxImg.removeAttribute("src"); }
  }

  if (lightbox && lightboxImg) {
    Array.prototype.forEach.call(doc.querySelectorAll(".figure__frame img"), function (img) {
      img.parentNode.addEventListener("click", function () {
        lightboxImg.src = img.getAttribute("src");
        lightboxImg.alt = img.getAttribute("alt") || "";
        lightbox.classList.add("is-open");
      });
    });

    lightbox.addEventListener("click", closeLightbox);
    doc.addEventListener("keydown", function (event) {
      if (event.key === "Escape") { closeLightbox(); }
    });
  }
})();
