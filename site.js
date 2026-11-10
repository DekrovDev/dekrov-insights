/* One catalog for the archive and sidebar. No build or publisher-specific API. */
(function () {
  "use strict";
  var root = document.body.getAttribute("data-root") || "./";
  var current = document.body.getAttribute("data-page") || "";
  function pagePath(page) {
    if (!page.slug) return root;
    // Older catalog entries still work while a publisher is being upgraded.
    if (typeof page.path === "string" && /^\/[a-z0-9]+(?:-[a-z0-9]+)*\/$/.test(page.path)) return page.path;
    return root + "pages/" + page.slug + "/";
  }
  function element(tag, className, value) {
    var node = document.createElement(tag);
    node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  }
  fetch(root + "pages.json", { cache: "no-store" })
    .then(function (response) {
      if (!response.ok) throw new Error("pages.json: " + response.status);
      return response.json();
    })
    .then(function (entries) {
      if (!Array.isArray(entries)) throw new Error("Invalid article catalog");
      var seen = new Set();
      var seenPaths = new Set();
      var pages = entries.filter(function (page) {
        if (!page || typeof page.slug !== "string" || typeof page.title !== "string" ||
            (page.slug !== "" && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(page.slug)) || seen.has(page.slug)) return false;
        var destination = pagePath(page);
        if (seenPaths.has(destination)) return false;
        seen.add(page.slug);
        seenPaths.add(destination);
        return true;
      });
      var nav = document.querySelector("[data-site-nav]");
      if (nav) {
        var links = document.createDocumentFragment();
        pages.forEach(function (page, index) {
          var link = element("a", "side-link");
          link.href = pagePath(page);
          if (page.slug === current) {
            link.classList.add("current");
            link.setAttribute("aria-current", "page");
          }
          link.append(element("span", "side-num", String(index + 1).padStart(2, "0")),
            element("span", "side-title", page.title), element("span", "side-meta", page.meta || ""));
          links.appendChild(link);
        });
        nav.replaceChildren(links);
      }
      var articles = pages.filter(function (page) { return page.slug; });
      var pageList = document.querySelector(".pages-list");
      if (pageList && articles.length) {
        // Preserve useful hand-authored fallback summaries; rebuild in catalog order.
        var summaries = new Map();
        pageList.querySelectorAll("a.page-row").forEach(function (row) {
          var desc = row.querySelector(".page-desc");
          if (desc) summaries.set(row.href, desc.textContent);
        });
        var rows = document.createDocumentFragment();
        articles.forEach(function (page, index) {
          var row = element("a", "page-row");
          row.href = pagePath(page);
          var details = document.createElement("span");
          details.append(element("span", "page-title", page.title), element("span", "page-kind", page.meta || "Research"));
          var arrow = element("span", "page-arrow", "→");
          arrow.setAttribute("aria-hidden", "true");
          row.append(element("span", "page-num", String(articles.length - index).padStart(2, "0")), details,
            element("span", "page-desc", page.summary || summaries.get(row.href) || "Source-linked research and analysis."), arrow);
          rows.appendChild(row);
        });
        pageList.replaceChildren(rows);
        var latestLink = document.querySelector(".hero-actions a.btn");
        if (latestLink) latestLink.href = pagePath(articles[0]);
      }
    })
    .catch(function () {
      var nav = document.querySelector("[data-site-nav]");
      if (nav) {
        var home = element("a", "side-link", "Home — article index");
        home.href = root;
        nav.replaceChildren(home);
      }
      // Server-rendered homepage rows and article content remain readable.
    });
})();
