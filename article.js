/* Progressive article tools. The article and sources remain usable without JS. */
(function () {
  "use strict";
  var article = document.querySelector(".article-body");
  if (!article) return;
  var main = document.querySelector("main");
  if (main && !main.id) main.id = "main";
  if (!document.querySelector(".skip-link") && main) {
    var skip = document.createElement("a");
    skip.href = "#" + main.id;
    skip.className = "skip-link";
    skip.textContent = "Skip to article";
    document.body.prepend(skip);
  }

  var headings = Array.from(article.querySelectorAll("h2")).filter(function (heading) {
    return !heading.closest(".article-engagement, [data-article-toc], dialog");
  });
  var ids = new Set(Array.from(document.querySelectorAll("[id]")).map(function (node) { return node.id; }));
  headings.forEach(function (heading) {
    if (heading.id) return;
    var base = heading.textContent.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "section";
    var id = base;
    var n = 2;
    while (ids.has(id)) id = base + "-" + n++;
    heading.id = id;
    ids.add(id);
  });
  var simple = article.querySelector('[data-explained-simply], #explained-simply');
  var simpleHeading = headings.find(function (h) { return /explained simply|in plain english/i.test(h.textContent); });
  if (!simple && simpleHeading) simple = simpleHeading;
  var title = article.querySelector("h1");
  if (title && headings.length && !article.querySelector("[data-article-toc]")) {
    var tools = document.createElement("nav");
    tools.className = "article-tools";
    tools.setAttribute("data-article-toc", "");
    tools.setAttribute("aria-label", "In this article");
    if (simple && simple.id) {
      var jump = document.createElement("a");
      jump.className = "btn simple-jump";
      jump.href = "#" + simple.id;
      jump.textContent = "New to this? Explained simply ↓";
      tools.appendChild(jump);
    }
    var details = document.createElement("details");
    details.className = "article-toc";
    var summary = document.createElement("summary");
    summary.textContent = "In this article · " + headings.length + " sections";
    var list = document.createElement("ol");
    headings.forEach(function (heading) {
      var li = document.createElement("li");
      var link = document.createElement("a");
      link.href = "#" + heading.id;
      link.textContent = heading.textContent;
      li.appendChild(link);
      list.appendChild(li);
    });
    details.append(summary, list);
    tools.appendChild(details);
    var intro = article.querySelector(".intro");
    (intro || title).after(tools);
  }

  // Portfolio-style section shortcuts, kept visible while reading.
  if (headings.length && title) {
    var topId = title.id || "article-title";
    while (!title.id && ids.has(topId)) topId += "-top";
    title.id = topId;
    var quick = document.createElement("nav");
    quick.className = "article-quicknav";
    quick.setAttribute("aria-label", "Quick section navigation");
    var shortcuts = document.createElement("div");
    shortcuts.className = "quicknav-links";
    var shortLinks = headings.map(function (heading) {
      var link = document.createElement("a");
      link.href = "#" + heading.id;
      var label = heading.textContent.replace(/^0?[0-9]+\s*\/\s*/, "");
      var concise = label.replace(/^Technical Deep Dive$/i, "Deep Dive").replace(/^Visual Evidence:.*$/i, "Visual Evidence").replace(/^Evidence & Sources$/i, "Sources");
      link.textContent = concise.length > 30 ? concise.slice(0, 27) + "…" : concise;
      link.setAttribute("aria-label", label);
      link.title = label;
      shortcuts.appendChild(link);
      return link;
    });
    var controls = document.createElement("div");
    controls.className = "quicknav-controls";
    var previous = document.createElement("button");
    previous.type = "button";
    previous.textContent = "↑";
    previous.setAttribute("aria-label", "Previous section");
    var next = document.createElement("button");
    next.type = "button";
    next.textContent = "↓";
    next.setAttribute("aria-label", "Next section");
    var top = document.createElement("a");
    top.href = "#" + title.id;
    top.textContent = "Top ↑";
    controls.append(previous, next, top);
    quick.append(shortcuts, controls);
    var tools = article.querySelector("[data-article-toc]");
    (tools || title).after(quick);
    var active = -1;
    var queued = false;
    function updateSection() {
      queued = false;
      var threshold = quick.getBoundingClientRect().bottom + 56;
      var index = -1;
      headings.forEach(function (heading, n) {
        var marker = heading === simpleHeading && simple ? simple : heading;
        if (marker.getBoundingClientRect().top <= threshold) index = n;
      });
      if (index !== active) {
        shortLinks.forEach(function (link, n) {
          if (n === index) link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
        active = index;
        if (index >= 0) {
          var bounds = shortLinks[index].getBoundingClientRect();
          var visible = shortcuts.getBoundingClientRect();
          if (bounds.left < visible.left || bounds.right > visible.right) {
            shortcuts.scrollLeft += bounds.left - visible.left - 8;
          }
        }
      }
      previous.disabled = active < 0;
      next.disabled = active >= headings.length - 1;
    }
    function move(delta) {
      updateSection();
      // From the first section, Previous returns to the article heading.
      var target = active + delta < 0 ? title : headings[Math.min(headings.length - 1, active + delta)];
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
      target.scrollIntoView({ block: "start" });
      history.replaceState(null, "", "#" + target.id);
    }
    previous.addEventListener("click", function () { move(-1); });
    next.addEventListener("click", function () { move(1); });
    window.addEventListener("scroll", function () {
      if (!queued) { queued = true; window.requestAnimationFrame(updateSection); }
    }, { passive: true });
    window.addEventListener("resize", updateSection);
    updateSection();
  }

  // Add a return link for every citation, including repeated references.
  article.querySelectorAll('.source-list > li[id]').forEach(function (source) {
    var refs = Array.from(article.querySelectorAll('a.citation')).filter(function (ref) {
      return ref.getAttribute("href") === "#" + source.id;
    });
    if (!refs.length) return;
    var returns = document.createElement("span");
    returns.className = "source-returns";
    refs.forEach(function (ref, index) {
      if (!ref.id) {
        var id = "cite-" + source.id + "-" + (index + 1);
        while (document.getElementById(id)) id += "-ref";
        ref.id = id;
      }
      var back = document.createElement("a");
      back.href = "#" + ref.id;
      back.textContent = "↩" + (refs.length > 1 ? " " + (index + 1) : "");
      back.setAttribute("aria-label", "Return to citation " + (index + 1) + " for " + source.id);
      returns.appendChild(back);
    });
    source.appendChild(returns);
  });

  // Links work normally without dialog support or JavaScript.
  var dialog;
  var opener;
  var largeImage;
  var caption;
  function makeDialog() {
    dialog = document.createElement("dialog");
    if (typeof dialog.showModal !== "function") return false;
    dialog.className = "image-dialog";
    dialog.setAttribute("aria-label", "Enlarged article image");
    var close = document.createElement("button");
    close.type = "button";
    close.className = "btn image-close";
    close.textContent = "Close image ×";
    close.addEventListener("click", function () { dialog.close(); });
    largeImage = document.createElement("img");
    caption = document.createElement("p");
    caption.className = "image-dialog-caption";
    caption.id = "article-image-caption";
    dialog.setAttribute("aria-describedby", caption.id);
    dialog.append(close, largeImage, caption);
    dialog.addEventListener("click", function (event) { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener("close", function () {
      document.documentElement.classList.remove("image-open");
      largeImage.removeAttribute("src");
      if (opener) opener.focus();
    });
    document.body.appendChild(dialog);
    return true;
  }
  article.querySelectorAll("figure.article-figure").forEach(function (figure) {
    var img = figure.querySelector("img");
    if (!img) return;
    function unavailable() {
      figure.classList.add("image-unavailable");
      var link = img.closest("a[data-lightbox]");
      if (link) {
        link.removeAttribute("data-lightbox");
        link.hidden = true;
      }
      img.hidden = true;
      if (!figure.querySelector(".image-fallback")) {
        var message = document.createElement("p");
        message.className = "image-fallback";
        message.setAttribute("role", "status");
        message.textContent = "Image unavailable. " + img.alt + " See the original source below.";
        figure.prepend(message);
      }
    }
    img.addEventListener("error", unavailable);
    if (img.complete && !img.naturalWidth) unavailable();
    var link = figure.querySelector("a[data-lightbox]");
    if (!link) return;
    link.addEventListener("click", function (event) {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
      if (!dialog && !makeDialog()) return;
      event.preventDefault();
      opener = link;
      largeImage.src = link.href;
      largeImage.alt = img.alt;
      var text = figure.querySelector("figcaption");
      caption.textContent = text ? text.textContent : img.alt;
      dialog.showModal();
      document.documentElement.classList.add("image-open");
    });
  });
})();
