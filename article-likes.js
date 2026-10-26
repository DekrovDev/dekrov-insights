/* Dekrov Insights article likes — Abacus public REST endpoint.
   No framework, API key, external library, or cookies required.
   Counts are shared; the local marker prevents accidental repeat votes on one browser.
*/
(function () {
  "use strict";

  var SECTION_SELECTOR = ".article-engagement";
  var API_ROOT = "https://abacus.jasoncameron.dev/";
  var NAMESPACE = "dekrovdev.github.io";
  var STORE_PREFIX = "dekrov-insights-liked:";
  var timeoutMs = 9000;

  function readMarker(key) {
    try { return window.localStorage.getItem(STORE_PREFIX + key) === "1"; }
    catch (_) { return false; }
  }

  function saveMarker(key) {
    try { window.localStorage.setItem(STORE_PREFIX + key, "1"); }
    catch (_) { /* Storage may be disabled. API still records votes. */ }
  }

  async function apiCall(key, readOnly) {
    var controller = new AbortController();
    var timeout = setTimeout(function () { controller.abort(); }, timeoutMs);
    try {
      var url = API_ROOT + (readOnly ? "get/" : "hit/") + NAMESPACE + "/" + encodeURIComponent("insights-like-" + key);
      var response = await fetch(url, {
        method: "GET",
        mode: "cors",
        cache: "no-store",
        signal: controller.signal
      });
      // Abacus only creates a counter on the first hit; 404 means zero likes so far.
      if (readOnly && response.status === 404) return 0;
      if (!response.ok) throw new Error("Counter service returned HTTP " + response.status);
      var payload = await response.json();
      if (typeof payload.value !== "number" || !Number.isFinite(payload.value)) {
        throw new Error("Counter service returned no valid count");
      }
      return payload.value;
    } finally {
      clearTimeout(timeout);
    }
  }

  function init(section) {
    var button = section.querySelector("[data-like-button]");
    var count = section.querySelector("[data-like-count]");
    var label = section.querySelector("[data-like-status]");
    if (!button || !count || !label) return;
    var key = button.getAttribute("data-article-key");
    if (!key || !/^[a-z0-9-]+$/.test(key)) return;

    var voted = readMarker(key);
    var pending = false;
    var ready = false;

    function updateVoted() {
      button.classList.toggle("is-liked", voted);
      button.setAttribute("aria-pressed", voted ? "true" : "false");
      button.setAttribute("aria-label", voted ? "Already liked this article" : "Like this article");
    }
    function setStatus(message) { label.textContent = message; }
    function renderCount(value) { count.textContent = new Intl.NumberFormat("en").format(value); }
    function setAvailability(available) {
      ready = available;
      button.disabled = !available || voted;
      button.title = !available ? "Likes temporarily unavailable" : (voted ? "Thanks for your vote" : "Like this article");
    }

    updateVoted();
    setAvailability(false);
    setStatus("Loading likes…");

    apiCall(key, true).then(function (value) {
      renderCount(value);
      setAvailability(true);
      setStatus(voted ? "Thanks for your vote." : "");
    }).catch(function (error) {
      console.warn("[Dekrov Insights] Unable to load article likes:", error);
      setAvailability(false);
      setStatus("Likes temporarily unavailable.");
    });

    button.addEventListener("click", async function () {
      if (!ready || voted || pending) return;
      pending = true;
      button.disabled = true;
      setStatus("Saving like…");
      try {
        var value = await apiCall(key, false);
        voted = true;
        saveMarker(key);
        renderCount(value);
        updateVoted();
        setStatus("Thanks for your vote.");
      } catch (error) {
        console.warn("[Dekrov Insights] Unable to save article like:", error);
        setStatus("Couldn't save your like. Please try again.");
      } finally {
        pending = false;
        setAvailability(ready);
      }
    });
  }

  function start() {
    document.querySelectorAll(SECTION_SELECTOR).forEach(init);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
