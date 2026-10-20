(function () {
  var nav = document.querySelector("[data-site-nav]");
  if (!nav) return;

  var root = document.body.getAttribute("data-root") || "./";
  var current = document.body.getAttribute("data-page") || "";
  var pagesPath = "pages/";

  fetch(root + "pages.json", { cache: "no-store" })
    .then(function (response) {
      if (!response.ok) throw new Error("pages.json: " + response.status);
      return response.json();
    })
    .then(function (pages) {
      if (!Array.isArray(pages)) return;

      pages.forEach(function (page, index) {
        var link = document.createElement("a");
        link.className = "side-link";
        link.href = root + (page.slug ? pagesPath + page.slug + "/" : "");
        if (page.slug === current) {
          link.className += " current";
          link.setAttribute("aria-current", "page");
        }

        var num = document.createElement("span");
        num.className = "side-num";
        num.textContent = ("0" + (index + 1)).slice(-2);

        var title = document.createElement("span");
        title.className = "side-title";
        title.textContent = page.title;

        var meta = document.createElement("span");
        meta.className = "side-meta";
        meta.textContent = page.meta || "";

        link.appendChild(num);
        link.appendChild(title);
        link.appendChild(meta);
        nav.appendChild(link);
      });
    })
    .catch(function () {
      /* The page content still works; only the sidebar is unavailable. */
    });
})();
