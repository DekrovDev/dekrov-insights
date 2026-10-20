(function () {
  var root = document.documentElement;
  var KEY = "dekrov-theme";
  var stored = null;

  try {
    stored = localStorage.getItem(KEY);
  } catch (e) {}

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    var dark = theme === "dark";
    var button = document.querySelector("[data-theme-toggle]");
    if (button) {
      button.setAttribute("aria-label", dark ? "Dark theme. Switch to light theme." : "Light theme. Switch to dark theme.");
      var label = button.querySelector("[data-theme-label]");
      if (label) label.textContent = dark ? "Dark" : "Light";
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", dark ? "#000000" : "#ffffff");
  }

  function systemTheme() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  apply(stored === "dark" || stored === "light" ? stored : systemTheme());

  document.addEventListener("DOMContentLoaded", function () {
    apply(root.getAttribute("data-theme") || systemTheme());
    var button = document.querySelector("[data-theme-toggle]");
    if (!button) return;
    button.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      stored = next;
      try {
        localStorage.setItem(KEY, next);
      } catch (e) {}
      apply(next);
    });
  });

  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var onChange = function (event) {
      if (stored !== "dark" && stored !== "light") {
        apply(event.matches ? "dark" : "light");
      }
    };
    if (mq.addEventListener) mq.addEventListener("change", onChange);
    else if (mq.addListener) mq.addListener(onChange);
  }
})();
