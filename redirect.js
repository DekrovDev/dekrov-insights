/* Legacy article URLs keep query parameters and section links. */
(function () {
  "use strict";
  var link = document.querySelector("[data-redirect-target]");
  if (!link) return;
  var href = link.getAttribute("href") || "";
  if (href.charAt(0) !== "/" || href.charAt(1) === "/") return;
  var target = new URL(href, window.location.href);
  if (target.origin !== window.location.origin || target.pathname === window.location.pathname) return;
  target.search = window.location.search;
  target.hash = window.location.hash;
  window.location.replace(target.href);
})();
