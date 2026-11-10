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

      // The homepage has an older hand-curated archive. Insert newly published
      // articles from pages.json without duplicating its existing entries.
      var pageList = document.querySelector(".pages-list");
      if (pageList) {
        var totalArticles = pages.filter(function (entry) { return Boolean(entry.slug); }).length;
        var freshRows = [];
        pages.forEach(function (page, index) {
          if (!page.slug || !/^[a-z0-9][a-z0-9-]*$/.test(page.slug)) return;
          var href = root + pagesPath + page.slug + "/";
          var present = Array.prototype.some.call(pageList.querySelectorAll("a.page-row"), function (row) {
            return row.getAttribute("href") === href;
          });
          if (present) return;
          var row = document.createElement("a");
          row.className = "page-row";
          row.href = href;
          var num = document.createElement("span");
          num.className = "page-num";
          num.textContent = ("0" + (totalArticles - index + 1)).slice(-2);
          var details = document.createElement("span");
          var title = document.createElement("span");
          title.className = "page-title";
          title.textContent = page.title;
          var kind = document.createElement("span");
          kind.className = "page-kind";
          kind.textContent = page.meta || "Research";
          details.appendChild(title);
          details.appendChild(kind);
          var summary = document.createElement("span");
          summary.className = "page-desc";
          summary.textContent = page.summary || "Source-linked research, technical evidence and a plain-English explanation.";
          var arrow = document.createElement("span");
          arrow.className = "page-arrow";
          arrow.setAttribute("aria-hidden", "true");
          arrow.textContent = "→";
          row.appendChild(num);
          row.appendChild(details);
          row.appendChild(summary);
          row.appendChild(arrow);
          freshRows.push(row);
        });
        // pages.json is ordered newest first, after the home entry.
        for (var i = freshRows.length - 1; i >= 0; i--) {
          pageList.insertBefore(freshRows[i], pageList.firstElementChild);
        }
        var latest = pages.find(function (entry) { return Boolean(entry.slug); });
        var latestLink = document.querySelector(".hero-actions a.btn");
        if (latest && latestLink) latestLink.href = root + pagesPath + latest.slug + "/";
      }
    })
    .catch(function () {
      /* The page content still works; only the sidebar is unavailable. */
    });
})();
